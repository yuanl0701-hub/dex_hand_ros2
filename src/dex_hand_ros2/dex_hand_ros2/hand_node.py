#!/usr/bin/env python3
"""ROS 2 adapter for the hardware-independent hand controller."""

from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
import json
import sys
from typing import Callable

import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import Int32MultiArray, String
from std_srvs.srv import SetBool, Trigger

from dex_hand_interfaces.msg import GestureCmd, MotorState, PIDconfig
from dex_hand_interfaces.srv import AddGesture, RunGesturePid

from .driver import DriverConfig
from .factory import create_driver
from .hand_driver import RoboticHand


class DexHandROS2Node(Node):
    """Non-blocking ROS facade preserving the original public interface names."""

    def __init__(self) -> None:
        super().__init__("dex_hand_node")
        self._declare_parameters()
        config = DriverConfig(
            tuple(int(value) for value in self.get_parameter("motor_ids").value),
            float(self.get_parameter("position_min").value),
            float(self.get_parameter("position_max").value),
        )
        status_frequency = float(self.get_parameter("status_pub_freq").value)
        if status_frequency <= 0:
            raise ValueError("status_pub_freq must be positive")

        self.driver = create_driver(
            str(self.get_parameter("driver_type").value),
            str(self.get_parameter("serial_port").value),
            int(self.get_parameter("baudrate").value),
            timeout=float(self.get_parameter("serial_timeout").value),
            retries=int(self.get_parameter("serial_retries").value),
            config=config,
        )
        if not self.driver.connect():
            raise RuntimeError("selected motor backend failed to connect")
        gesture_file = str(self.get_parameter("gesture_file").value).strip() or None
        self.hand = RoboticHand(
            self.driver,
            gesture_file,
            watchdog_timeout=float(self.get_parameter("command_watchdog_timeout").value),
            max_rate=float(self.get_parameter("max_command_rate").value),
        )
        for motor_id in config.motor_ids:
            self.hand.configure_pid(
                motor_id,
                float(self.get_parameter("pid_kp").value),
                float(self.get_parameter("pid_ki").value),
                float(self.get_parameter("pid_kd").value),
            )

        qos = QoSProfile(
            reliability=self._reliability_policy(),
            history=HistoryPolicy.KEEP_LAST,
            depth=int(self.get_parameter("qos_depth").value),
        )
        self.status_pub = self.create_publisher(String, "/dex_hand/status", qos)
        self.motor_state_pub = self.create_publisher(MotorState, "/dex_hand/motor_state", qos)
        self.create_subscription(
            GestureCmd, "/dex_hand/gesture_cmd", self.gesture_cmd_callback, qos
        )
        self.create_subscription(
            Int32MultiArray,
            "/dex_hand/motor_pos_cmd",
            self.motor_pos_callback,
            qos,
        )
        self.create_subscription(
            Int32MultiArray,
            "/dex_hand/motor_pos_pid_cmd",
            self.motor_pos_pid_callback,
            qos,
        )
        self.create_subscription(PIDconfig, "/dex_hand/pid_config", self.pid_config_callback, qos)
        self.create_service(Trigger, "/dex_hand/list_gestures", self.list_gestures_callback)
        self.create_service(Trigger, "/dex_hand/demo_gestures", self.demo_gestures_callback)
        self.create_service(AddGesture, "/dex_hand/add_gesture", self.add_gesture_callback)
        self.create_service(
            RunGesturePid,
            "/dex_hand/run_gesture_pid",
            self.run_gesture_pid_callback,
        )
        self.create_service(SetBool, "/dex_hand/emergency_stop", self.emergency_stop_callback)

        self._worker = ThreadPoolExecutor(max_workers=1, thread_name_prefix="dex-hand")
        self._command_future: Future[object] | None = None
        self._state_future: Future[object] | None = None
        self.create_timer(1.0 / status_frequency, self.publish_status)
        self.create_timer(
            min(
                0.25,
                float(self.get_parameter("command_watchdog_timeout").value) / 2.0,
            ),
            self._watchdog_callback,
        )
        self.get_logger().info(
            f"DEX hand ready with backend={self.get_parameter('driver_type').value}"
        )

    def _declare_parameters(self) -> None:
        defaults = {
            "driver_type": "fake",
            "serial_port": "/dev/ttyUSB0",
            "baudrate": 115200,
            "serial_timeout": 0.3,
            "serial_retries": 1,
            "motor_ids": [1, 2, 3, 4, 5, 6],
            "position_min": 0.0,
            "position_max": 100.0,
            "max_command_rate": 1000.0,
            "command_watchdog_timeout": 1.0,
            "status_pub_freq": 10.0,
            "pid_kp": 2.0,
            "pid_ki": 0.1,
            "pid_kd": 0.05,
            "gesture_file": "",
            "qos_reliability": "reliable",
            "qos_depth": 10,
        }
        for name, value in defaults.items():
            self.declare_parameter(name, value)

    def _reliability_policy(self) -> ReliabilityPolicy:
        value = str(self.get_parameter("qos_reliability").value).strip().lower()
        depth = int(self.get_parameter("qos_depth").value)
        if depth <= 0:
            raise ValueError("qos_depth must be positive")
        if value == "reliable":
            return ReliabilityPolicy.RELIABLE
        if value == "best_effort":
            return ReliabilityPolicy.BEST_EFFORT
        raise ValueError("qos_reliability must be reliable or best_effort")

    def _submit(self, label: str, operation: Callable[[], object]) -> bool:
        if self._command_future is not None and not self._command_future.done():
            self.get_logger().warning(f"command rejected while busy: {label}")
            return False
        self._command_future = self._worker.submit(operation)
        self._command_future.add_done_callback(lambda future: self._log_future(label, future))
        return True

    def _log_future(self, label: str, future: Future[object]) -> None:
        try:
            result = future.result()
            self.get_logger().info(f"{label}: {'success' if result is not False else 'failed'}")
        except Exception as exc:
            self.get_logger().error(f"{label} failed: {exc}")

    def gesture_cmd_callback(self, msg: GestureCmd) -> None:
        speed = float(msg.speed)
        if speed <= 0:
            self.get_logger().error("gesture speed must be positive")
            return
        self._submit(
            f"gesture {msg.gesture}",
            lambda: self.hand.run_gesture_smooth(msg.gesture, speed),
        )

    def motor_pos_callback(self, msg: Int32MultiArray) -> None:
        if len(msg.data) != 2:
            self.get_logger().error("motor command must be [motor_id, position]")
            return
        motor_id, position = (int(msg.data[0]), float(msg.data[1]))
        self._submit(
            f"motor {motor_id} position",
            lambda: self.hand.set_motor_position(motor_id, position),
        )

    def motor_pos_pid_callback(self, msg: Int32MultiArray) -> None:
        if len(msg.data) != 2:
            self.get_logger().error("PID command must be [motor_id, position]")
            return
        motor_id, target = (int(msg.data[0]), float(msg.data[1]))
        self._submit(
            f"motor {motor_id} PID",
            lambda: self.hand.set_motor_with_pid(motor_id, target),
        )

    def pid_config_callback(self, msg: PIDconfig) -> None:
        try:
            self.hand.configure_pid(msg.motor_id, msg.kp, msg.ki, msg.kd)
        except Exception as exc:
            self.get_logger().error(f"PID configuration rejected: {exc}")

    def list_gestures_callback(self, request: object, response: Trigger.Response):
        del request
        response.success = True
        response.message = ", ".join(self.hand.get_gesture_list())
        return response

    def demo_gestures_callback(self, request: object, response: Trigger.Response):
        del request

        def run_demo() -> bool:
            return all(self.hand.run_gesture_smooth(name) for name in self.hand.get_gesture_list())

        response.success = self._submit("gesture demo", run_demo)
        response.message = "demo accepted" if response.success else "controller busy"
        return response

    def add_gesture_callback(self, request: AddGesture.Request, response: AddGesture.Response):
        try:
            if len(request.positions) != len(self.driver.config.motor_ids):
                raise ValueError("positions must match configured motor count")
            positions = dict(zip(self.driver.config.motor_ids, request.positions))
            self.hand.add_gesture(
                request.name,
                positions,
                request.description,
                request.duration,
            )
            response.success = True
            response.message = f"gesture added: {request.name}"
        except Exception as exc:
            response.success = False
            response.message = str(exc)
        return response

    def run_gesture_pid_callback(
        self, request: RunGesturePid.Request, response: RunGesturePid.Response
    ):
        response.success = self._submit(
            f"PID gesture {request.gesture_name}",
            lambda: self.hand.run_gesture_with_pid(request.gesture_name),
        )
        response.message = "command accepted" if response.success else "controller busy"
        return response

    def emergency_stop_callback(self, request: SetBool.Request, response: SetBool.Response):
        if request.data:
            self.hand.emergency_stop()
            response.success = True
            response.message = "emergency stop latched"
        else:
            response.success = self.hand.recover()
            response.message = "controller recovered" if response.success else "recovery rejected"
        return response

    def publish_status(self) -> None:
        status = self.hand.safety.status
        message = String()
        message.data = json.dumps(
            {
                "connected": self.driver.is_connected(),
                "safety_state": status.state.value,
                "reason": status.reason,
                "gesture_count": len(self.hand.get_gesture_list()),
                "qos_reliability": str(
                    self.get_parameter("qos_reliability").value
                ),
                "qos_depth": int(self.get_parameter("qos_depth").value),
            },
            sort_keys=True,
        )
        self.status_pub.publish(message)
        command_idle = self._command_future is None or self._command_future.done()
        state_idle = self._state_future is None or self._state_future.done()
        if command_idle and state_idle:
            self._state_future = self._worker.submit(self._read_and_publish_states)
            self._state_future.add_done_callback(self._log_state_future)

    def _log_state_future(self, future: Future[object]) -> None:
        try:
            future.result()
        except Exception as exc:
            self.get_logger().error(f"state poll failed: {exc}")

    def _read_and_publish_states(self) -> bool:
        for motor_id in self.driver.config.motor_ids:
            position = self.driver.get_position(motor_id)
            state = MotorState()
            state.motor_id = motor_id
            state.position = -1 if position is None else int(round(position))
            state.velocity = 0.0
            state.connected = self.driver.is_connected()
            self.motor_state_pub.publish(state)
        return True

    def _watchdog_callback(self) -> None:
        if not self.hand.safety.check_watchdog():
            self.get_logger().warning(self.hand.safety.status.reason)

    def destroy_node(self) -> None:
        if hasattr(self, "hand"):
            self.hand.safety.shutdown()
        if hasattr(self, "_worker"):
            self._worker.shutdown(wait=True, cancel_futures=True)
        if hasattr(self, "driver"):
            self.driver.disconnect()
        super().destroy_node()


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node: DexHandROS2Node | None = None
    try:
        node = DexHandROS2Node()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as exc:
        print(f"dex_hand_node failed: {exc}", file=sys.stderr)
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
