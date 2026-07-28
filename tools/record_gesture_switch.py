#!/usr/bin/env python3
"""Record a deterministic ROS 2 named-gesture switching sequence to CSV."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import time

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

from dex_hand_interfaces.msg import GestureCmd


class GestureSwitchRecorder(Node):
    """Publish three named gestures and retain every received joint sample."""

    def __init__(self, duration: float = 10.0) -> None:
        super().__init__("gesture_switch_recorder")
        self.duration = duration
        self.start = time.monotonic()
        self.current_command = "initial"
        self.rows: list[list[object]] = []
        self.events: list[list[object]] = []
        self.commands = [
            (1.0, "fist"),
            (4.0, "vgesture"),
            (7.0, "open"),
        ]
        self.next_command = 0
        self.publisher = self.create_publisher(
            GestureCmd, "/dex_hand/gesture_cmd", 10
        )
        self.create_subscription(JointState, "/joint_states", self.on_joint_state, 10)
        self.create_timer(0.01, self.on_timer)

    @property
    def elapsed(self) -> float:
        return time.monotonic() - self.start

    @property
    def finished(self) -> bool:
        return self.elapsed >= self.duration

    def on_timer(self) -> None:
        while self.next_command < len(self.commands):
            scheduled_time, gesture = self.commands[self.next_command]
            if self.elapsed < scheduled_time:
                break
            message = GestureCmd()
            message.gesture = gesture
            message.speed = 1.0
            self.publisher.publish(message)
            self.current_command = gesture
            self.events.append(
                [self.elapsed, gesture, float(message.speed)]
            )
            self.get_logger().info(f"published gesture={gesture}")
            self.next_command += 1

    def on_joint_state(self, message: JointState) -> None:
        positions = dict(zip(message.name, message.position))
        for joint_name in sorted(positions):
            self.rows.append(
                [
                    self.elapsed,
                    self.current_command,
                    joint_name,
                    float(positions[joint_name]),
                ]
            )


def write_csv(output_dir: Path, recorder: GestureSwitchRecorder) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "gesture_switch_trace.csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        writer = csv.writer(stream)
        writer.writerow(
            ["elapsed_time_s", "active_gesture_command", "joint_name", "position_rad"]
        )
        writer.writerows(recorder.rows)
    with (output_dir / "gesture_switch_events.csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        writer = csv.writer(stream)
        writer.writerow(["elapsed_time_s", "gesture", "speed_factor"])
        writer.writerows(recorder.events)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--duration", type=float, default=10.0)
    args = parser.parse_args()
    if args.duration <= 7.5:
        raise ValueError("duration must exceed the final command time")

    rclpy.init()
    recorder = GestureSwitchRecorder(args.duration)
    try:
        while rclpy.ok() and not recorder.finished:
            rclpy.spin_once(recorder, timeout_sec=0.05)
    finally:
        write_csv(args.output_dir, recorder)
        recorder.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
