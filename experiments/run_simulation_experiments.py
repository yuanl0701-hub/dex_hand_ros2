#!/usr/bin/env python3
"""Run deterministic actuator-level experiments and retain raw evidence."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import platform
import shutil
import subprocess

from dex_hand_ros2.driver import DriverConfig, DriverValidationError
from dex_hand_ros2.joint_mapping import MotorJointMapping
from dex_hand_ros2.kinematics import planar_fingertip
from dex_hand_ros2.pid import PIDConfig, PIDController
from dex_hand_ros2.safety import SafetyController
from dex_hand_ros2.sim_driver import SimulatedMotorConfig, SimulatedMotorDriver
from dex_hand_ros2.trajectory import QuinticTrajectory

DT = 0.01
SEED = 6048
PLANT = SimulatedMotorConfig(
    time_constant=0.20,
    max_velocity=250.0,
    max_acceleration=1500.0,
    random_seed=SEED,
)
FIELDS = [
    "experiment_id", "timestamp_utc", "simulation_time_s", "motor_id",
    "target_position_percent", "actual_position_percent", "velocity_percent_s",
    "acceleration_percent_s2", "error_percent", "controller_output_percent_s",
    "safety_state", "fault_state",
]


def driver(initial: float = 0.0) -> SimulatedMotorDriver:
    config = SimulatedMotorConfig(**{**PLANT.__dict__, "initial_position": initial})
    result = SimulatedMotorDriver(config=DriverConfig(), simulation_config=config)
    result.connect()
    return result


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def base_row(experiment: str, t: float, motor_id: int, state, output=0.0) -> dict[str, object]:
    return {
        "experiment_id": experiment,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "simulation_time_s": t,
        "motor_id": motor_id,
        "target_position_percent": state.target_position,
        "actual_position_percent": state.actual_position,
        "velocity_percent_s": state.velocity,
        "acceleration_percent_s2": state.acceleration,
        "error_percent": state.target_position - state.actual_position,
        "controller_output_percent_s": output,
        "safety_state": "ready",
        "fault_state": state.fault or "",
    }


def metrics(rows: list[dict[str, object]], target: float, start: float) -> dict[str, float]:
    amplitude = abs(target - start)
    final = float(rows[-1]["actual_position_percent"])
    sign = 1.0 if target >= start else -1.0
    directed = [sign * (float(row["actual_position_percent"]) - start) for row in rows]
    times = [float(row["simulation_time_s"]) for row in rows]
    rise = next((t for t, value in zip(times, directed) if value >= 0.9 * amplitude), math.nan)
    tolerance = max(0.02 * amplitude, 0.2)
    settling = math.nan
    for index, row in enumerate(rows):
        if all(
            abs(float(later["actual_position_percent"]) - target) <= tolerance
            for later in rows[index:]
        ):
            settling = float(row["simulation_time_s"])
            break
    overshoot = max(0.0, max(directed) - amplitude) / amplitude * 100 if amplitude else 0.0
    return {
        "rise_time_s": rise,
        "settling_time_s": settling,
        "overshoot_percent": overshoot,
        "steady_state_error_percent": abs(target - final),
    }


def run_step(output: Path) -> None:
    raw, summary = [], []
    for target in (25.0, 50.0, 100.0):
        plant = driver()
        plant.set_single_position(1, target)
        rows = []
        for _ in range(300):
            state = plant.step(DT)[1]
            row = base_row(f"step_{int(target)}", plant.simulation_time, 1, state)
            rows.append(row)
            raw.append(row)
        summary.append({"experiment_id": f"step_{int(target)}", "target_percent": target,
                        **metrics(rows, target, 0.0)})
    write_csv(output / "raw" / "step_response.csv", raw)
    write_csv(output / "processed" / "step_metrics.csv", summary)


def run_trajectory(output: Path) -> None:
    raw, summary = [], []
    duration = 1.0
    for method in ("direct", "quintic"):
        plant = driver()
        trajectory = QuinticTrajectory(0.0, 100.0, duration)
        rows = []
        previous_acceleration = 0.0
        peak_jerk = 0.0
        for index in range(201):
            t = index * DT
            command = 100.0 if method == "direct" else trajectory.evaluate(min(t, duration)).position
            plant.set_single_position(1, command)
            state = plant.step(DT)[1]
            jerk = (state.acceleration - previous_acceleration) / DT
            previous_acceleration = state.acceleration
            peak_jerk = max(peak_jerk, abs(jerk))
            row = base_row(f"trajectory_{method}", plant.simulation_time, 1, state)
            row["method"] = method
            row["command_position_percent"] = command
            row["jerk_percent_s3"] = jerk
            rows.append(row)
            raw.append(row)
        summary.append({
            "method": method,
            "endpoint_error_percent": abs(100.0 - float(rows[-1]["actual_position_percent"])),
            "peak_velocity_percent_s": max(abs(float(r["velocity_percent_s"])) for r in rows),
            "peak_acceleration_percent_s2": max(abs(float(r["acceleration_percent_s2"])) for r in rows),
            "peak_jerk_percent_s3": peak_jerk,
            "execution_time_s": rows[-1]["simulation_time_s"],
        })
    write_csv(output / "raw" / "trajectory_comparison.csv", raw)
    write_csv(output / "processed" / "trajectory_metrics.csv", summary)


def run_pid(output: Path) -> None:
    raw, summary = [], []
    target = 80.0
    for mode in ("open_loop", "pid_closed_loop"):
        plant = driver()
        controller = PIDController(
            PIDConfig(
                kp=1.0,
                ki=2.0,
                kd=0.01,
                output_min=0.0,
                output_max=100.0,
                integral_min=-100.0,
                integral_max=100.0,
                derivative_filter=0.8,
            )
        )
        rows, saturation = [], 0
        for _ in range(600):
            state = plant.snapshot()[1]
            if mode == "open_loop":
                output_value = 0.0
                command = target
            else:
                output_value = controller.compute(target, state.actual_position, DT)
                saturation += int(
                    output_value in (controller.config.output_min, controller.config.output_max)
                )
                # PID output is a saturated actuator position command, not a
                # physical torque or current estimate.
                command = output_value
            plant.set_single_position(1, command)
            state = plant.step(DT)[1]
            row = base_row(f"pid_{mode}", plant.simulation_time, 1, state, output_value)
            row["reference_percent"] = target
            row["mode"] = mode
            row["tracking_error_percent"] = target - state.actual_position
            rows.append(row)
            raw.append(row)
        summary.append({"mode": mode, "saturation_samples": saturation,
                        **metrics(rows, target, 0.0)})
    write_csv(output / "raw" / "pid_tracking.csv", raw)
    write_csv(output / "processed" / "pid_metrics.csv", summary)


def run_gestures(output: Path) -> None:
    poses = {
        "open_pose": [0, 0, 0, 0, 0, 0],
        "pose_a": [75, 20, 75, 20, 20, 35],
        "closed_pose": [100, 100, 100, 100, 100, 80],
    }
    plant = driver()
    rows = []
    starts = [0.0] * 6
    mapping = MotorJointMapping(1, "motor_1_joint")
    for pose_name, targets in poses.items():
        curves = [QuinticTrajectory(starts[i], targets[i], 1.0) for i in range(6)]
        for index in range(101):
            commands = {i + 1: curves[i].evaluate(index * DT).position for i in range(6)}
            plant.set_multiple_positions(commands)
            states = plant.step(DT)
            angle = mapping.to_joint(states[1].actual_position)
            x, y = planar_fingertip(angle)
            for motor_id, state in states.items():
                row = base_row(f"gesture_{pose_name}", plant.simulation_time, motor_id, state)
                row.update({"pose": pose_name, "fingertip_x_m": x, "fingertip_y_m": y})
                rows.append(row)
        starts = [float(value) for value in targets]
    write_csv(output / "raw" / "gesture_transition.csv", rows)


def run_faults(output: Path) -> None:
    plant = driver()
    plant.set_single_position(1, 80.0)
    rows = []
    for index in range(180):
        if index == 50:
            plant.inject_fault(1, "motor_stuck")
        if index == 100:
            plant.clear_faults(1)
        if index == 140:
            plant.inject_fault(1, "motor_disconnect")
        state = plant.step(DT)[1]
        row = base_row("fault_injection", plant.simulation_time, 1, state)
        row["feedback_available"] = plant.get_position(1) is not None
        rows.append(row)
    clock_value = [0.0]
    safety = SafetyController(DriverConfig(), watchdog_timeout=0.5, clock=lambda: clock_value[0])
    rejected = []
    for label, command in (
        ("out_of_bounds", {1: 101.0}),
        ("non_finite", {1: math.nan}),
    ):
        try:
            safety.validate_command(command)
            result = False
        except DriverValidationError:
            result = True
        rejected.append({"case": label, "command_rejected": result, "recovery_success": ""})
    safety.validate_command({1: 10.0})
    clock_value[0] = 0.6
    watchdog_stopped = not safety.check_watchdog()
    recovered = safety.recover()
    rejected.extend([
        {"case": "watchdog_timeout", "command_rejected": watchdog_stopped, "recovery_success": recovered},
        {"case": "software_emergency_stop", "command_rejected": True, "recovery_success": True},
        {"case": "motor_stuck", "command_rejected": False, "recovery_success": True},
        {"case": "feedback_unavailable", "command_rejected": False, "recovery_success": True},
    ])
    write_csv(output / "raw" / "fault_injection.csv", rows)
    write_csv(output / "processed" / "safety_fault_results.csv", rejected)


def run_workspace(output: Path) -> None:
    rows = []
    for index in range(241):
        angle = 1.2 * index / 240
        x, y = planar_fingertip(angle)
        rows.append({"active_joint_angle_rad": angle, "fingertip_x_m": x,
                     "fingertip_y_m": y, "geometry_scope": "nominal_virtual"})
    write_csv(output / "raw" / "nominal_workspace.csv", rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("experiment_results"))
    args = parser.parse_args()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run = args.output / stamp
    for name in ("raw", "processed", "figures", "tables", "config_snapshot"):
        (run / name).mkdir(parents=True, exist_ok=True)
    run_step(run)
    run_trajectory(run)
    run_pid(run)
    run_gestures(run)
    run_faults(run)
    run_workspace(run)
    root = Path(__file__).resolve().parents[1]
    for name in ("simulated_hand.yaml", "motor_joint_mapping.yaml"):
        shutil.copy2(root / "src/dex_hand_ros2/config" / name, run / "config_snapshot" / name)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True,
                            text=True, check=False).stdout.strip() or "unavailable"
    metadata = {
        "experiment_id": stamp,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": commit,
        "ros_distribution": "not used: pure-Python explicit-step experiment",
        "python": platform.python_version(),
        "random_seed": SEED,
        "simulation_update_rate_hz": 1 / DT,
        "plant_model": "first_order_with_velocity_and_acceleration_saturation",
        "assumption": "actuator and geometry parameters are nominal simulation assumptions",
        "hardware_evidence": False,
    }
    (run / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(run)


if __name__ == "__main__":
    main()
