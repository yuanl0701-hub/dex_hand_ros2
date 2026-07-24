"""ROS 2 experiment client for the deterministic virtual hand backend.

The outputs produced here are ROS 2 virtual-backend measurements.  They are
not physical dexterous-hand measurements.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import statistics
import time
from typing import Callable

import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import Int32MultiArray
from std_srvs.srv import SetBool, Trigger

from dex_hand_interfaces.msg import GestureCmd, MotorState


class ExperimentClient(Node):
    """Synchronous experiment facade around asynchronous ROS 2 interfaces."""

    def __init__(self, reliability: str = "reliable") -> None:
        super().__init__("dex_hand_experiment_client")
        self.motor_events: list[tuple[int, MotorState]] = []
        self.status_events: list[tuple[int, dict[str, object]]] = []
        policy = (
            ReliabilityPolicy.RELIABLE
            if reliability == "reliable"
            else ReliabilityPolicy.BEST_EFFORT
        )
        qos = QoSProfile(
            reliability=policy,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )
        self.motor_pub = self.create_publisher(
            Int32MultiArray, "/dex_hand/motor_pos_cmd", qos
        )
        self.gesture_pub = self.create_publisher(
            GestureCmd, "/dex_hand/gesture_cmd", qos
        )
        self.create_subscription(
            MotorState, "/dex_hand/motor_state", self._motor_callback, qos
        )
        from std_msgs.msg import String

        self.create_subscription(
            String, "/dex_hand/status", self._status_callback, qos
        )
        self.estop_client = self.create_client(SetBool, "/dex_hand/emergency_stop")
        self.gesture_list_client = self.create_client(
            Trigger, "/dex_hand/list_gestures"
        )

    def _motor_callback(self, message: MotorState) -> None:
        self.motor_events.append((time.monotonic_ns(), message))

    def _status_callback(self, message: object) -> None:
        try:
            payload = json.loads(str(message.data))
        except (AttributeError, json.JSONDecodeError):
            payload = {"decode_error": True}
        self.status_events.append((time.monotonic_ns(), payload))

    def spin_until(self, predicate: Callable[[], bool], timeout_s: float) -> bool:
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            rclpy.spin_once(self, timeout_sec=min(0.05, deadline - time.monotonic()))
            if predicate():
                return True
        return predicate()

    def wait_for_interfaces(self, timeout_s: float = 10.0) -> bool:
        clients_ready = self.estop_client.wait_for_service(
            timeout_sec=timeout_s
        ) and self.gesture_list_client.wait_for_service(timeout_sec=timeout_s)
        messages_ready = self.spin_until(
            lambda: bool(self.motor_events) and bool(self.status_events), timeout_s
        )
        return clients_ready and messages_ready

    def call_estop(self, value: bool, timeout_s: float = 3.0):
        request = SetBool.Request()
        request.data = value
        future = self.estop_client.call_async(request)
        if not self.spin_until(future.done, timeout_s):
            return None
        return future.result()

    def recover(self) -> bool:
        if (
            self.status_events
            and self.status_events[-1][1].get("safety_state") == "ready"
        ):
            # Reset command history as well as the safety state so each
            # experiment begins from an independent timing/rate-limit state.
            stopped = self.call_estop(True)
            if stopped is None or not stopped.success:
                return False
        response = self.call_estop(False)
        if response is None:
            return False
        return self.spin_until(
            lambda: bool(self.status_events)
            and self.status_events[-1][1].get("safety_state") == "ready",
            1.0,
        )

    def latest_position(self, motor_id: int) -> int | None:
        for _, message in reversed(self.motor_events):
            if message.motor_id == motor_id:
                return int(message.position)
        return None

    def publish_position(self, motor_id: int, position: int) -> int:
        message = Int32MultiArray()
        message.data = [motor_id, position]
        sent_ns = time.monotonic_ns()
        self.motor_pub.publish(message)
        return sent_ns

    def wait_for_position(
        self, motor_id: int, position: int, sent_ns: int, timeout_s: float = 1.0
    ) -> tuple[int, MotorState] | None:
        match: tuple[int, MotorState] | None = None

        def matched() -> bool:
            nonlocal match
            for event_ns, message in reversed(self.motor_events):
                if event_ns < sent_ns:
                    break
                if message.motor_id == motor_id and int(message.position) == position:
                    match = (event_ns, message)
                    return True
            return False

        self.spin_until(matched, timeout_s)
        return match


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run_functional(client: ExperimentClient, output: Path) -> bool:
    rows: list[dict[str, object]] = []

    def record(
        test_id: str,
        expected: str,
        observed: str,
        passed: bool,
        elapsed_ms: float,
        notes: str = "",
    ) -> None:
        rows.append(
            {
                "test_id": test_id,
                "expected": expected,
                "observed": observed,
                "passed": passed,
                "elapsed_ms": f"{elapsed_ms:.6f}",
                "notes": notes,
            }
        )

    started = time.monotonic_ns()
    future = client.gesture_list_client.call_async(Trigger.Request())
    completed = client.spin_until(future.done, 3.0)
    response = future.result() if completed else None
    names = "" if response is None else response.message
    record(
        "E02-F01",
        "open, fist and vgesture are listed",
        names or "service timeout",
        response is not None
        and response.success
        and {"open", "fist", "vgesture"}.issubset(set(names.split(", "))),
        (time.monotonic_ns() - started) / 1e6,
    )

    client.recover()
    started = client.publish_position(1, 25)
    match = client.wait_for_position(1, 25, started)
    record(
        "E02-F02",
        "motor 1 reaches normalized position 25",
        "position=25" if match else f"position={client.latest_position(1)}",
        match is not None,
        (time.monotonic_ns() - started) / 1e6,
    )

    invalid_cases = [
        ("E02-F03", [1], "wrong-dimension command is rejected"),
        ("E02-F04", [99, 50], "unknown motor ID is rejected"),
        ("E02-F05", [1, 101], "out-of-range position is rejected"),
    ]
    for test_id, data, expected in invalid_cases:
        client.recover()
        baseline = client.latest_position(1)
        message = Int32MultiArray()
        message.data = data
        started = time.monotonic_ns()
        client.motor_pub.publish(message)
        client.spin_until(lambda: False, 0.25)
        observed = client.latest_position(1)
        record(
            test_id,
            expected,
            f"motor_1_before={baseline}; motor_1_after={observed}",
            baseline is not None and observed == baseline,
            (time.monotonic_ns() - started) / 1e6,
            "Rejection is inferred from unchanged virtual state; inspect node log.",
        )

    client.recover()
    started = time.monotonic_ns()
    stop_response = client.call_estop(True)
    stopped = client.spin_until(
        lambda: bool(client.status_events)
        and client.status_events[-1][1].get("safety_state") == "stopped",
        1.0,
    )
    record(
        "E02-F06",
        "software emergency stop latches stopped state",
        "stopped" if stopped else "status timeout",
        stop_response is not None and stop_response.success and stopped,
        (time.monotonic_ns() - started) / 1e6,
        "Software state only; this is not a physical torque-off result.",
    )

    before = client.latest_position(1)
    started = client.publish_position(1, 30)
    client.spin_until(lambda: False, 0.25)
    after = client.latest_position(1)
    record(
        "E02-F07",
        "position command is rejected while stopped",
        f"motor_1_before={before}; motor_1_after={after}",
        before is not None and before == after,
        (time.monotonic_ns() - started) / 1e6,
    )

    started = time.monotonic_ns()
    recovered = client.recover()
    record(
        "E02-F08",
        "operator recovery returns controller to ready",
        "ready" if recovered else "recovery timeout",
        recovered,
        (time.monotonic_ns() - started) / 1e6,
    )

    client.recover()
    gesture = GestureCmd()
    gesture.gesture = "open"
    gesture.speed = 1.0
    started = time.monotonic_ns()
    client.gesture_pub.publish(gesture)
    gesture_match = client.wait_for_position(1, 100, started, timeout_s=2.0)
    record(
        "E02-F09",
        "open gesture reaches normalized position 100",
        "position=100"
        if gesture_match
        else f"position={client.latest_position(1)}",
        gesture_match is not None,
        (time.monotonic_ns() - started) / 1e6,
    )

    _write_csv(
        output / "functional_results.csv",
        ["test_id", "expected", "observed", "passed", "elapsed_ms", "notes"],
        rows,
    )
    summary = {
        "data_kind": "ros2_virtual_backend_measurement",
        "tests": len(rows),
        "passed": sum(bool(row["passed"]) for row in rows),
        "failed": sum(not bool(row["passed"]) for row in rows),
    }
    (output / "functional_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary["failed"] == 0


def run_timing(
    client: ExperimentClient, output: Path, samples: int, condition: str
) -> bool:
    rows: list[dict[str, object]] = []
    client.recover()
    experiment_start_ns = time.monotonic_ns()

    for index in range(samples):
        target = 10 + index % 80
        sent_ns = client.publish_position(1, target)
        match = client.wait_for_position(1, target, sent_ns, timeout_s=1.0)
        received_ns = "" if match is None else match[0]
        latency_ms = "" if match is None else (match[0] - sent_ns) / 1e6
        rows.append(
            {
                "condition": condition,
                "sample": index,
                "target_normalized_percent": target,
                "send_monotonic_ns": sent_ns,
                "receive_monotonic_ns": received_ns,
                "latency_ms": latency_ms,
                "matched": match is not None,
            }
        )

    state_times = [
        event_ns
        for event_ns, message in client.motor_events
        if event_ns >= experiment_start_ns and message.motor_id == 1
    ]
    interarrival_rows = [
        {
            "condition": condition,
            "sample": index,
            "interarrival_ms": (right - left) / 1e6,
        }
        for index, (left, right) in enumerate(zip(state_times, state_times[1:]), start=1)
    ]

    output.mkdir(parents=True, exist_ok=True)
    _write_csv(
        output / "command_latency.csv",
        [
            "condition",
            "sample",
            "target_normalized_percent",
            "send_monotonic_ns",
            "receive_monotonic_ns",
            "latency_ms",
            "matched",
        ],
        rows,
    )
    _write_csv(
        output / "state_interarrival.csv",
        ["condition", "sample", "interarrival_ms"],
        interarrival_rows,
    )
    values = [float(row["latency_ms"]) for row in rows if row["latency_ms"] != ""]
    summary = {
        "data_kind": "ros2_virtual_backend_measurement",
        "condition": condition,
        "requested_samples": samples,
        "matched_samples": len(values),
        "loss_count": samples - len(values),
        "mean_latency_ms": statistics.fmean(values) if values else None,
        "median_latency_ms": statistics.median(values) if values else None,
        "min_latency_ms": min(values) if values else None,
        "max_latency_ms": max(values) if values else None,
    }
    (output / "timing_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return len(values) == samples


def run_safety(client: ExperimentClient, output: Path, repetitions: int) -> bool:
    rows: list[dict[str, object]] = []
    for index in range(repetitions):
        client.recover()
        sent_ns = client.publish_position(1, 20 + index % 20)
        stopped = client.spin_until(
            lambda: bool(client.status_events)
            and client.status_events[-1][0] >= sent_ns
            and client.status_events[-1][1].get("safety_state") == "stopped"
            and "watchdog" in str(client.status_events[-1][1].get("reason", "")),
            2.0,
        )
        stopped_ns = client.status_events[-1][0] if stopped else None
        rows.append(
            {
                "test": "watchdog_state_transition",
                "repetition": index,
                "start_monotonic_ns": sent_ns,
                "end_monotonic_ns": stopped_ns or "",
                "latency_ms": ""
                if stopped_ns is None
                else (stopped_ns - sent_ns) / 1e6,
                "success": stopped,
                "scope": "software_state_only",
            }
        )

    for index in range(repetitions):
        client.recover()
        started_ns = time.monotonic_ns()
        response = client.call_estop(True)
        stopped = client.spin_until(
            lambda: bool(client.status_events)
            and client.status_events[-1][0] >= started_ns
            and client.status_events[-1][1].get("safety_state") == "stopped",
            1.0,
        )
        ended_ns = client.status_events[-1][0] if stopped else None
        rows.append(
            {
                "test": "emergency_stop_service_to_status",
                "repetition": index,
                "start_monotonic_ns": started_ns,
                "end_monotonic_ns": ended_ns or "",
                "latency_ms": ""
                if ended_ns is None
                else (ended_ns - started_ns) / 1e6,
                "success": response is not None and response.success and stopped,
                "scope": "software_state_only",
            }
        )
        client.recover()

    _write_csv(
        output / "safety_timing.csv",
        [
            "test",
            "repetition",
            "start_monotonic_ns",
            "end_monotonic_ns",
            "latency_ms",
            "success",
            "scope",
        ],
        rows,
    )
    succeeded = sum(bool(row["success"]) for row in rows)
    summary = {
        "data_kind": "ros2_virtual_backend_measurement",
        "scope": "software_state_only",
        "measurements": len(rows),
        "successful": succeeded,
        "failed": len(rows) - succeeded,
    }
    (output / "safety_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return succeeded == len(rows)


def run_load(
    client: ExperimentClient, output: Path, duration_s: float, rate_hz: float
) -> bool:
    client.recover()
    period = 1.0 / rate_hz
    deadline = time.monotonic() + duration_s
    published = 0
    next_send = time.monotonic()
    while time.monotonic() < deadline:
        now = time.monotonic()
        if now >= next_send:
            client.publish_position(1, 10 + published % 80)
            published += 1
            next_send += period
        rclpy.spin_once(client, timeout_sec=min(0.01, max(0.0, next_send - now)))
    output.mkdir(parents=True, exist_ok=True)
    summary = {
        "data_kind": "ros2_virtual_backend_measurement",
        "duration_s": duration_s,
        "requested_rate_hz": rate_hz,
        "published_commands": published,
        "achieved_publish_rate_hz": published / duration_s,
    }
    (output / "load_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return True


def main(args: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--qos-reliability",
        choices=("reliable", "best_effort"),
        default="reliable",
    )
    subparsers = parser.add_subparsers(dest="mode", required=True)
    functional = subparsers.add_parser("functional")
    functional.add_argument("--output", type=Path, required=True)
    timing = subparsers.add_parser("timing")
    timing.add_argument("--output", type=Path, required=True)
    timing.add_argument("--samples", type=int, default=600)
    timing.add_argument("--condition", default="idle")
    safety = subparsers.add_parser("safety")
    safety.add_argument("--output", type=Path, required=True)
    safety.add_argument("--repetitions", type=int, default=20)
    load = subparsers.add_parser("load")
    load.add_argument("--output", type=Path, required=True)
    load.add_argument("--duration", type=float, default=60.0)
    load.add_argument("--rate", type=float, default=20.0)
    parsed = parser.parse_args(args)
    if getattr(parsed, "samples", 1) <= 0:
        parser.error("--samples must be positive")
    if getattr(parsed, "repetitions", 1) <= 0:
        parser.error("--repetitions must be positive")
    if getattr(parsed, "duration", 1.0) <= 0:
        parser.error("--duration must be positive")
    if getattr(parsed, "rate", 1.0) <= 0:
        parser.error("--rate must be positive")

    rclpy.init()
    client = ExperimentClient(parsed.qos_reliability)
    succeeded = False
    try:
        if not client.wait_for_interfaces():
            raise RuntimeError("DEX hand ROS interfaces did not become ready")
        if parsed.mode == "functional":
            succeeded = run_functional(client, parsed.output)
        elif parsed.mode == "timing":
            succeeded = run_timing(
                client, parsed.output, parsed.samples, parsed.condition
            )
        elif parsed.mode == "safety":
            succeeded = run_safety(client, parsed.output, parsed.repetitions)
        else:
            succeeded = run_load(
                client, parsed.output, parsed.duration, parsed.rate
            )
    finally:
        client.destroy_node()
        rclpy.shutdown()
    raise SystemExit(0 if succeeded else 1)


if __name__ == "__main__":
    main()
