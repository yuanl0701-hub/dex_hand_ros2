#!/usr/bin/env python3
"""Read-only MPD20 bus verification for commissioning and deployment."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import sys
from typing import Sequence

from ..backends.mpd20 import MPD20Driver, build_mpd20_calibrations
from ..core.driver import DriverConfig


def _int_list(value: str) -> list[int]:
    try:
        values = [int(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected comma-separated integers") from exc
    if not values:
        raise argparse.ArgumentTypeError("list must not be empty")
    return values


def _expanded(values: Sequence[int], count: int, label: str) -> list[int]:
    if len(values) == 1:
        return [int(values[0])] * count
    if len(values) != count:
        raise ValueError(f"{label} must contain one value or {count} values")
    return [int(value) for value in values]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=("Read MPD20 function-04 telemetry without writing any motor register")
    )
    parser.add_argument("--port", required=True, help="serial device, e.g. /dev/ttyUSB0")
    parser.add_argument("--baudrate", type=int, default=115200)
    parser.add_argument("--ids", type=_int_list, default=_int_list("1,2,3,4,5,6"))
    parser.add_argument("--raw-mins", type=_int_list, default=_int_list("120"))
    parser.add_argument("--raw-maxs", type=_int_list, default=_int_list("850"))
    parser.add_argument("--directions", type=_int_list, default=_int_list("1"))
    parser.add_argument("--max-speeds", type=_int_list, default=_int_list("10"))
    parser.add_argument("--timeout", type=float, default=0.3)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument(
        "--allow-moving",
        action="store_true",
        help="return success even when an actuator reports moving",
    )
    parser.add_argument(
        "--allow-outside-calibration",
        action="store_true",
        help="return success when feedback is outside the supplied raw limits",
    )
    return parser


def run_preflight(args: argparse.Namespace) -> dict[str, object]:
    motor_ids = tuple(int(value) for value in args.ids)
    count = len(motor_ids)
    config = DriverConfig(motor_ids)
    calibrations = build_mpd20_calibrations(
        motor_ids,
        _expanded(args.raw_mins, count, "raw-mins"),
        _expanded(args.raw_maxs, count, "raw-maxs"),
        _expanded(args.directions, count, "directions"),
        _expanded(args.max_speeds, count, "max-speeds"),
    )
    driver = MPD20Driver(
        args.port,
        args.baudrate,
        timeout=args.timeout,
        retries=args.retries,
        config=config,
        calibrations=calibrations,
        motion_enabled=False,
        verify_on_connect=False,
        hold_on_connect=False,
    )
    motors: list[dict[str, object]] = []
    try:
        driver.connect()
        for motor_id in motor_ids:
            telemetry = driver.read_telemetry(motor_id)
            item = asdict(telemetry)
            item["motor_id"] = motor_id
            try:
                item["normalized_position"] = round(
                    driver.raw_to_position(motor_id, telemetry.raw_position), 3
                )
                item["within_calibration"] = True
            except Exception as exc:
                item["normalized_position"] = None
                item["within_calibration"] = False
                item["calibration_error"] = str(exc)
            motors.append(item)
    finally:
        driver.disconnect()
    return {
        "port": args.port,
        "baudrate": args.baudrate,
        "read_only": True,
        "all_stationary": not any(bool(item["moving"]) for item in motors),
        "all_within_calibration": all(bool(item["within_calibration"]) for item in motors),
        "motors": motors,
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run_preflight(args)
        print(json.dumps(result, indent=2, sort_keys=True))
        if not result["all_stationary"] and not args.allow_moving:
            print(
                "preflight failed: at least one actuator is moving; wait or remove power",
                file=sys.stderr,
            )
            return 3
        if not result["all_within_calibration"] and not args.allow_outside_calibration:
            print(
                "preflight failed: feedback is outside the supplied calibration",
                file=sys.stderr,
            )
            return 4
        return 0
    except Exception as exc:
        print(f"MPD20 preflight failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
