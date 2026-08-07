#!/usr/bin/env python3
"""Explicitly confirmed, bounded single-axis MPD20 commissioning jog."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import sys
import time
from typing import Sequence

from ..backends.mpd20 import MPD20Driver, MPD20MotorCalibration, MPD20Telemetry
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


def wait_for_jog_completion(
    driver: MPD20Driver,
    motor_id: int,
    before: MPD20Telemetry,
    timeout: float,
    *,
    poll_interval: float = 0.05,
    stable_samples: int = 2,
) -> MPD20Telemetry:
    """Wait for delayed motion onset and then for a stationary position.

    MPD20 may still report ``moving=false`` in the first feedback frame after a
    target write.  Treating that first frame as completion immediately cancels
    the jog when the commissioning tool performs its final hold.
    """
    if timeout <= 0 or poll_interval < 0 or stable_samples < 1:
        raise DriverValidationError("invalid commissioning observation settings")
    deadline = time.monotonic() + timeout
    after = before
    last_position = before.raw_position
    position_changed = False
    motion_seen = False
    stationary_samples = 0
    while time.monotonic() < deadline:
        time.sleep(poll_interval)
        after = driver.read_telemetry(motor_id)
        if after.raw_position != before.raw_position:
            position_changed = True
        if after.moving:
            motion_seen = True
            stationary_samples = 0
        elif position_changed:
            if motion_seen:
                return after
            if after.raw_position == last_position:
                stationary_samples += 1
            else:
                stationary_samples = 0
            if stationary_samples >= stable_samples:
                return after
        last_position = after.raw_position
    if after.moving:
        raise RuntimeError("motor remained moving until commissioning timeout")
    if not position_changed:
        raise RuntimeError("no motor position change observed before commissioning timeout")
    raise RuntimeError("motor position did not settle before commissioning timeout")


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
        after = wait_for_jog_completion(driver, args.motor_id, before, args.timeout)
        return {
            "motor_id": args.motor_id,
            "commanded_raw_target": args.raw_target,
            "position_changed": after.raw_position != before.raw_position,
            "target_error_raw": after.raw_position - args.raw_target,
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
