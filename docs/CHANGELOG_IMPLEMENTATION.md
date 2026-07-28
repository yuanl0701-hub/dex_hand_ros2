# Implementation Changelog

## 2026-07-28 — Isaac Sim 4.5 gesture visualization path

- Added collision geometry, positive mass/inertia and joint dynamics to the
  nominal six-joint Xacro so it can be imported as a PhysX articulation.
- Added a dedicated Isaac Sim command configuration and ROS 2 launch. The
  controller publishes standard `JointState` commands on
  `/dex_hand/joint_command`, while Isaac Sim publishes measured articulation
  state on `/isaac_joint_states`; the separated topics prevent feedback loops.
- Added an Isaac Sim 4.5 standalone script that imports the expanded URDF,
  configures position drives, creates the official ROS 2 joint-state
  subscriber/publisher Action Graph and starts the simulation timeline.
- Added Ubuntu one-command startup, a complete gesture-catalogue demonstration
  script, dependency bootstrap updates and a focused operating guide.

Actual results:

| Check | Result |
|---|---|
| Pure Python tests | 49 passed |
| Xacro expansion and `check_urdf` | Passed; one root and six child links |
| Isolated Humble build | 2 packages passed |
| Isaac ROS launch | `/dex_hand/joint_command` published six named joints |
| Gesture endpoint test | `open` approximately 0 rad; `fist` approximately 1.2 rad (joint 6: 0.8 rad) |
| Isaac Sim 4.5 runtime/viewpoint | Pending execution on the Ubuntu/RTX 3090 device |

The ROS 2 command path is verified. A visible Isaac Sim gesture transition and
`/isaac_joint_states` feedback must not be claimed until the Ubuntu acceptance
test in `docs/ISAAC_SIM_4_5_GUIDE.md` passes.

## 2026-07-25 — gesture-switching thesis evidence

- Changed the nominal visual mapping direction so the legacy
  `open=100` preset appears extended and `fist=0` appears flexed in RViz;
  this remains an uncalibrated visualisation convention.
- Added a reproducible Mac/Docker evidence script for
  `fist -> vgesture -> open`, retaining command logs, terminal simulator
  status, `JointState`, X11 RViz captures, and SHA-256 checksums.
- Added a ROS 2 recorder that retained 999 complete joint-state messages
  (5994 joint observations) across a 10 s named-gesture sequence.
- Generated a publication composite in PDF, SVG, PNG, and TIFF and linked its
  source data to the dissertation experiment and result sections.
- Inspected the supplied BrainCo Revo2 USD layers and confirmed 11 revolute
  joints per hand: six driven joints and five PhysX mimic joints, with authored
  limits, mass, collision and visual geometry.
- Added a non-destructive USD pose renderer that reads the authored joint
  frames and limits, records source-layer SHA-256 digests, and creates
  `fist`, `vgesture`, and `open` kinematic views using one camera and lighting
  configuration.
- Replaced the primitive RViz screenshots in the publication composite with
  evidence-aligned Revo2 pose reconstructions while retaining all recorded ROS
  traces and terminal values. The anatomical mapping is explicitly labelled as
  a qualitative visualisation convention, not hardware calibration.

## 2026-07-23

### Repository recovery

- Confirmed clean baseline `main` at `665395d175882320303474bc9ff659c792371cf2`.
- Verified the broken gitlink referenced `7424eae0d385ee0b16c2331a339872c0d33d08cf`.
- `git ls-remote origin` succeeded after network approval.
- Exact-SHA `git fetch --no-tags origin 7424eae…` succeeded in an isolated
  temporary repository.
- Recovered source was normalized into a self-contained package.

### Implemented

- Correct ROS package metadata and interface generation configuration.
- Driver abstraction, deterministic mock, strict Modbus/Feetech protocols,
  real-driver adapters, safety/watchdog, emergency stop, gesture library,
  quintic trajectories, PID, asynchronous ROS adapter, launch/configuration,
  tests, experiment export, and audit/thesis documentation.
