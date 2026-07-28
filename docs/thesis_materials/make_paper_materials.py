#!/usr/bin/env python3
"""Generate manuscript tables and figures from one thesis experiment archive.

The script reads the archive without modifying it.  It deliberately excludes
E07 from paper figures because that experiment monitored the ``ros2 run``
wrapper rather than the child node process.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import tarfile
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mpl_toolkits.axes_grid1.inset_locator import inset_axes


EXPECTED_ARCHIVE_SHA256 = (
    "47920f495003c87861902d370fc900138ba4f8929b442b1628c52972fc453f3d"
)
CONDITION_ORDER = ["reliable_idle", "best_effort_idle", "cpu_stress"]
CONDITION_LABELS = {
    "reliable_idle": "Reliable\nidle",
    "best_effort_idle": "Best effort\nidle",
    "cpu_stress": "Reliable\nCPU stress",
}
COLORS = {
    "reliable_idle": "#0072B2",
    "best_effort_idle": "#009E73",
    "cpu_stress": "#D55E00",
    "P": "#0072B2",
    "PI": "#009E73",
    "PID": "#D55E00",
}


class ArchiveReader:
    def __init__(self, archive: Path):
        self.archive = archive
        self.tar = tarfile.open(archive, "r:gz")
        roots = {
            member.name.split("/", 1)[0]
            for member in self.tar.getmembers()
            if member.name and not member.name.startswith("/")
        }
        if len(roots) != 1:
            raise ValueError(f"Expected one archive root, found: {sorted(roots)}")
        self.root = roots.pop()

    def close(self) -> None:
        self.tar.close()

    def _bytes(self, relative: str) -> bytes:
        member = self.tar.getmember(f"{self.root}/{relative}")
        file_obj = self.tar.extractfile(member)
        if file_obj is None:
            raise FileNotFoundError(relative)
        return file_obj.read()

    def text(self, relative: str) -> str:
        return self._bytes(relative).decode("utf-8")

    def json(self, relative: str):
        return json.loads(self.text(relative))

    def frame(self, relative: str) -> pd.DataFrame:
        return pd.read_csv(io.BytesIO(self._bytes(relative)))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def configure_plotting() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans", "sans-serif"],
            "mathtext.fontset": "custom",
            "mathtext.rm": "Helvetica",
            "mathtext.it": "Helvetica:italic",
            "mathtext.bf": "Helvetica:bold",
            "font.size": 8.0,
            "axes.titlesize": 8.5,
            "axes.labelsize": 8.0,
            "xtick.labelsize": 7.2,
            "ytick.labelsize": 7.2,
            "legend.fontsize": 7.2,
            "axes.linewidth": 0.8,
            "lines.linewidth": 1.35,
            "lines.markersize": 4.4,
            "xtick.major.width": 0.8,
            "ytick.major.width": 0.8,
            "xtick.direction": "out",
            "ytick.direction": "out",
            "axes.spines.right": False,
            "axes.spines.top": False,
            "legend.frameon": False,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.04,
        }
    )


def save_figure(fig: plt.Figure, output_base: Path) -> None:
    output_base.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_base.with_suffix(".svg"))
    fig.savefig(output_base.with_suffix(".pdf"))
    fig.savefig(output_base.with_suffix(".png"), dpi=600)
    fig.savefig(
        output_base.with_suffix(".tiff"),
        dpi=600,
        pil_kwargs={"compression": "tiff_lzw"},
    )
    plt.close(fig)


def panel_label(ax: plt.Axes, label: str) -> None:
    ax.text(
        -0.14,
        1.06,
        label,
        transform=ax.transAxes,
        fontsize=8.5,
        fontweight="bold",
        va="top",
    )


def style_axis(ax: plt.Axes, grid: bool = True) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if grid:
        ax.grid(axis="y", color="#D9D9D9", linewidth=0.55, alpha=0.75)
        ax.set_axisbelow(True)


def load_timing(reader: ArchiveReader) -> tuple[pd.DataFrame, pd.DataFrame]:
    mapping = {
        "reliable_idle": "idle",
        "best_effort_idle": "best_effort_idle",
        "cpu_stress": "cpu_stress",
    }
    latency_frames = []
    run_rows = []
    for condition, directory in mapping.items():
        for run in range(1, 6):
            base = f"E03_timing/{directory}_run_{run:02d}"
            frame = reader.frame(f"{base}/command_latency.csv")
            frame = frame.loc[frame["matched"].astype(bool)].copy()
            frame["condition"] = condition
            frame["run"] = run
            latency_frames.append(frame)
            intervals = reader.frame(f"{base}/state_interarrival.csv")
            interval_column = next(
                column
                for column in intervals.columns
                if column in {"interarrival_ms", "interval_ms", "period_ms"}
            )
            values = frame["latency_ms"].to_numpy(dtype=float)
            period_ms = intervals[interval_column].to_numpy(dtype=float)
            run_rows.append(
                {
                    "condition": condition,
                    "run": run,
                    "matched_samples": len(values),
                    "mean_latency_ms": np.mean(values),
                    "median_latency_ms": np.median(values),
                    "p95_latency_ms": np.percentile(values, 95),
                    "p99_latency_ms": np.percentile(values, 99),
                    "max_latency_ms": np.max(values),
                    "state_frequency_hz": 1000.0 / np.mean(period_ms),
                }
            )
    return pd.concat(latency_frames, ignore_index=True), pd.DataFrame(run_rows)


def timing_summary(latency: pd.DataFrame, runs: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for condition in CONDITION_ORDER:
        values = latency.loc[
            latency["condition"] == condition, "latency_ms"
        ].to_numpy(dtype=float)
        run_subset = runs.loc[runs["condition"] == condition]
        rows.append(
            {
                "condition": condition,
                "independent_runs_n": len(run_subset),
                "technical_observations": len(values),
                "matched_observations": int(
                    latency.loc[latency["condition"] == condition, "matched"].sum()
                ),
                "pooled_mean_ms": np.mean(values),
                "pooled_sd_ms": np.std(values, ddof=1),
                "pooled_median_ms": np.median(values),
                "pooled_p95_ms": np.percentile(values, 95),
                "pooled_p99_ms": np.percentile(values, 99),
                "pooled_min_ms": np.min(values),
                "pooled_max_ms": np.max(values),
                "mean_state_frequency_hz": run_subset["state_frequency_hz"].mean(),
            }
        )
    return pd.DataFrame(rows)


def plot_timing(
    latency: pd.DataFrame, runs: pd.DataFrame, output_dir: Path
) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(7.20, 4.85))

    metrics = [
        ("mean_latency_ms", "Run-level mean (ms)", "a"),
        ("p95_latency_ms", "Run-level 95th percentile (ms)", "b"),
    ]
    for ax, (metric, ylabel, label) in zip(axes[0], metrics):
        for x, condition in enumerate(CONDITION_ORDER):
            values = runs.loc[runs["condition"] == condition, metric].to_numpy()
            jitter = np.linspace(-0.08, 0.08, len(values))
            ax.scatter(
                np.full(len(values), x) + jitter,
                values,
                s=26,
                color=COLORS[condition],
                edgecolor="white",
                linewidth=0.45,
                zorder=3,
            )
            ax.plot(
                [x - 0.18, x + 0.18],
                [np.median(values), np.median(values)],
                color="#222222",
                linewidth=1.2,
                zorder=4,
            )
        ax.set_xticks(range(3), [CONDITION_LABELS[c] for c in CONDITION_ORDER])
        ax.set_ylabel(ylabel)
        style_axis(ax)
        panel_label(ax, label)

    ax = axes[1, 0]
    for condition in CONDITION_ORDER:
        values = np.sort(
            latency.loc[latency["condition"] == condition, "latency_ms"].to_numpy()
        )
        y = np.arange(1, len(values) + 1) / len(values)
        ax.step(
            values,
            y,
            where="post",
            color=COLORS[condition],
            label=CONDITION_LABELS[condition].replace("\n", " "),
        )
    ax.set_xlim(90, 115)
    ax.set_ylim(0, 1.005)
    ax.set_xlabel("Command-to-observable-state latency (ms)")
    ax.set_ylabel("Empirical cumulative probability")
    ax.legend(frameon=False, loc="lower right", handlelength=1.8)
    style_axis(ax)
    panel_label(ax, "c")
    inset = inset_axes(ax, width="36%", height="35%", loc="upper left", borderpad=0.75)
    inset.set_facecolor("white")
    for condition in CONDITION_ORDER:
        values = np.sort(
            latency.loc[latency["condition"] == condition, "latency_ms"].to_numpy()
        )
        y = np.arange(1, len(values) + 1) / len(values)
        inset.step(values, y, where="post", color=COLORS[condition], linewidth=0.9)
    inset.set_xlim(0, 420)
    inset.set_ylim(0, 1.01)
    inset.set_xticks([0, 200, 400])
    inset.set_yticks([0, 1])
    inset.set_title("Full range", fontsize=6.8, y=1.02, pad=4.0)
    inset.tick_params(labelsize=6.2, length=2.5)
    inset.spines["top"].set_visible(True)
    inset.spines["right"].set_visible(True)
    for spine in inset.spines.values():
        spine.set_linewidth(0.55)

    ax = axes[1, 1]
    for x, condition in enumerate(CONDITION_ORDER):
        values = runs.loc[
            runs["condition"] == condition, "state_frequency_hz"
        ].to_numpy()
        jitter = np.linspace(-0.08, 0.08, len(values))
        ax.scatter(
            np.full(len(values), x) + jitter,
            values,
            s=26,
            color=COLORS[condition],
            edgecolor="white",
            linewidth=0.45,
            zorder=3,
        )
        ax.plot(
            [x - 0.18, x + 0.18],
            [np.median(values), np.median(values)],
            color="#222222",
            linewidth=1.2,
            zorder=4,
        )
    ax.axhline(10.0, color="#666666", linewidth=0.8, linestyle="--")
    ax.set_xticks(range(3), [CONDITION_LABELS[c] for c in CONDITION_ORDER])
    ax.set_ylabel("Observed state frequency (Hz)")
    ax.text(
        0.98,
        0.90,
        "10 Hz target",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=6.7,
        color="#555555",
    )
    style_axis(ax)
    panel_label(ax, "d")

    fig.subplots_adjust(
        left=0.095,
        right=0.985,
        bottom=0.11,
        top=0.975,
        wspace=0.34,
        hspace=0.40,
    )
    save_figure(fig, output_dir / "figure_1_timing_comparison")


def safety_summary(safety: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for test, subset in safety.groupby("test", sort=False):
        values = subset["latency_ms"].to_numpy(dtype=float)
        rows.append(
            {
                "test": test,
                "technical_repetitions_n": len(values),
                "successful": int(subset["success"].astype(bool).sum()),
                "mean_ms": np.mean(values),
                "sd_ms": np.std(values, ddof=1),
                "median_ms": np.median(values),
                "p95_ms": np.percentile(values, 95),
                "min_ms": np.min(values),
                "max_ms": np.max(values),
                "scope": subset["scope"].iloc[0],
            }
        )
    return pd.DataFrame(rows)


def plot_safety(safety: pd.DataFrame, output_dir: Path) -> None:
    tests = ["emergency_stop_service_to_status", "watchdog_state_transition"]
    titles = ["Software E-stop", "Command watchdog"]
    colors = ["#0072B2", "#D55E00"]
    fig, axes = plt.subplots(1, 2, figsize=(7.20, 2.70))
    for ax, test, title, color, label in zip(
        axes, tests, titles, colors, ["a", "b"]
    ):
        values = safety.loc[safety["test"] == test, "latency_ms"].to_numpy()
        jitter = np.linspace(-0.055, 0.055, len(values))
        ax.scatter(
            np.ones(len(values)) + jitter,
            values,
            s=25,
            color=color,
            alpha=0.85,
            edgecolor="white",
            linewidth=0.4,
            zorder=3,
        )
        q1, median, q3 = np.percentile(values, [25, 50, 75])
        ax.plot([0.82, 1.18], [median, median], color="#222222", linewidth=1.4)
        ax.plot([1, 1], [q1, q3], color="#222222", linewidth=2.8)
        ax.set_xlim(0.62, 1.38)
        ax.set_xticks([1], [title])
        ax.set_ylabel("Latency (ms)")
        style_axis(ax)
        panel_label(ax, label)
    fig.subplots_adjust(wspace=0.36)
    save_figure(fig, output_dir / "figure_2_software_safety")


def plot_trajectory(samples: pd.DataFrame, output_dir: Path) -> None:
    subset = samples.loc[samples["scenario"] == "T07"].copy()
    fields = [
        ("position_normalized_percent", "Position (%)", "a"),
        ("velocity_percent_per_s", "Velocity (% s$^{-1}$)", "b"),
        ("acceleration_percent_per_s2", "Acceleration (% s$^{-2}$)", "c"),
        ("jerk_percent_per_s3", "Jerk (% s$^{-3}$)", "d"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(7.20, 4.75), sharex=True)
    for ax, (field, ylabel, label) in zip(axes.flat, fields):
        ax.plot(subset["time_s"], subset[field], color="#0072B2", linewidth=1.6)
        ax.set_ylabel(ylabel)
        ax.set_xlabel("Time (s)")
        style_axis(ax)
        panel_label(ax, label)
    fig.subplots_adjust(wspace=0.34, hspace=0.42)
    save_figure(fig, output_dir / "figure_3_quintic_trajectory")


def pid_summary(summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for controller in ["P", "PI", "PID"]:
        subset = summary.loc[summary["controller"] == controller]
        rows.append(
            {
                "controller": controller,
                "scenarios_n": len(subset),
                "converged_n": int(subset["converged"].astype(bool).sum()),
                "mean_iterations": subset["iterations"].mean(),
                "sd_iterations": subset["iterations"].std(ddof=1),
                "mean_final_abs_error_percent": subset["final_abs_error"].mean(),
                "mean_saturation_count": subset["saturation_count"].mean(),
                "total_saturation_count": int(subset["saturation_count"].sum()),
                "evidence_scope": subset["evidence_scope"].iloc[0],
            }
        )
    return pd.DataFrame(rows)


def plot_pid(
    samples: pd.DataFrame, summary: pd.DataFrame, output_dir: Path
) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(7.20, 3.05))
    ax = axes[0]
    for controller in ["P", "PI", "PID"]:
        scenario = f"{controller}_0_100"
        subset = samples.loc[samples["scenario"] == scenario]
        ax.plot(
            subset["time_s"],
            subset["measurement_normalized_percent"],
            color=COLORS[controller],
            label=controller,
        )
    ax.axhline(100, color="#666666", linewidth=0.8, linestyle="--", label="Target")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Normalized position (%)")
    ax.legend(frameon=False, ncol=2)
    style_axis(ax)
    panel_label(ax, "a")

    ax = axes[1]
    for x, controller in enumerate(["P", "PI", "PID"]):
        values = summary.loc[
            summary["controller"] == controller, "iterations"
        ].to_numpy()
        jitter = np.linspace(-0.06, 0.06, len(values))
        ax.scatter(
            np.full(len(values), x) + jitter,
            values,
            s=27,
            color=COLORS[controller],
            edgecolor="white",
            linewidth=0.45,
            zorder=3,
        )
        ax.plot(
            [x - 0.18, x + 0.18],
            [np.median(values), np.median(values)],
            color="#222222",
            linewidth=1.2,
            zorder=4,
        )
    ax.set_xticks(range(3), ["P", "PI", "PID"])
    ax.set_xlabel("Controller")
    ax.set_ylabel("Iterations to 2% tolerance")
    style_axis(ax)
    panel_label(ax, "b")
    fig.subplots_adjust(wspace=0.34)
    save_figure(fig, output_dir / "figure_4_pid_algorithm")


def write_csv(frame: pd.DataFrame, path: Path, decimals: int = 6) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, float_format=f"%.{decimals}f")


def write_latex_tables(
    timing: pd.DataFrame,
    safety: pd.DataFrame,
    pid: pd.DataFrame,
    output_path: Path,
) -> None:
    labels = {
        "reliable_idle": "Reliable, idle",
        "best_effort_idle": "Best effort, idle",
        "cpu_stress": "Reliable, CPU stress",
        "emergency_stop_service_to_status": "Software E-stop",
        "watchdog_state_transition": "Command watchdog",
    }
    lines = [
        "% Auto-generated by make_paper_materials.py",
        "% Requires: \\usepackage{booktabs}",
        "",
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Command-to-observable-state update timing under the deterministic virtual backend. Values are pooled descriptive summaries; $n=5$ independent runs per condition, with 600 sequential observations per run.}",
        "\\label{tab:timing}",
        "\\begin{tabular}{lrrrrr}",
        "\\toprule",
        "Condition & Mean (ms) & SD (ms) & Median (ms) & P95 (ms) & Max (ms) \\\\",
        "\\midrule",
    ]
    for row in timing.itertuples(index=False):
        lines.append(
            f"{labels[row.condition]} & {row.pooled_mean_ms:.3f} & "
            f"{row.pooled_sd_ms:.3f} & {row.pooled_median_ms:.3f} & "
            f"{row.pooled_p95_ms:.3f} & {row.pooled_max_ms:.3f} \\\\"
        )
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}", ""]
    lines += [
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Software-state safety timing. Each row contains 20 technical repetitions from one experiment session; no physical torque-off was measured.}",
        "\\label{tab:safety}",
        "\\begin{tabular}{lrrrrr}",
        "\\toprule",
        "Mechanism & Success & Mean (ms) & SD (ms) & P95 (ms) & Max (ms) \\\\",
        "\\midrule",
    ]
    for row in safety.itertuples(index=False):
        lines.append(
            f"{labels[row.test]} & {row.successful}/{row.technical_repetitions_n} & "
            f"{row.mean_ms:.3f} & {row.sd_ms:.3f} & {row.p95_ms:.3f} & "
            f"{row.max_ms:.3f} \\\\"
        )
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}", ""]
    lines += [
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Deterministic controller-algorithm checks over four set-point transitions. These results do not include actuator dynamics.}",
        "\\label{tab:pid}",
        "\\begin{tabular}{lrrrr}",
        "\\toprule",
        "Controller & Converged & Mean iterations & Mean final error (\\%) & Saturation count \\\\",
        "\\midrule",
    ]
    for row in pid.itertuples(index=False):
        lines.append(
            f"{row.controller} & {row.converged_n}/{row.scenarios_n} & "
            f"{row.mean_iterations:.1f} & "
            f"{row.mean_final_abs_error_percent:.3f} & "
            f"{row.total_saturation_count} \\\\"
        )
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}", ""]
    output_path.write_text("\n".join(lines), encoding="utf-8")


def write_verification_table(reader: ArchiveReader, output_path: Path) -> None:
    build = reader.frame("E00_environment/build_summary.csv")
    functional = reader.json("E02_functional/functional_summary.json")
    safety = reader.json("E04_safety/safety_summary.json")
    trajectory = reader.frame("E05_trajectory/trajectory_summary.csv")
    pid = reader.frame("E06_pid/pid_summary.csv")
    rows = [
        ["E00", "Isolated workspace builds", 3, int((build["exit_code"] == 0).sum()), "Software build"],
        ["E01", "colcon tests", 36, 36, "Automated software tests"],
        ["E01", "pytest tests", 35, 35, "Automated software tests"],
        ["E02", "Functional cases", functional["tests"], functional["passed"], "Virtual backend"],
        ["E04", "Safety-state repetitions", safety["measurements"], safety["successful"], "Software state only"],
        ["E05", "Quintic trajectory scenarios", len(trajectory), int(trajectory["finite"].astype(bool).sum()), "Deterministic algorithm"],
        ["E06", "Controller scenarios", len(pid), int(pid["converged"].astype(bool).sum()), "Ideal integrator model"],
    ]
    frame = pd.DataFrame(
        rows, columns=["experiment", "verification_item", "total", "passed", "scope"]
    )
    write_csv(frame, output_path, decimals=0)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "generated",
    )
    parser.add_argument(
        "--allow-different-hash",
        action="store_true",
        help="Process a different archive version after explicit review.",
    )
    args = parser.parse_args()
    archive_hash = sha256(args.archive)
    if archive_hash != EXPECTED_ARCHIVE_SHA256 and not args.allow_different_hash:
        raise SystemExit(
            "Archive SHA256 differs from the audited result package. "
            "Use --allow-different-hash only after reviewing the new run.\n"
            f"expected={EXPECTED_ARCHIVE_SHA256}\nactual={archive_hash}"
        )

    configure_plotting()
    output = args.output.resolve()
    figures = output / "figures"
    tables = output / "tables"
    source_data = output / "source_data"
    for directory in [figures, tables, source_data]:
        directory.mkdir(parents=True, exist_ok=True)

    reader = ArchiveReader(args.archive)
    try:
        latency, timing_runs = load_timing(reader)
        timing = timing_summary(latency, timing_runs)
        safety_raw = reader.frame("E04_safety/safety_timing.csv")
        safety = safety_summary(safety_raw)
        trajectory_raw = reader.frame(
            "E05_trajectory/raw/trajectory_samples.csv"
        )
        pid_raw = reader.frame("E06_pid/raw/pid_samples.csv")
        pid_scenarios = reader.frame("E06_pid/pid_summary.csv")
        pid = pid_summary(pid_scenarios)

        write_csv(timing, tables / "table_2_timing_comparison.csv")
        write_csv(safety, tables / "table_3_safety_timing.csv")
        write_csv(pid, tables / "table_4_pid_algorithm.csv")
        write_verification_table(reader, tables / "table_1_software_verification.csv")

        write_csv(timing_runs, source_data / "figure_1_run_level_timing.csv")
        write_csv(
            latency[["condition", "run", "sample", "latency_ms", "matched"]],
            source_data / "figure_1_latency_observations.csv",
        )
        write_csv(safety_raw, source_data / "figure_2_safety_observations.csv")
        write_csv(
            trajectory_raw.loc[trajectory_raw["scenario"] == "T07"],
            source_data / "figure_3_trajectory_T07.csv",
        )
        write_csv(
            pid_raw.loc[pid_raw["scenario"].str.endswith("_0_100")],
            source_data / "figure_4_pid_response.csv",
        )
        write_csv(pid_scenarios, source_data / "figure_4_pid_scenarios.csv")

        plot_timing(latency, timing_runs, figures)
        plot_safety(safety_raw, figures)
        plot_trajectory(trajectory_raw, figures)
        plot_pid(pid_raw, pid_scenarios, figures)
        write_latex_tables(timing, safety, pid, output / "paper_tables.tex")

        provenance = {
            "archive": str(args.archive.resolve()),
            "archive_sha256": archive_hash,
            "archive_root": reader.root,
            "generator": str(Path(__file__).resolve()),
            "included_experiments": ["E00", "E01", "E02", "E03", "E04", "E05", "E06"],
            "excluded_experiments": {
                "E07": (
                    "Resource monitor sampled the ros2 CLI wrapper rather than "
                    "the child dex_hand_node process."
                )
            },
            "statistical_unit": {
                "E03": "five independent runs per condition; 600 sequential technical observations per run",
                "E04": "20 technical repetitions in one experiment session per safety mechanism",
                "E05": "15 deterministic algorithm scenarios",
                "E06": "four deterministic set-point scenarios per controller",
            },
            "data_exclusions": "None. The 408.009 ms E03 observation is retained.",
        }
        (output / "provenance.json").write_text(
            json.dumps(provenance, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    finally:
        reader.close()

    print(f"Generated paper materials in {output}")


if __name__ == "__main__":
    main()
