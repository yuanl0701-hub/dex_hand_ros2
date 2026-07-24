#!/usr/bin/env python3
"""Collect machine-readable E00 environment evidence without external packages."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import subprocess


def _capture(command: list[str], timeout: float = 30.0) -> dict[str, object]:
    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return {
            "command": command,
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
        }
    return {
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def _first_line(record: dict[str, object]) -> str:
    text = str(record.get("stdout", "")).strip()
    return text.splitlines()[0] if text else "unavailable"


def _os_pretty_name() -> str:
    try:
        entries = {}
        for line in Path("/etc/os-release").read_text(encoding="utf-8").splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                entries[key] = value.strip('"')
        return entries.get("PRETTY_NAME", platform.platform())
    except OSError:
        return platform.platform()


def _cpu_model() -> str:
    try:
        for line in Path("/proc/cpuinfo").read_text(encoding="utf-8").splitlines():
            if line.lower().startswith("model name"):
                return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or "unavailable"


def _memory_gib() -> str:
    try:
        for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
            if line.startswith("MemTotal:"):
                kib = int(line.split()[1])
                return f"{kib / 1024 / 1024:.2f} GiB"
    except (OSError, ValueError):
        pass
    return "unavailable"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    commands = {
        "os_release": ["lsb_release", "-a"],
        "kernel": ["uname", "-a"],
        "cpu": ["lscpu"],
        "memory": ["free", "-h"],
        "gpu": ["nvidia-smi"],
        "gpu_summary": [
            "nvidia-smi",
            "--query-gpu=name,memory.total,driver_version",
            "--format=csv,noheader",
        ],
        "python": ["python3", "--version"],
        "ros2": ["ros2", "doctor", "--report"],
        "git_commit": ["git", "rev-parse", "HEAD"],
        "git_status": ["git", "status", "--short"],
    }
    records = {name: _capture(command) for name, command in commands.items()}
    metadata = {
        "data_kind": "environment_record",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "hostname": platform.node(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "ros_distro": os.environ.get("ROS_DISTRO", ""),
        "rmw_implementation": os.environ.get(
            "RMW_IMPLEMENTATION", "not_explicitly_set"
        ),
        "records": records,
    }
    (args.output / "environment.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    with (args.output / "environment_table.csv").open(
        "w", encoding="utf-8", newline=""
    ) as stream:
        writer = csv.writer(stream)
        writer.writerow(["component", "recorded_value", "evidence_command"])
        writer.writerow(["host", platform.node(), "platform.node"])
        writer.writerow(["operating system", _os_pretty_name(), "/etc/os-release"])
        writer.writerow(["kernel", platform.release(), "uname -a"])
        writer.writerow(["CPU", _cpu_model(), "/proc/cpuinfo"])
        writer.writerow(["logical CPUs", os.cpu_count(), "os.cpu_count"])
        writer.writerow(["system memory", _memory_gib(), "/proc/meminfo"])
        writer.writerow(
            [
                "GPU, memory and driver",
                _first_line(records["gpu_summary"]),
                "nvidia-smi --query-gpu",
            ]
        )
        writer.writerow(["ROS distribution", os.environ.get("ROS_DISTRO", ""), "ROS_DISTRO"])
        writer.writerow(
            [
                "RMW implementation",
                os.environ.get("RMW_IMPLEMENTATION", "not_explicitly_set"),
                "RMW_IMPLEMENTATION",
            ]
        )
        writer.writerow(["Python", _first_line(records["python"]), "python3 --version"])
        writer.writerow(
            ["Git commit", _first_line(records["git_commit"]), "git rev-parse HEAD"]
        )
        writer.writerow(
            [
                "Working tree",
                "clean"
                if not str(records["git_status"].get("stdout", "")).strip()
                else "modified",
                "git status --short",
            ]
        )

    with (args.output / "environment_commands.txt").open(
        "w", encoding="utf-8"
    ) as stream:
        for name, record in records.items():
            stream.write(f"===== {name} =====\n")
            stream.write(f"$ {' '.join(record['command'])}\n")
            stream.write(str(record.get("stdout", "")) + "\n")
            if record.get("stderr"):
                stream.write("[stderr]\n" + str(record["stderr"]) + "\n")
            stream.write(f"[returncode] {record.get('returncode')}\n\n")

    warnings = []
    if records["gpu_summary"].get("returncode") != 0:
        warnings.append(
            "nvidia-smi did not complete successfully; GPU/driver evidence is "
            "unavailable for this run. This does not invalidate CPU-only ROS 2 "
            "experiments, but it must be resolved before GPU/Isaac Sim claims."
        )
    if str(records["git_status"].get("stdout", "")).strip():
        warnings.append(
            "The Git working tree was modified when evidence was collected; "
            "preserve git_state and do not describe the run as a clean-revision run."
        )
    (args.output / "environment_warnings.txt").write_text(
        ("\n".join(f"- {warning}" for warning in warnings) if warnings else "None")
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
