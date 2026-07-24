# Thesis Experiment Guide

## Scope

The automated suite evaluates the implemented software without a physical
dexterous hand. It distinguishes:

- `environment_record`: deployment and toolchain evidence.
- `algorithm_output`: deterministic trajectory or PID computation.
- `ros2_virtual_backend_measurement`: ROS 2 execution using `driver_type=fake`.

None of these categories is a hardware measurement. The suite does not support
claims about actuator accuracy, physical stopping time, torque, contact,
temperature, power, grasp success, serial latency, or physical trajectory
tracking.

## Run sequence

One-time Ubuntu setup:

```bash
cd ~/yl/dex_hand_ros2
git pull --ff-only
./scripts/bootstrap_ubuntu.sh
```

Short deployment check:

```bash
./scripts/run_thesis_experiments.sh --quick
```

Final no-hardware evidence run:

```bash
./scripts/run_thesis_experiments.sh
```

The full defaults can be overridden without changing source:

```bash
DEX_TIMING_SAMPLES=1200 \
DEX_TIMING_RUNS=5 \
DEX_SAFETY_REPETITIONS=30 \
DEX_RESOURCE_DURATION=120 \
./scripts/run_thesis_experiments.sh
```

## Experiment mapping

| ID | Output | Thesis use |
|---|---|---|
| E00 | Environment JSON/CSV, rosdep and three isolated build logs | Chapter 6 environment and reproducibility; Chapter 7 build result |
| E01 | Colcon and pytest logs | Chapter 7 software verification |
| E02 | Functional result matrix | Chapter 7 interface and command correctness |
| E03 | Raw reliable/best-effort command latency and state inter-arrival CSV | Chapter 7 latency, jitter, QoS and load comparison |
| E04 | Watchdog and emergency-stop software timing | Chapter 7 safety-state behavior |
| E05 | Quintic raw samples and boundary/smoothness summary | Chapters 5--7 trajectory validation |
| E06 | Deterministic P/PI/PID samples and convergence summary | Chapters 5--7 algorithm validation |
| E07 | Linux process CPU, RSS and thread samples | Chapter 7 resource usage |

## Required review before thesis use

1. Open `run_status.csv`. Any failed or skipped item must be disclosed.
2. Open `EVIDENCE_INDEX.md` and confirm evidence-scope labels.
3. Preserve `checksums.sha256` with the submitted data bundle.
4. Use CSV files under `thesis_tables/` for tables.
5. Use SVG files under `thesis_figures/` for figures.
6. Inspect raw logs before writing causal explanations.
7. Do not combine quick and full runs as equivalent replicates.

## Statistical interpretation

The analysis script reports descriptive statistics because timing samples are
serially correlated and run on one computer. Report sample count, mean,
standard deviation, median, IQR, P95, P99, minimum, maximum, and loss count.
Treat the independent run, rather than every message, as the experimental
replicate for inferential comparisons.

## Failure handling

The runner does not overwrite historical evidence or silently convert failures
to successes. It continues where meaningful so that algorithm evidence can
still be collected if ROS runtime experiments fail. A non-zero final exit code
means at least one required step failed; inspect `run_status.csv` and the
referenced log.
