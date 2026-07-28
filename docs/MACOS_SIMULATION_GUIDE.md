# macOS ARM64 simulation and ROS 2 experiment guide

## Supported workflow

The current host is Apple Silicon (`arm64`) running macOS 26.5.2. The
actuator-level experiments run natively with Python, while ROS 2 Humble runs
inside an Ubuntu 22.04 ARM64 Docker container. RViz uses Xvfb and Mesa
llvmpipe; noVNC exposes the virtual display only on `127.0.0.1:6080`.

This arrangement verifies the target Humble packages without claiming native
macOS ROS support or physical hardware behavior.

## One-time image build

Start Docker Desktop, then run:

```bash
./scripts/mac/build_ros2_humble_container.sh
```

The image is `dex-hand-ros2-humble:local`. Its build installs Humble,
robot_state_publisher, xacro, rviz2, rosbag2, Xvfb, x11vnc and noVNC.

## Native deterministic experiments

```bash
./scripts/mac/run_native_simulation.sh
```

This runs the pure-Python suite, creates a new timestamped raw-data directory
and generates the PDF/SVG/PNG/CSV/LaTeX assets.

## Headless Humble experiment

```bash
./scripts/mac/run_ros2_headless_experiments.sh
```

The script performs rosdep resolution, isolated colcon build/test, launch,
topic/service/parameter inventory, JointState frequency measurement, TF
query, three gestures, online stuck-fault injection, reset/clear, rosbag2
recording, process-group clean shutdown and SHA-256 generation.

The isolated build tree is `.experiment_work/mac_ros2`; it does not replace
the repository's existing build/install/log trees.

## RViz over noVNC

```bash
./scripts/mac/start_rviz.sh
```

Open [http://localhost:6080/vnc.html](http://localhost:6080/vnc.html), press
**Connect**, and inspect the nominal virtual hand. Stop it with:

```bash
./scripts/mac/stop_rviz.sh
```

The RViz config uses a hand-scale grid/camera, a transient-local
`/robot_description` subscription and a 20 Hz rendering limit. TF overlay is
off by default for readable screenshots; TF publication remains active.

For a dependency-free framebuffer evidence image:

```bash
docker exec ros2_humble_sim-rviz-1 python3 /workspace/tools/capture_x11.py \
  --output /workspace/experiment_results/<run>/screenshots/rviz.png
```

## Verified run on 2026-07-25

- Native run: `experiment_results/20260725_180830`
- Humble/RViz run: `experiment_results/mac_ros2_20260725T103359Z`
- Native tests: 47 passed.
- Humble colcon result: 48 tests, 0 errors, 0 failures, 0 skipped.
- Nodes: one `/dex_hand_node`, one `/robot_state_publisher`.
- JointState observed rate: approximately 99.98 Hz.
- TF tree: `base_link` plus all six `motor_N_link` frames.
- Online `motor_stuck` fault: service success; status reported motor 1 stuck
  with zero simulated velocity.
- Three legacy gestures: `open`, `fist`, `vgesture`, all logged successful.
- rosbag2: 1,811 messages over about 10.11 s, including JointState, TF,
  status and MotorState.
- Clean shutdown: both launched processes reported clean completion.
- RViz: actual X11 framebuffer screenshots retained for two distinct joint
  configurations; Mesa reported OpenGL 4.5 through llvmpipe.

## Limitations

Docker Desktop and software rendering add host scheduling variability, so the
measured ROS publication timing is deployment evidence, not a hard real-time
guarantee. The serial package is skipped by the no-hardware rosdep run because
real transports import pyserial lazily; hardware experiments still require
that dependency and device access. Geometry and plant parameters remain
nominal assumptions.
