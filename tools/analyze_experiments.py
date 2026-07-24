#!/usr/bin/env python3
"""Create thesis-ready summary tables, SVG figures and an evidence index."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re
import statistics
from xml.sax.saxutils import escape


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return math.nan
    location = (len(ordered) - 1) * fraction
    lower = math.floor(location)
    upper = math.ceil(location)
    if lower == upper:
        return ordered[lower]
    weight = location - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def _summary(values: list[float]) -> dict[str, object]:
    return {
        "n": len(values),
        "mean": statistics.fmean(values) if values else "",
        "standard_deviation": statistics.stdev(values) if len(values) > 1 else 0.0,
        "median": statistics.median(values) if values else "",
        "iqr": _percentile(values, 0.75) - _percentile(values, 0.25)
        if values
        else "",
        "p95": _percentile(values, 0.95) if values else "",
        "p99": _percentile(values, 0.99) if values else "",
        "minimum": min(values) if values else "",
        "maximum": max(values) if values else "",
    }


def _write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


COLORS = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9"]


def _line_svg(
    path: Path,
    title: str,
    x_label: str,
    y_label: str,
    series: list[tuple[str, list[tuple[float, float]]]],
) -> None:
    usable = [(name, points) for name, points in series if points]
    if not usable:
        return
    width, height = 900, 520
    left, right, top, bottom = 90, 30, 55, 75
    plot_width = width - left - right
    plot_height = height - top - bottom
    x_values = [x for _, points in usable for x, _ in points]
    y_values = [y for _, points in usable for _, y in points]
    x_min, x_max = min(x_values), max(x_values)
    y_min, y_max = min(y_values), max(y_values)
    if math.isclose(x_min, x_max):
        x_max = x_min + 1.0
    if math.isclose(y_min, y_max):
        y_max = y_min + 1.0
    y_padding = (y_max - y_min) * 0.05
    y_min -= y_padding
    y_max += y_padding

    def sx(value: float) -> float:
        return left + (value - x_min) / (x_max - x_min) * plot_width

    def sy(value: float) -> float:
        return top + (y_max - value) / (y_max - y_min) * plot_height

    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width / 2}" y="30" text-anchor="middle" '
        f'font-family="Arial" font-size="20">{escape(title)}</text>',
    ]
    for index in range(6):
        fraction = index / 5
        x = left + fraction * plot_width
        y = top + fraction * plot_height
        x_value = x_min + fraction * (x_max - x_min)
        y_value = y_max - fraction * (y_max - y_min)
        elements.append(
            f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" '
            f'y2="{top + plot_height}" stroke="#dddddd"/>'
        )
        elements.append(
            f'<line x1="{left}" y1="{y:.2f}" x2="{left + plot_width}" '
            f'y2="{y:.2f}" stroke="#dddddd"/>'
        )
        elements.append(
            f'<text x="{x:.2f}" y="{top + plot_height + 23}" '
            f'text-anchor="middle" font-family="Arial" font-size="12">{x_value:.3g}</text>'
        )
        elements.append(
            f'<text x="{left - 12}" y="{y + 4:.2f}" text-anchor="end" '
            f'font-family="Arial" font-size="12">{y_value:.3g}</text>'
        )
    elements.extend(
        [
            f'<line x1="{left}" y1="{top + plot_height}" x2="{left + plot_width}" '
            f'y2="{top + plot_height}" stroke="black" stroke-width="1.5"/>',
            f'<line x1="{left}" y1="{top}" x2="{left}" '
            f'y2="{top + plot_height}" stroke="black" stroke-width="1.5"/>',
            f'<text x="{left + plot_width / 2}" y="{height - 22}" text-anchor="middle" '
            f'font-family="Arial" font-size="15">{escape(x_label)}</text>',
            f'<text x="23" y="{top + plot_height / 2}" text-anchor="middle" '
            f'font-family="Arial" font-size="15" '
            f'transform="rotate(-90 23 {top + plot_height / 2})">{escape(y_label)}</text>',
        ]
    )
    for index, (name, points) in enumerate(usable):
        color = COLORS[index % len(COLORS)]
        coordinates = " ".join(f"{sx(x):.2f},{sy(y):.2f}" for x, y in points)
        elements.append(
            f'<polyline points="{coordinates}" fill="none" stroke="{color}" '
            f'stroke-width="2"/>'
        )
        legend_x = left + 12 + (index % 3) * 225
        legend_y = top + 18 + (index // 3) * 21
        elements.append(
            f'<line x1="{legend_x}" y1="{legend_y}" x2="{legend_x + 24}" '
            f'y2="{legend_y}" stroke="{color}" stroke-width="3"/>'
        )
        elements.append(
            f'<text x="{legend_x + 31}" y="{legend_y + 4}" '
            f'font-family="Arial" font-size="12">{escape(name)}</text>'
        )
    elements.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(elements) + "\n", encoding="utf-8")


def _ecdf(values: list[float]) -> list[tuple[float, float]]:
    ordered = sorted(values)
    return [
        (value, (index + 1) / len(ordered)) for index, value in enumerate(ordered)
    ]


def analyze_timing(run: Path, tables: Path, figures: Path) -> None:
    grouped: dict[str, list[float]] = {}
    grouped_interarrival: dict[str, list[float]] = {}
    requested: dict[str, int] = {}
    for path in sorted((run / "E03_timing").glob("*/command_latency.csv")):
        rows = _read_rows(path)
        condition = rows[0]["condition"] if rows else path.parent.name
        grouped.setdefault(condition, [])
        requested[condition] = requested.get(condition, 0) + len(rows)
        grouped[condition].extend(
            float(row["latency_ms"])
            for row in rows
            if row.get("matched") == "True" and row.get("latency_ms")
        )
        interarrival_path = path.parent / "state_interarrival.csv"
        if interarrival_path.exists():
            grouped_interarrival.setdefault(condition, []).extend(
                float(row["interarrival_ms"])
                for row in _read_rows(interarrival_path)
                if row.get("interarrival_ms")
            )
    summary_rows = []
    for condition, values in grouped.items():
        row: dict[str, object] = {
            "condition": condition,
            "data_kind": "ros2_virtual_backend_measurement",
            "requested": requested[condition],
            "matched": len(values),
            "loss_count": requested[condition] - len(values),
        }
        row.update({f"latency_ms_{key}": value for key, value in _summary(values).items()})
        summary_rows.append(row)
    _write_rows(tables / "communication_latency_summary.csv", summary_rows)
    interarrival_summaries = []
    for condition, values in grouped_interarrival.items():
        row: dict[str, object] = {
            "condition": condition,
            "data_kind": "ros2_virtual_backend_measurement",
            "observed_frequency_hz_from_mean_period": (
                1000.0 / statistics.fmean(values) if values else ""
            ),
        }
        row.update(
            {
                f"interarrival_ms_{key}": value
                for key, value in _summary(values).items()
            }
        )
        interarrival_summaries.append(row)
    _write_rows(
        tables / "state_interarrival_summary.csv", interarrival_summaries
    )
    _line_svg(
        figures / "communication_latency_ecdf.svg",
        "ROS 2 command-to-state latency",
        "Latency (ms)",
        "Empirical cumulative probability",
        [(condition, _ecdf(values)) for condition, values in grouped.items()],
    )


def copy_core_tables(run: Path, tables: Path) -> None:
    mappings = {
        run / "E00_environment" / "environment_table.csv": "environment_table.csv",
        run / "E00_environment" / "build_summary.csv": "build_summary.csv",
        run / "E02_functional" / "functional_results.csv": "functional_results.csv",
    }
    for source, destination in mappings.items():
        if source.exists():
            (tables / destination).write_text(
                source.read_text(encoding="utf-8"), encoding="utf-8"
            )

    test_rows: list[dict[str, object]] = []
    pytest_log = run / "E01_tests" / "pytest.log"
    if pytest_log.exists():
        text = pytest_log.read_text(encoding="utf-8", errors="replace")
        passed = re.search(r"(\d+)\s+passed", text)
        failed = re.search(r"(\d+)\s+failed", text)
        test_rows.append(
            {
                "test_runner": "pytest",
                "passed": int(passed.group(1)) if passed else "",
                "failed": int(failed.group(1)) if failed else 0,
                "evidence": "E01_tests/pytest.log",
            }
        )
    colcon_log = run / "E01_tests" / "colcon_test_result.log"
    if colcon_log.exists():
        text = colcon_log.read_text(encoding="utf-8", errors="replace")
        match = re.search(
            r"Summary:\s*(\d+)\s+tests?,\s*(\d+)\s+errors?,\s*"
            r"(\d+)\s+failures?,\s*(\d+)\s+skipped",
            text,
        )
        test_rows.append(
            {
                "test_runner": "colcon",
                "passed": int(match.group(1)) - int(match.group(3)) if match else "",
                "failed": int(match.group(3)) if match else "",
                "evidence": "E01_tests/colcon_test_result.log",
            }
        )
    _write_rows(tables / "automated_test_summary.csv", test_rows)


def analyze_safety(run: Path, tables: Path, figures: Path) -> None:
    source = run / "E04_safety" / "safety_timing.csv"
    if not source.exists():
        return
    grouped: dict[str, list[float]] = {}
    for row in _read_rows(source):
        if row.get("success") == "True" and row.get("latency_ms"):
            grouped.setdefault(row["test"], []).append(float(row["latency_ms"]))
    summary_rows = []
    for test, values in grouped.items():
        row: dict[str, object] = {
            "test": test,
            "scope": "software_state_only",
        }
        row.update({f"latency_ms_{key}": value for key, value in _summary(values).items()})
        summary_rows.append(row)
    _write_rows(tables / "software_safety_timing_summary.csv", summary_rows)
    _line_svg(
        figures / "software_safety_latency_ecdf.svg",
        "Software safety state-transition latency",
        "Latency (ms)",
        "Empirical cumulative probability",
        [(test, _ecdf(values)) for test, values in grouped.items()],
    )


def analyze_algorithms(run: Path, tables: Path, figures: Path) -> None:
    trajectory_summary = run / "E05_trajectory" / "trajectory_summary.csv"
    pid_summary = run / "E06_pid" / "pid_summary.csv"
    if trajectory_summary.exists():
        (tables / "trajectory_summary.csv").write_text(
            trajectory_summary.read_text(encoding="utf-8"), encoding="utf-8"
        )
    if pid_summary.exists():
        (tables / "pid_summary.csv").write_text(
            pid_summary.read_text(encoding="utf-8"), encoding="utf-8"
        )

    trajectory_raw = run / "E05_trajectory" / "raw" / "trajectory_samples.csv"
    if trajectory_raw.exists():
        rows = [
            row for row in _read_rows(trajectory_raw) if row["scenario"] == "T06"
        ]
        fields = [
            ("position_normalized_percent", "Position (normalized %)"),
            ("velocity_percent_per_s", "Velocity (normalized %/s)"),
            ("acceleration_percent_per_s2", "Acceleration (normalized %/s²)"),
            ("jerk_percent_per_s3", "Jerk (normalized %/s³)"),
        ]
        for field, label in fields:
            _line_svg(
                figures / f"quintic_{field}.svg",
                "Quintic trajectory: 0–100%, duration 1 s",
                "Time (s)",
                label,
                [
                    (
                        "quintic",
                        [(float(row["time_s"]), float(row[field])) for row in rows],
                    )
                ],
            )

    pid_raw = run / "E06_pid" / "raw" / "pid_samples.csv"
    if pid_raw.exists():
        rows = [
            row for row in _read_rows(pid_raw) if row["scenario"].endswith("_0_100")
        ]
        grouped: dict[str, list[tuple[float, float]]] = {}
        for row in rows:
            grouped.setdefault(row["controller"], []).append(
                (
                    float(row["time_s"]),
                    float(row["measurement_normalized_percent"]),
                )
            )
        _line_svg(
            figures / "pid_algorithm_response.svg",
            "Deterministic PID algorithm response: 0–100%",
            "Algorithm time (s)",
            "State (normalized %)",
            list(grouped.items()),
        )


def analyze_resources(run: Path, tables: Path, figures: Path) -> None:
    grouped_cpu: dict[str, list[float]] = {}
    grouped_rows: dict[str, list[dict[str, str]]] = {}
    for path in sorted((run / "E07_resources").glob("*.csv")):
        rows = _read_rows(path)
        if not rows:
            continue
        condition = rows[0]["condition"]
        grouped_rows.setdefault(condition, []).extend(rows)
        grouped_cpu.setdefault(condition, []).extend(
            float(row["cpu_percent_of_one_core"]) for row in rows
        )
    summaries = []
    for condition, rows in grouped_rows.items():
        cpu = [float(row["cpu_percent_of_one_core"]) for row in rows]
        rss = [float(row["rss_kib"]) / 1024.0 for row in rows]
        threads = [float(row["threads"]) for row in rows]
        summaries.append(
            {
                "condition": condition,
                "samples": len(rows),
                "cpu_mean_percent_of_one_core": statistics.fmean(cpu),
                "cpu_p95_percent_of_one_core": _percentile(cpu, 0.95),
                "rss_mean_mib": statistics.fmean(rss),
                "rss_max_mib": max(rss),
                "threads_median": statistics.median(threads),
            }
        )
    _write_rows(tables / "resource_usage_summary.csv", summaries)
    _line_svg(
        figures / "resource_cpu_ecdf.svg",
        "DEX hand node CPU usage",
        "CPU (% of one logical core)",
        "Empirical cumulative probability",
        [(condition, _ecdf(values)) for condition, values in grouped_cpu.items()],
    )


def write_evidence_index(run: Path) -> None:
    lines = [
        "# Thesis Experiment Evidence Index",
        "",
        f"- Generated at (UTC): {datetime.now(timezone.utc).isoformat()}",
        "- Verification status: generated; interpretation pending",
        "- Hardware-hand measurements: none",
        "",
        "## Evidence-scope rules",
        "",
        "- `environment_record`: deployment evidence only.",
        "- `algorithm_output`: deterministic mathematical/controller output.",
        "- `ros2_virtual_backend_measurement`: ROS 2 timing with the fake backend.",
        "- No file in this run may be described as a physical hand measurement.",
        "",
        "## Files",
        "",
    ]
    for path in sorted(candidate for candidate in run.rglob("*") if candidate.is_file()):
        relative = path.relative_to(run)
        if relative.name != "checksums.sha256":
            lines.append(f"- `{relative}`")
    (run / "EVIDENCE_INDEX.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, required=True)
    args = parser.parse_args()
    tables = args.run / "thesis_tables"
    figures = args.run / "thesis_figures"
    tables.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    copy_core_tables(args.run, tables)
    analyze_timing(args.run, tables, figures)
    analyze_safety(args.run, tables, figures)
    analyze_algorithms(args.run, tables, figures)
    analyze_resources(args.run, tables, figures)
    (args.run / "analysis_method.json").write_text(
        json.dumps(
            {
                "data_kind": "analysis_output",
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "percentile_method": "linear interpolation at (n-1)*p",
                "standard_deviation": "sample standard deviation",
                "figures": "dependency-free SVG generated from retained CSV data",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    write_evidence_index(args.run)


if __name__ == "__main__":
    main()
