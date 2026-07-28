#!/usr/bin/env python3
"""Local browser control panel for the dexterous-hand ROS 2 interfaces."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import math
from pathlib import Path
from queue import Empty, SimpleQueue
from threading import Lock, Thread
import time
from typing import Any
import webbrowser

from ament_index_python.packages import get_package_share_directory
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import Int32MultiArray, String
from std_srvs.srv import SetBool, Trigger

from dex_hand_interfaces.msg import GestureCmd, MotorState, PIDconfig
from dex_hand_interfaces.srv import AddGesture, RunGesturePid, SetSimFault


GESTURES = (
    "open",
    "fist",
    "vgesture",
    "pinch_two",
    "pinch_three",
    "pinch_side",
    "point",
    "thumbs_up",
    "gesture_666",
)
FAULT_TYPES = (
    "motor_stuck",
    "motor_disconnect",
    "position_bias",
    "reduced_velocity",
    "limit_hit",
    "over_temperature",
    "stale_feedback",
    "command_drop",
)


class SharedState:
    def __init__(self) -> None:
        self._lock = Lock()
        self._status: dict[str, Any] = {
            "connected": False,
            "safety_state": "waiting",
            "reason": "waiting for /dex_hand/status",
        }
        self._motors: dict[str, dict[str, Any]] = {}
        self._last_action = "Web control node started"
        self._last_error = ""
        self._updated_at = time.time()

    def update_status(self, status: dict[str, Any]) -> None:
        with self._lock:
            self._status = status
            self._updated_at = time.time()

    def update_motor(self, message: MotorState) -> None:
        with self._lock:
            self._motors[str(message.motor_id)] = {
                "position": int(message.position),
                "velocity": float(message.velocity),
                "connected": bool(message.connected),
            }
            self._updated_at = time.time()

    def action(self, text: str) -> None:
        with self._lock:
            self._last_action = text
            self._last_error = ""
            self._updated_at = time.time()

    def error(self, text: str) -> None:
        with self._lock:
            self._last_error = text
            self._updated_at = time.time()

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "status": dict(self._status),
                "motors": {
                    key: dict(value) for key, value in self._motors.items()
                },
                "last_action": self._last_action,
                "last_error": self._last_error,
                "updated_at": self._updated_at,
                "gestures": list(GESTURES),
                "fault_types": list(FAULT_TYPES),
            }


class HandWebControlNode(Node):
    """Translate validated browser requests into the existing ROS 2 API."""

    def __init__(self) -> None:
        super().__init__("dex_hand_web_ui")
        self.declare_parameter("web_host", "127.0.0.1")
        self.declare_parameter("web_port", 8765)
        self.declare_parameter("open_browser", True)
        self.shared = SharedState()
        self._commands: SimpleQueue[tuple[str, dict[str, Any]]] = SimpleQueue()

        self._gesture_pub = self.create_publisher(
            GestureCmd, "/dex_hand/gesture_cmd", 10
        )
        self._motor_pub = self.create_publisher(
            Int32MultiArray, "/dex_hand/motor_pos_cmd", 10
        )
        self._motor_pid_pub = self.create_publisher(
            Int32MultiArray, "/dex_hand/motor_pos_pid_cmd", 10
        )
        self._pid_pub = self.create_publisher(
            PIDconfig, "/dex_hand/pid_config", 10
        )
        self.create_subscription(
            String, "/dex_hand/status", self._status_callback, 10
        )
        self.create_subscription(
            MotorState, "/dex_hand/motor_state", self._motor_state_callback, 10
        )

        self._service_clients = {
            "demo": self.create_client(Trigger, "/dex_hand/demo_gestures"),
            "reset": self.create_client(Trigger, "/dex_hand/sim/reset"),
            "clear_faults": self.create_client(
                Trigger, "/dex_hand/sim/clear_faults"
            ),
            "emergency_stop": self.create_client(
                SetBool, "/dex_hand/emergency_stop"
            ),
            "add_gesture": self.create_client(
                AddGesture, "/dex_hand/add_gesture"
            ),
            "run_gesture_pid": self.create_client(
                RunGesturePid, "/dex_hand/run_gesture_pid"
            ),
            "set_fault": self.create_client(
                SetSimFault, "/dex_hand/sim/set_fault"
            ),
        }
        self.create_timer(0.02, self._drain_commands)

    @property
    def web_host(self) -> str:
        return str(self.get_parameter("web_host").value)

    @property
    def web_port(self) -> int:
        return int(self.get_parameter("web_port").value)

    @property
    def should_open_browser(self) -> bool:
        return bool(self.get_parameter("open_browser").value)

    def enqueue(self, action: str, payload: dict[str, Any]) -> None:
        if action not in {
            "gesture",
            "motor",
            "pid",
            "service",
            "add_gesture",
            "fault",
        }:
            raise ValueError(f"unknown action: {action}")
        if not isinstance(payload, dict):
            raise ValueError("request payload must be a JSON object")
        self._commands.put((action, payload))

    def _status_callback(self, message: String) -> None:
        try:
            payload = json.loads(message.data)
            if not isinstance(payload, dict):
                raise ValueError("status payload is not an object")
            self.shared.update_status(payload)
        except Exception as exc:
            self.shared.error(f"Invalid status message: {exc}")

    def _motor_state_callback(self, message: MotorState) -> None:
        self.shared.update_motor(message)

    @staticmethod
    def _finite(value: Any, label: str) -> float:
        number = float(value)
        if not math.isfinite(number):
            raise ValueError(f"{label} must be finite")
        return number

    @staticmethod
    def _motor_id(value: Any) -> int:
        motor_id = int(value)
        if motor_id not in range(1, 7):
            raise ValueError("motor_id must be between 1 and 6")
        return motor_id

    @classmethod
    def _position(cls, value: Any) -> int:
        position = int(round(cls._finite(value, "position")))
        if position not in range(0, 101):
            raise ValueError("position must be between 0 and 100")
        return position

    def _drain_commands(self) -> None:
        for _ in range(32):
            try:
                action, payload = self._commands.get_nowait()
            except Empty:
                return
            try:
                getattr(self, f"_handle_{action}")(payload)
            except Exception as exc:
                self.get_logger().error(f"web command {action} rejected: {exc}")
                self.shared.error(f"{action}: {exc}")

    def _handle_gesture(self, payload: dict[str, Any]) -> None:
        name = str(payload.get("gesture", "")).strip()
        speed = self._finite(payload.get("speed", 1.0), "speed")
        if not name:
            raise ValueError("gesture must not be empty")
        if speed <= 0:
            raise ValueError("speed must be positive")
        message = GestureCmd()
        message.gesture = name
        message.speed = speed
        self._gesture_pub.publish(message)
        self.shared.action(f"Gesture sent: {name} (speed={speed:g})")

    def _handle_motor(self, payload: dict[str, Any]) -> None:
        motor_id = self._motor_id(payload.get("motor_id"))
        position = self._position(payload.get("position"))
        use_pid = bool(payload.get("use_pid", False))
        message = Int32MultiArray()
        message.data = [motor_id, position]
        (self._motor_pid_pub if use_pid else self._motor_pub).publish(message)
        mode = "PID" if use_pid else "position"
        self.shared.action(f"Motor {motor_id}: {position} ({mode})")

    def _handle_pid(self, payload: dict[str, Any]) -> None:
        motor_id = self._motor_id(payload.get("motor_id"))
        message = PIDconfig()
        message.motor_id = motor_id
        message.kp = self._finite(payload.get("kp"), "kp")
        message.ki = self._finite(payload.get("ki"), "ki")
        message.kd = self._finite(payload.get("kd"), "kd")
        self._pid_pub.publish(message)
        self.shared.action(
            f"PID motor {motor_id}: {message.kp:g}, {message.ki:g}, {message.kd:g}"
        )

    def _handle_service(self, payload: dict[str, Any]) -> None:
        name = str(payload.get("name", "")).strip()
        if name in {"demo", "reset", "clear_faults"}:
            self._call_service(name, Trigger.Request())
            return
        if name in {"emergency_stop", "recover"}:
            request = SetBool.Request()
            request.data = name == "emergency_stop"
            self._call_service("emergency_stop", request, label=name)
            return
        if name == "run_gesture_pid":
            request = RunGesturePid.Request()
            request.gesture_name = str(payload.get("gesture", "")).strip()
            if not request.gesture_name:
                raise ValueError("gesture must not be empty")
            self._call_service(name, request)
            return
        raise ValueError(f"unknown service action: {name}")

    def _handle_add_gesture(self, payload: dict[str, Any]) -> None:
        name = str(payload.get("name", "")).strip()
        positions = payload.get("positions")
        if not name:
            raise ValueError("gesture name must not be empty")
        if not isinstance(positions, list) or len(positions) != 6:
            raise ValueError("positions must contain six values")
        request = AddGesture.Request()
        request.name = name
        request.positions = [self._position(value) for value in positions]
        request.description = str(payload.get("description", "")).strip()
        request.duration = self._finite(payload.get("duration", 0.5), "duration")
        if request.duration <= 0:
            raise ValueError("duration must be positive")
        self._call_service("add_gesture", request, label=f"add {name}")

    def _handle_fault(self, payload: dict[str, Any]) -> None:
        request = SetSimFault.Request()
        request.motor_id = self._motor_id(payload.get("motor_id"))
        request.fault_type = str(payload.get("fault_type", "")).strip()
        if request.fault_type not in FAULT_TYPES:
            raise ValueError("unsupported fault type")
        request.value = self._finite(payload.get("value", 0.0), "value")
        request.enabled = bool(payload.get("enabled", True))
        self._call_service(
            "set_fault",
            request,
            label=f"fault {request.fault_type} motor {request.motor_id}",
        )

    def _call_service(self, name: str, request: Any, *, label: str = "") -> None:
        client = self._service_clients[name]
        display = label or name
        if not client.service_is_ready():
            self.shared.error(f"Service unavailable: {name}")
            return
        future = client.call_async(request)
        self.shared.action(f"Service requested: {display}")

        def completed(result_future) -> None:
            try:
                response = result_future.result()
                success = bool(getattr(response, "success", True))
                message = str(getattr(response, "message", "")).strip()
                text = f"{display}: {message or ('success' if success else 'failed')}"
                if success:
                    self.shared.action(text)
                else:
                    self.shared.error(text)
            except Exception as exc:
                self.shared.error(f"{display}: {exc}")

        future.add_done_callback(completed)


def make_handler(node: HandWebControlNode, html: bytes):
    class RequestHandler(BaseHTTPRequestHandler):
        server_version = "DexHandWebUI/1.0"

        def _send_json(self, status: int, payload: dict[str, Any]) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            if self.path in {"/", "/index.html"}:
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(html)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(html)
                return
            if self.path == "/api/state":
                self._send_json(200, node.shared.snapshot())
                return
            self._send_json(404, {"ok": False, "error": "not found"})

        def do_POST(self) -> None:
            if not self.path.startswith("/api/"):
                self._send_json(404, {"ok": False, "error": "not found"})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > 65536:
                    raise ValueError("invalid request size")
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
                action = self.path.removeprefix("/api/")
                node.enqueue(action, payload)
                self._send_json(202, {"ok": True, "queued": action})
            except Exception as exc:
                self._send_json(400, {"ok": False, "error": str(exc)})

        def log_message(self, format_string: str, *args: Any) -> None:
            node.get_logger().debug(format_string % args)

    return RequestHandler


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node: HandWebControlNode | None = None
    server: ThreadingHTTPServer | None = None
    server_thread: Thread | None = None
    try:
        node = HandWebControlNode()
        if not 1 <= node.web_port <= 65535:
            raise ValueError("web_port must be between 1 and 65535")
        html_path = (
            Path(get_package_share_directory("dex_hand_ros2"))
            / "web"
            / "index.html"
        )
        html = html_path.read_bytes()
        server = ThreadingHTTPServer(
            (node.web_host, node.web_port), make_handler(node, html)
        )
        server.daemon_threads = True
        server_thread = Thread(
            target=server.serve_forever,
            name="dex-hand-web-server",
            daemon=True,
        )
        server_thread.start()
        url = f"http://{node.web_host}:{node.web_port}"
        node.get_logger().info(f"DEX hand web control: {url}")
        if node.web_host not in {"127.0.0.1", "localhost", "::1"}:
            node.get_logger().warning(
                "Web UI is exposed beyond localhost and has no authentication"
            )
        if node.should_open_browser:
            webbrowser.open(url)
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    except Exception as exc:
        if node is not None:
            node.get_logger().error(f"web UI failed: {exc}")
        else:
            print(f"dex_hand_web_ui failed: {exc}")
    finally:
        if server is not None:
            server.shutdown()
            server.server_close()
        if server_thread is not None:
            server_thread.join(timeout=2.0)
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