- Model-dependent FK/IK/RViz work was not attempted because verified geometry
  is absent.

### Commands and actual results

| Command | Result |
|---|---|
| Initial `git ls-remote origin` in sandbox | Failed: network name resolution blocked |
| Approved `git ls-remote origin` | Passed; `main`/HEAD at `665395d…` |
| Approved exact-SHA fetch | Passed; object type `commit`, exact hash matched |
| Initial `python3 -m pytest` | Blocked: Apple system Python has no pytest |
| Initial `compileall` | Blocked: Apple cache path outside sandbox |
| `ruff check src/dex_hand_ros2/dex_hand_ros2 src/dex_hand_ros2/test` | Passed |
| `PYTHONPATH=src/dex_hand_ros2 /opt/anaconda3/bin/pytest -q src/dex_hand_ros2/test` | Passed: 30 tests at that stage |
| `PYTHONPYCACHEPREFIX=/private/tmp/dex-hand-pycache python3 -m compileall -q ...` | Passed |
| `mypy ... --exclude '(hand_node\|config_node\|gesture_cli)\.py'` | Passed |
| Final pure Python test suite | Passed: 34 tests |
| Final Ruff lint and format checks | Passed |
| Final mypy core check | Passed: no issues in 12 source files |
| XML syntax check for `package.xml` | Passed |
| Theoretical trajectory export smoke test | Passed; output labeled `algorithm_output` in `/private/tmp` |
| `git diff --check` | Passed |
| `python3 setup.py --name --version` from repository root | Failed: command used the wrong working directory |
| `python3 setup.py --name --version` from `src/dex_hand_ros2` | Passed |
| `command -v cmake`, `colcon`, `ros2`, `rclpy` | No commands found; ROS/CMake verification blocked by environment |

ROS 2 build, launch, and hardware tests were not run and are not recorded as
passing.
# 2026-07-24 — Humble interface split and thesis experiment automation

- Pulled Ubuntu evidence commit `cd0657a` with fast-forward-only Git semantics.
- Confirmed the Humble duplicate-target failure caused by generating interfaces
  and installing Python code under the same `dex_hand_ros2` package name.
- Split messages and services into `dex_hand_interfaces`; updated Python
  imports and package dependencies.
- Removed committed colcon build/install/log caches while retaining raw E00
  failure evidence.
- Corrected an unverified historical summary that incorrectly claimed the
  split and three successful builds had already occurred.
- Added Ubuntu bootstrap and one-command E00--E07 experiment collection.
- Added machine-readable metadata, raw CSV, summary tables, dependency-free SVG
  figures, evidence index, checksums, and archive generation.
- Local status: pure/static validation pending in this change; ROS 2 Humble
  execution remains to be verified on Ubuntu.

# 2026-07-25 — Lightweight actuator and virtual-hand simulation

## Implemented

- Kept `MockMotorDriver` unchanged and added an explicitly selected
  `SimulatedMotorDriver` with deterministic `step(dt)`, first-order position
  response, velocity/acceleration saturation, delay/noise and explicit faults.
- Added validated normalized-position to virtual-joint mapping and nominal
  planar fingertip kinematics.
- Added `/joint_states`, simulation status, reset/clear-fault services,
  primitive-geometry Xacro, `robot_state_publisher`, RViz configuration and a
  single simulated-hand launch.
- Added deterministic step, trajectory, gesture, PID, fault and workspace
  experiments plus CSV-to-PDF/SVG/PNG/LaTeX generation.
- Added audit, assumptions, thesis material and claim-to-evidence documents.
- Generated accepted run `experiment_results/20260725_170324`; generated runs
  are ignored by Git and are not source artifacts.

## Commands and actual results

