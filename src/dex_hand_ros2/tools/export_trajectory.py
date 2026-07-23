#!/usr/bin/env python3
"""Export theoretical quintic output; this does not produce experimental evidence."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess

from dex_hand_ros2.experiment import ExperimentMetadata, write_trajectory_csv
from dex_hand_ros2.trajectory import QuinticTrajectory


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--start", type=float, default=0.0)
    parser.add_argument("--end", type=float, default=100.0)
    parser.add_argument("--duration", type=float, default=1.0)
    parser.add_argument("--sample-period", type=float, default=0.01)
    args = parser.parse_args()
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    trajectory = QuinticTrajectory(args.start, args.end, args.duration)
    metadata = ExperimentMetadata.create(
        data_kind="algorithm_output",
        units="normalized_percent",
        git_commit=commit,
        configuration={
            "start": args.start,
            "end": args.end,
            "duration_s": args.duration,
            "sample_period_s": args.sample_period,
        },
    )
    data_path, metadata_path = write_trajectory_csv(
        args.output, trajectory.sample(args.sample_period), metadata
    )
    print(data_path)
    print(metadata_path)


if __name__ == "__main__":
    main()
