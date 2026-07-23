"""Reproducible CSV export helpers for implemented algorithms."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Iterable

from .trajectory import TrajectoryPoint


@dataclass(frozen=True)
class ExperimentMetadata:
    """Metadata stored beside raw data; ``data_kind`` prevents evidence confusion."""

    data_kind: str
    units: str
    git_commit: str
    configuration: dict[str, object]
    created_at_utc: str

    @classmethod
    def create(
        cls,
        *,
        data_kind: str,
        units: str,
        git_commit: str,
        configuration: dict[str, object],
    ) -> ExperimentMetadata:
        if data_kind not in {"algorithm_output", "mock_fixture", "hardware_measurement"}:
            raise ValueError("unsupported data_kind")
        if not units or not git_commit:
            raise ValueError("units and git_commit are required")
        return cls(
            data_kind=data_kind,
            units=units,
            git_commit=git_commit,
            configuration=configuration,
            created_at_utc=datetime.now(timezone.utc).isoformat(),
        )


def write_trajectory_csv(
    path: str | Path,
    points: Iterable[TrajectoryPoint],
    metadata: ExperimentMetadata,
) -> tuple[Path, Path]:
    """Write raw trajectory values and a JSON metadata sidecar."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = list(points)
    if not rows:
        raise ValueError("at least one trajectory point is required")
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            [
                "time_s",
                "position_normalized_percent",
                "velocity_percent_per_s",
                "acceleration_percent_per_s2",
                "jerk_percent_per_s3",
            ]
        )
        for point in rows:
            writer.writerow(
                [
                    point.time,
                    point.position,
                    point.velocity,
                    point.acceleration,
                    point.jerk,
                ]
            )
    metadata_path = output.with_suffix(output.suffix + ".metadata.json")
    metadata_path.write_text(
        json.dumps(asdict(metadata), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output, metadata_path