| Command | Result |
|---|---|
| System `python3 -m pytest -q ...` | Blocked: `/usr/bin/python3` has no pytest |
| `PYTHONPATH=src/dex_hand_ros2 /opt/anaconda3/bin/python3 -m pytest -q src/dex_hand_ros2/test` before final PID regression | Passed: 46 tests |
| Final pure-Python suite after PID-on-plant regression | Passed: 47 tests |
| First simulation run `20260725_170211` | Completed; exposed an unsuitable incremental PID experiment definition and was not accepted as thesis evidence |
| Corrected simulation run `20260725_170324` | Completed; raw/config/metadata/processed outputs retained |
| `generate_thesis_assets.py --run-dir experiment_results/20260725_170324` | Passed; 12 figure families in PDF/SVG/PNG, four CSV tables and one LaTeX table |
| Ruff, mypy core, compileall, XML parsing, and `git diff --check` | Passed |
| ROS 2/colcon/xacro/RViz commands | Blocked: tools unavailable on current macOS host |

Physical hardware behavior, calibrated geometry, contact dynamics, ROS 2
runtime publication and RViz rendering are not recorded as verified.

# 2026-07-25 — Apple Silicon Humble and RViz execution

- Added an Ubuntu 22.04 ARM64/Humble Docker environment with rviz2,
  robot_state_publisher, rosbag2, Xvfb, x11vnc and noVNC.
- Added `SetSimFault.srv` and the `/dex_hand/sim/set_fault` service.
- Added macOS wrappers for native experiments, image build, headless ROS
  evidence, RViz start/stop and full orchestration.
- Fixed ROS/colcon setup compatibility with shell strict mode and added bounded
  process-group shutdown.
- Added a dependency-free X11 framebuffer capture utility and hand-scale RViz
  camera/QoS configuration.

Actual results:

| Check | Result |
|---|---|
| Native Python experiment | 47 tests passed; run `20260725_180830` |
| ARM64 Humble colcon build | 2 packages passed |
| Humble colcon test-result | 48 tests, 0 errors/failures/skips |
| ROS graph | One hand node and one robot-state publisher |
| JointState | Approximately 99.98 Hz |
| TF | `base_link` and six motor links observed |
| Online fault | `motor_stuck` accepted and visible with zero velocity |
| Gestures | `open`, `fist`, `vgesture` successful |
| rosbag2 | 1,811 messages over approximately 10.11 s |
| Shutdown | Both launched nodes finished cleanly |
| RViz/noVNC | OpenGL 4.5 llvmpipe; distinct joint poses captured |
| Evidence integrity | SHA-256 verification passed |

Accepted ROS run: `experiment_results/mac_ros2_20260725T103359Z`.
Physical hardware remains unverified.

# 2026-07-26 — Expanded named-gesture library

## Implemented

- Retained the exact legacy `open`, `fist`, and `vgesture` vectors.
- Added `pinch_two`, `pinch_three`, `pinch_side`, `point`, `thumbs_up`, and
  `gesture_666` as complete six-motor normalized software presets.
- Added packaged-configuration tests for catalogue order, complete motor
  coverage, valid ranges, and backward compatibility.
- Updated both launch files to load the packaged gesture configuration by
  default instead of silently falling back to the three built-in definitions.
- Updated the USD renderer to load the validated gesture configuration rather
  than maintaining a separate hard-coded pose list.
- Rendered all nine poses from one Revo2 USD asset and created a
  publication-ready catalogue in PDF, SVG, PNG, and TIFF.

## Commands and actual results

| Check | Result |
|---|---|
| Packaged gesture tests | Passed: 6 tests |
| Full pure-Python suite | Passed: 49 tests |
| Isolated Humble gesture listing | Passed: all 9 names returned |
| Isolated Humble `pinch_two` command | Passed: target vector `[35, 100, 100, 100, 25, 25]` reported by the simulated plant |
| Revo2 USD catalogue render | Passed for 9 poses at 1200 px using macOS Metal outside the filesystem sandbox |
| Physical hardware execution | Not run; mappings remain uncalibrated |

The current BrainCo SDK documents a `0..1000` hardware scale with zero fully
open and 1000 fully closed. This project retains its historical simulation
convention of `0..100`, with 100 represented as extension. No direct hardware
compatibility is claimed.
