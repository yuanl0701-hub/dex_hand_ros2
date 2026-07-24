#!/usr/bin/env python3
"""Sample CPU, memory and thread usage for a Linux process."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import os
from pathlib import Path
import time


def _read_process(pid: int) -> tuple[int, int, int]:
    stat = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").split()
    status_lines = Path(f"/proc/{pid}/status").read_text(encoding="utf-8").splitlines()
    ticks = int(stat[13]) + int(stat[14])
    rss_kib = 0
    threads = 0
    for line in status_lines:
        if line.startswith("VmRSS:"):
            rss_kib = int(line.split()[1])
        elif line.startswith("Threads:"):
            threads = int(line.split()[1])
    return ticks, rss_kib, threads


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pid", type=int, required=True)
    parser.add_argument("--duration", type=float, required=True)
    parser.add_argument("--interval", type=float, default=0.5)
    parser.add_argument("--condition", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.duration <= 0 or args.interval <= 0:
        raise SystemExit("duration and interval must be positive")
    if not Path(f"/proc/{args.pid}").exists():
        raise SystemExit(f"process {args.pid} does not exist")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    clock_ticks = os.sysconf(os.sysconf_names["SC_CLK_TCK"])
    started = time.monotonic()
    previous_time = started
    previous_ticks, _, _ = _read_process(args.pid)
    rows: list[dict[str, object]] = []
    while time.monotonic() - started < args.duration:
        time.sleep(args.interval)
        now = time.monotonic()
        try:
            ticks, rss_kib, threads = _read_process(args.pid)
        except FileNotFoundError:
            break
        elapsed = now - previous_time
        cpu_percent = (
            (ticks - previous_ticks) / clock_ticks / elapsed * 100.0
            if elapsed > 0
            else 0.0
        )
        rows.append(
            {
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "condition": args.condition,
                "elapsed_s": now - started,
                "cpu_percent_of_one_core": cpu_percent,
                "rss_kib": rss_kib,
                "threads": threads,
            }
        )
        previous_time = now
        previous_ticks = ticks

    with args.output.open("w", encoding="utf-8", newline="") as stream:
        fields = [
            "created_at_utc",
            "condition",
            "elapsed_s",
            "cpu_percent_of_one_core",
            "rss_kib",
            "threads",
        ]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
