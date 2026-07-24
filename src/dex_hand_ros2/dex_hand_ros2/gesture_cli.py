#!/usr/bin/env python3
"""Small interactive publisher for compatibility gesture commands."""

import rclpy
from rclpy.node import Node

from dex_hand_interfaces.msg import GestureCmd


class GestureCLI(Node):
    def __init__(self) -> None:
        super().__init__("gesture_cli")
        self.publisher = self.create_publisher(GestureCmd, "/dex_hand/gesture_cmd", 10)

    def send(self, name: str, speed: float = 1.0) -> None:
        message = GestureCmd()
        message.gesture = name
        message.speed = speed
        self.publisher.publish(message)


def main() -> None:
    rclpy.init()
    node = GestureCLI()
    try:
        while rclpy.ok():
            name = input("gesture (or quit)> ").strip()
            if name.lower() == "quit":
                break
            if name:
                node.send(name)
                rclpy.spin_once(node, timeout_sec=0.05)
    except (EOFError, KeyboardInterrupt):
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
