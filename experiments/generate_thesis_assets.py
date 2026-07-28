#!/usr/bin/env python3
"""Generate figures and tables exclusively from a retained simulation run."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import shutil

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def save(figure: plt.Figure, directory: Path, name: str) -> None:
    figure.tight_layout()
    for extension in ("pdf", "svg", "png"):
        figure.savefig(directory / f"{name}.{extension}", dpi=240, bbox_inches="tight")
    plt.close(figure)


def line_plot(directory: Path, name: str, title: str, ylabel: str, series) -> None:
    figure, axis = plt.subplots(figsize=(7.2, 4.2))
    for label, x, y in series:
        axis.plot(x, y, label=label, linewidth=1.8)
    axis.set(title=title, xlabel="Simulation time (s)", ylabel=ylabel)
    axis.grid(alpha=0.25)
    axis.legend(frameon=False)
    save(figure, directory, name)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    run = args.run_dir.resolve()
    figures, tables = run / "figures", run / "tables"
    figures.mkdir(exist_ok=True)
    tables.mkdir(exist_ok=True)

    step = read(run / "raw" / "step_response.csv")
    step_series = []
    for experiment in ("step_25", "step_50", "step_100"):
        rows = [r for r in step if r["experiment_id"] == experiment]
        step_series.append((experiment, [float(r["simulation_time_s"]) for r in rows],
                            [float(r["actual_position_percent"]) for r in rows]))
    line_plot(figures, "01_simulated_motor_step_response",
              "Simulated motor step responses", "Actual position (normalized %)", step_series)
    rows100 = [r for r in step if r["experiment_id"] == "step_100"]
    time100 = [float(r["simulation_time_s"]) for r in rows100]
    line_plot(figures, "02_target_and_actual_position",
              "Target and simulated actual position", "Position (normalized %)",
              [("target", time100, [100.0] * len(rows100)),
               ("actual", time100, [float(r["actual_position_percent"]) for r in rows100])])
    figure, axes = plt.subplots(2, 1, figsize=(7.2, 6.0), sharex=True)
    axes[0].plot(time100, [float(r["velocity_percent_s"]) for r in rows100])
    axes[0].set_ylabel("Velocity (%/s)")
    axes[0].grid(alpha=0.25)
    axes[1].plot(time100, [float(r["acceleration_percent_s2"]) for r in rows100])
    axes[1].set(xlabel="Simulation time (s)", ylabel="Acceleration (%/s²)")
    axes[1].grid(alpha=0.25)
    figure.suptitle("Actuator dynamic state")
    save(figure, figures, "03_velocity_and_acceleration")

    trajectory = read(run / "raw" / "trajectory_comparison.csv")
    series = []
    for method in ("direct", "quintic"):
        rows = [r for r in trajectory if r["method"] == method]
        series.append((method, [float(r["simulation_time_s"]) for r in rows],
                       [float(r["actual_position_percent"]) for r in rows]))
    line_plot(figures, "04_direct_versus_quintic",
              "Direct command versus quintic command", "Actual position (normalized %)", series)
    line_plot(figures, "05_jerk_comparison", "Plant jerk comparison",
              "Jerk (normalized %/s³)",
              [(method,
                [float(r["simulation_time_s"]) for r in trajectory if r["method"] == method],
                [float(r["jerk_percent_s3"]) for r in trajectory if r["method"] == method])
               for method in ("direct", "quintic")])

    pid = read(run / "raw" / "pid_tracking.csv")
    line_plot(figures, "06_pid_tracking_response", "Open-loop and PID tracking",
              "Actual position (normalized %)",
              [(mode, [float(r["simulation_time_s"]) for r in pid if r["mode"] == mode],
                [float(r["actual_position_percent"]) for r in pid if r["mode"] == mode])
               for mode in ("open_loop", "pid_closed_loop")])
    line_plot(figures, "07_pid_tracking_error", "PID tracking error",
              "Error (normalized %)",
              [("PID error",
                [float(r["simulation_time_s"]) for r in pid if r["mode"] == "pid_closed_loop"],
                [float(r["tracking_error_percent"]) for r in pid if r["mode"] == "pid_closed_loop"])])

    gesture = read(run / "raw" / "gesture_transition.csv")
    line_plot(figures, "08_multi_joint_gesture_transition", "Multi-joint gesture transition",
              "Actual position (normalized %)",
              [(f"motor_{motor}", [float(r["simulation_time_s"]) for r in gesture
                                   if int(r["motor_id"]) == motor],
                [float(r["actual_position_percent"]) for r in gesture
                 if int(r["motor_id"]) == motor]) for motor in range(1, 7)])
    motor1 = [r for r in gesture if r["motor_id"] == "1"]
    figure, axis = plt.subplots(figsize=(5.6, 5.0))
    axis.plot([float(r["fingertip_x_m"]) for r in motor1],
              [float(r["fingertip_y_m"]) for r in motor1])
    axis.set(title="Nominal virtual fingertip trajectory", xlabel="x (m)", ylabel="y (m)")
    axis.axis("equal")
    axis.grid(alpha=0.25)
    save(figure, figures, "09_fingertip_trajectory")

    workspace = read(run / "raw" / "nominal_workspace.csv")
    figure, axis = plt.subplots(figsize=(5.6, 5.0))
    axis.scatter([float(r["fingertip_x_m"]) for r in workspace],
                 [float(r["fingertip_y_m"]) for r in workspace], s=9)
    axis.set(title="Nominal virtual fingertip workspace sample", xlabel="x (m)", ylabel="y (m)")
    axis.axis("equal")
    axis.grid(alpha=0.25)
    save(figure, figures, "10_virtual_fingertip_workspace")

    fault = read(run / "raw" / "fault_injection.csv")
    line_plot(figures, "11_fault_injection_response", "Motor-stuck and feedback fault response",
              "Position (normalized %)",
              [("target", [float(r["simulation_time_s"]) for r in fault],
                [float(r["target_position_percent"]) for r in fault]),
               ("actual", [float(r["simulation_time_s"]) for r in fault],
                [float(r["actual_position_percent"]) for r in fault])])
    figure, axis = plt.subplots(figsize=(7.2, 2.8))
    times = [float(r["simulation_time_s"]) for r in fault]
    codes = [0 if not r["fault_state"] else
             (1 if r["fault_state"] == "motor_stuck" else 2) for r in fault]
    axis.step(times, codes, where="post")
    axis.set(title="Fault-state timeline", xlabel="Simulation time (s)",
             yticks=[0, 1, 2], yticklabels=["clear", "stuck", "feedback unavailable"])
    axis.grid(alpha=0.25)
    save(figure, figures, "12_safety_fault_timeline")

    processed = sorted((run / "processed").glob("*.csv"))
    for path in processed:
        shutil.copy2(path, tables / path.name)
    metadata = json.loads((run / "metadata.json").read_text(encoding="utf-8"))
    tex_lines = [
        "% Generated from retained simulation CSV; inspect before manuscript use.",
        r"\begin{tabular}{ll}",
        r"\toprule",
        r"Parameter & Value \\",
        r"\midrule",
        f"Update rate & {metadata['simulation_update_rate_hz']:.0f} Hz \\\\",
        f"Random seed & {metadata['random_seed']} \\\\",
        r"Plant time constant & 0.20 s \\",
        r"Maximum velocity & 250 normalized \%/s \\",
        r"Maximum acceleration & 1500 normalized \%/s$^2$ \\",
        r"\bottomrule",
        r"\end{tabular}",
    ]
    (tables / "simulated_motor_parameters.tex").write_text(
        "\n".join(tex_lines) + "\n", encoding="utf-8"
    )
    summary = (
        "# Generated simulation assets\n\n"
        "All figures in `figures/` were generated from CSV files in `raw/`. "
        "They describe a deterministic lightweight actuator-level simulation "
        "with nominal virtual geometry, not physical hardware measurements.\n\n"
        f"- Source run: `{run.name}`\n"
        f"- Git commit recorded by run: `{metadata['git_commit']}`\n"
        f"- Figure families: {len(list(figures.glob('*.pdf')))}, each in PDF/SVG/PNG\n"
        f"- Processed tables: {len(processed)} CSV plus one LaTeX parameter table\n"
    )
    (run / "THESIS_ASSET_SUMMARY.md").write_text(summary, encoding="utf-8")
    print(run)


if __name__ == "__main__":
    main()
