#!/usr/bin/env python3
"""Explicitly confirmed, bounded single-axis MPD20 commissioning jog."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import sys
import time
from typing import Sequence

from ..backends.mpd20 import MPD20Driver, MPD20MotorCalibration
from ..core.driver import DriverConfig, DriverValidationError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Jog one stationary MPD20 by a small raw-position delta"
    )
    parser.add_argument("--port", required=True)
    parser.add_argument("--id", type=int, required=True, dest="motor_id")
    parser.add_argument("--raw-target", type=int, required=True)
    parser.add_argument("--baudrate", type=int, default=115200)
    parser.add_argument("--max-speed", type=int, default=5)
    parser.add_argument("--max-delta", type=int, default=20)
    parser.add_argument("--timeout", type=float, default=3.0)
    parser.add_argument("--serial-timeout", type=float, default=0.3)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument(
        "--confirm-small-jog",
        action="store_true",
        help="required acknowledgement that the axis is unloaded and clear",
    )
    return parser


def _validate_request(target_raw: int, max_delta: int, confirmed: bool) -> None:
    if not confirmed:
        raise DriverValidationError("--confirm-small-jog is required")
    if not 1 <= max_delta <= 50:
        raise DriverValidationError("max_delta must be in [1, 50]")
    if not 0 <= target_raw <= 1023:
        raise DriverValidationError("raw_target must be in [0, 1023]")


def validate_jog(current_raw: int, target_raw: int, max_delta: int, confirmed: bool) -> None:
    _validate_request(target_raw, max_delta, confirmed)
    delta = abs(target_raw - current_raw)
    if delta == 0 or delta > max_delta:
        raise DriverValidationError(f"requested raw delta {delta} must be in [1, {max_delta}]")


def run_jog(args: argparse.Namespace) -> dict[str, object]:
    if args.timeout <= 0:
        raise DriverValidationError("timeout must be positive")
    _validate_request(args.raw_target, args.max_delta, args.confirm_small_jog)
    config = DriverConfig((args.motor_id,))
    calibration = MPD20MotorCalibration(0, 1023, 1, args.max_speed)
    driver = MPD20Driver(
        args.port,
        args.baudrate,
        timeout=args.serial_timeout,
        retries=args.retries,
        config=config,
        calibrations={args.motor_id: calibration},
        motion_enabled=True,
        verify_on_connect=True,
        hold_on_connect=True,
        require_stationary_on_connect=True,
    )
    connected = False
    try:
        driver.connect()
        connected = True
        before = driver.read_telemetry(args.motor_id)
        validate_jog(
            before.raw_position,
            args.raw_target,
            args.max_delta,
            args.confirm_small_jog,
        )
        driver.set_raw_position(args.motor_id, args.raw_target)
        deadline = time.monotonic() + args.timeout
        after = driver.read_telemetry(args.motor_id)
        while after.moving and time.monotonic() < deadline:
            time.sleep(0.05)
            after = driver.read_telemetry(args.motor_id)
        if after.moving:
            raise RuntimeError("motor remained moving until commissioning timeout")
        return {
            "motor_id": args.motor_id,
            "commanded_raw_target": args.raw_target,
            "before": asdict(before),
            "after": asdict(after),
        }
    finally:
        if connected:
            try:
                driver.hold_current_position()
            finally:
                driver.disconnect()


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        print(json.dumps(run_jog(args), indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"MPD20 commissioning jog failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
