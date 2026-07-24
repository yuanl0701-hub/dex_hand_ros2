#!/usr/bin/env python3
"""Generate E05 trajectory and E06 PID algorithm evidence."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import subprocess

from dex_hand_ros2.pid import PIDConfig, PIDController
from dex_hand_ros2.trajectory import QuinticTrajectory


def _commit() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def run_trajectory(output: Path) -> None:
    raw_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []
    scenarios = [
        (0.0, 100.0, duration, sample_period)
        for duration in (0.25, 0.5, 1.0, 2.0)
        for sample_period in (0.01, 0.02, 0.05)
    ]
    scenarios.extend(
        [
            (100.0, 0.0, 1.0, 0.02),
            (25.0, 75.0, 1.0, 0.02),
            (50.0, 50.0, 1.0, 0.02),
        ]
    )
    for scenario_index, (start, end, duration, sample_period) in enumerate(scenarios):
        scenario = f"T{scenario_index:02d}"
        trajectory = QuinticTrajectory(start, end, duration)
        points = trajectory.sample(sample_period)
        jerk_integral = 0.0
        for left, right in zip(points, points[1:]):
            jerk_integral += (
                (left.jerk**2 + right.jerk**2)
                * 0.5
                * (right.time - left.time)
            )
        for point in points:
            raw_rows.append(
                {
                    "scenario": scenario,
                    "method": "quintic",
                    "start_normalized_percent": start,
                    "end_normalized_percent": end,
                    "duration_s": duration,
                    "sample_period_s": sample_period,
                    "time_s": point.time,
                    "position_normalized_percent": point.position,
                    "velocity_percent_per_s": point.velocity,
                    "acceleration_percent_per_s2": point.acceleration,
                    "jerk_percent_per_s3": point.jerk,
                }
            )
        first, last = points[0], points[-1]
        summary_rows.append(
            {
                "scenario": scenario,
                "start": start,
                "end": end,
                "duration_s": duration,
                "sample_period_s": sample_period,
                "start_position_residual": abs(first.position - start),
                "end_position_residual": abs(last.position - end),
                "start_velocity_residual": abs(first.velocity),
                "end_velocity_residual": abs(last.velocity),
                "start_acceleration_residual": abs(first.acceleration),
                "end_acceleration_residual": abs(last.acceleration),
                "peak_abs_velocity": max(abs(point.velocity) for point in points),
                "peak_abs_acceleration": max(
                    abs(point.acceleration) for point in points
                ),
                "peak_abs_jerk": max(abs(point.jerk) for point in points),
                "integrated_squared_jerk": jerk_integral,
                "finite": all(
                    math.isfinite(value)
                    for point in points
                    for value in (
                        point.position,
                        point.velocity,
                        point.acceleration,
                        point.jerk,
                    )
                ),
            }
        )
    _write_csv(
        output / "raw" / "trajectory_samples.csv",
        [
            "scenario",
            "method",
            "start_normalized_percent",
            "end_normalized_percent",
            "duration_s",
            "sample_period_s",
            "time_s",
            "position_normalized_percent",
            "velocity_percent_per_s",
            "acceleration_percent_per_s2",
            "jerk_percent_per_s3",
        ],
        raw_rows,
    )
    _write_csv(
        output / "trajectory_summary.csv",
        list(summary_rows[0]),
        summary_rows,
    )


def run_pid(output: Path) -> None:
    raw_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []
    configurations = {
        "P": PIDConfig(kp=2.0, ki=0.0, kd=0.0),
        "PI": PIDConfig(kp=2.0, ki=0.1, kd=0.0),
        "PID": PIDConfig(kp=2.0, ki=0.1, kd=0.05),
    }
    transitions = [(0.0, 100.0), (100.0, 0.0), (25.0, 75.0), (75.0, 25.0)]
    dt = 0.02
    tolerance = 2.0
    maximum_iterations = 200
    for config_name, config in configurations.items():
        for start, target in transitions:
            scenario = f"{config_name}_{int(start)}_{int(target)}"
            controller = PIDController(config)
            measurement = start
            converged = False
            saturation_count = 0
            peak_abs_effort = 0.0
            for iteration in range(maximum_iterations):
                error = target - measurement
                if abs(error) <= tolerance:
                    converged = True
                    break
                effort = controller.compute(target, measurement, dt)
                saturation_count += int(
                    math.isclose(effort, config.output_min)
                    or math.isclose(effort, config.output_max)
                )
                peak_abs_effort = max(peak_abs_effort, abs(effort))
                raw_rows.append(
                    {
                        "scenario": scenario,
                        "controller": config_name,
                        "iteration": iteration,
                        "time_s": iteration * dt,
                        "start_normalized_percent": start,
                        "target_normalized_percent": target,
                        "measurement_normalized_percent": measurement,
                        "error_normalized_percent": error,
                        "effort_normalized_percent_per_s": effort,
                        "kp": config.kp,
                        "ki": config.ki,
                        "kd": config.kd,
                    }
                )
                measurement = max(0.0, min(100.0, measurement + effort * dt))
            summary_rows.append(
                {
                    "scenario": scenario,
                    "controller": config_name,
                    "start": start,
                    "target": target,
                    "dt_s": dt,
                    "iterations": iteration,
                    "converged": converged,
                    "final_measurement": measurement,
                    "final_abs_error": abs(target - measurement),
                    "peak_abs_effort": peak_abs_effort,
                    "saturation_count": saturation_count,
                    "evidence_scope": "deterministic_algorithm_output",
                }
            )
    _write_csv(
        output / "raw" / "pid_samples.csv",
        [
            "scenario",
            "controller",
            "iteration",
            "time_s",
            "start_normalized_percent",
            "target_normalized_percent",
            "measurement_normalized_percent",
            "error_normalized_percent",
            "effort_normalized_percent_per_s",
            "kp",
            "ki",
            "kd",
        ],
        raw_rows,
    )
    _write_csv(output / "pid_summary.csv", list(summary_rows[0]), summary_rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    run_trajectory(args.output / "E05_trajectory")
    run_pid(args.output / "E06_pid")
    metadata = {
        "data_kind": "algorithm_output",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": _commit(),
        "units": "normalized_percent",
        "warning": (
            "These are deterministic algorithm outputs. They are not hardware "
            "measurements and do not include actuator dynamics."
        ),
    }
    (args.output / "algorithm_metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
