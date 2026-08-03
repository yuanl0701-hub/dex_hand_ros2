#!/usr/bin/env python3
"""Dedicated hardware-configuration ROS 2 node."""

from __future__ import annotations

import sys

import rclpy
from rclpy.node import Node

from dex_hand_interfaces.srv import ChangeBaud, ChangeId

from .backends.factory import ConnectionSettings, MPD20Settings, create_driver
from .core.driver import DriverConfig


def _parse_change(command: str) -> tuple[int, int]:
    parts = command.strip().split(">")
    if len(parts) != 2:
        raise ValueError("command must contain exactly one '>'")
    return int(parts[0]), int(parts[1])


class DexHandConfigNode(Node):
    def __init__(self) -> None:
        super().__init__("dex_hand_config_node")
        self.declare_parameter("driver_type", "mpd20")
        self.declare_parameter("serial_port", "/dev/ttyUSB0")
        self.declare_parameter("baudrate", 115200)
        self.declare_parameter("serial_timeout", 0.3)
        self.declare_parameter("serial_retries", 1)
        self.declare_parameter("motor_ids", [1])
        config = DriverConfig(tuple(int(value) for value in self.get_parameter("motor_ids").value))
        backend = str(self.get_parameter("driver_type").value).strip().lower()
        settings = (
            MPD20Settings(
                motion_enabled=False,
                verify_on_connect=False,
                hold_on_connect=False,
                require_stationary_on_connect=False,
            )
            if backend == "mpd20"
            else None
        )
        self.driver = create_driver(
            backend,
            config=config,
            connection=ConnectionSettings(
                port=str(self.get_parameter("serial_port").value),
                baudrate=int(self.get_parameter("baudrate").value),
                timeout=float(self.get_parameter("serial_timeout").value),
                retries=int(self.get_parameter("serial_retries").value),
            ),
            settings=settings,
        )
        if not self.driver.connect():
            raise RuntimeError("configuration backend failed to connect")
        self.create_service(ChangeId, "/dex_hand/change_id", self.change_id_callback)
        self.create_service(ChangeBaud, "/dex_hand/change_baud", self.change_baud_callback)

    def change_id_callback(self, request: ChangeId.Request, response: ChangeId.Response):
        try:
            old_id, new_id = _parse_change(request.command)
            response.success = self.driver.change_id(old_id, new_id)
            response.message = "ID change acknowledged" if response.success else "ID change failed"
        except Exception as exc:
            response.success = False
            response.message = str(exc)
        return response

    def change_baud_callback(self, request: ChangeBaud.Request, response: ChangeBaud.Response):
        try:
            target_id, baudrate = _parse_change(request.command)
            response.success = self.driver.change_baudrate(target_id, baudrate)
            response.message = (
                "baud change acknowledged" if response.success else "baud change failed"
            )
        except Exception as exc:
            response.success = False
            response.message = str(exc)
        return response

    def destroy_node(self) -> None:
        if hasattr(self, "driver"):
            self.driver.disconnect()
        super().destroy_node()


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node: DexHandConfigNode | None = None
    try:
        node = DexHandConfigNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as exc:
        print(f"dex_hand_config_node failed: {exc}", file=sys.stderr)
        raise
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
