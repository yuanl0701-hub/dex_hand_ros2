# Implementation Status

Status reflects the current source and tests, not README claims or historical
build products.

| Module | Status | Evidence | Related files | Problems | Required work |
|---|---|---|---|---|---|
| Source recovery | Implemented and verified | Exact SHA fetch matched `7424eae…` | `RECOVERY_PROVENANCE.md` | Original gitlink had no mapping | Preserve provenance |
| Low-level driver abstraction | Implemented and verified | Pure unit tests | `driver.py`, `test_driver.py` | Synchronous API | Consider async transport only after profiling |
| Protocol handling | Implemented and verified | Fake-transport CRC/checksum/function-03/function-04 tests | `protocols.py`, `test_protocols.py` | Hardware timing unverified | Run device protocol tests |
| MPD20 backend | Implemented and manual-verified; hardware pending | Vendor V1.5/Modbus Poll cross-check; fake-transport mapping, probe, motion-gate and per-axis dropout/recovery tests | `backends/mpd20.py`, `test_mpd20_driver.py` | Physical ID map, travel, direction and timing are unknown; partial operation reduces coordination guarantees | Execute staged physical acceptance and dropout tests |
| HTS20L backend | Partially implemented | Isolated position adapter present | `backends/hts20l.py` | Baud-code map unavailable | Supply authoritative map |
| Feetech backend | Implemented but not verified | Status/checksum validation tested with fake transport | `backends/feetech.py` | Device response behavior unverified | Hardware test |
| Mock backend | Implemented and verified | Deterministic state and validation tests | `driver.py`, `test_driver.py` | No physical dynamics | Keep claims limited to functional simulation |
| Simulated motor backend | Implemented and verified | Explicit-step, limits, seed, fault and PID tests; retained run `20260725_170324` | `sim_driver.py`, `test_sim_driver.py` | Nominal plant parameters | Identify from hardware before physical claims |
| ROS 2 nodes | Implemented and container-verified | Humble ARM64 build/test plus MPD20 launch argument parse on 2026-07-30 | `hand_node.py`, `config_node.py` | Physical serial node unavailable in container | Repeat on deployment Ubuntu with hand |
| ROS 2 interfaces | Implemented and container-verified | Humble build plus online SetSimFault call | `src/dex_hand_interfaces/msg/`, `srv/` | Hardware services unverified | Hardware test separately |
| State feedback | Implemented and container-verified | JointState ~99.98 Hz, TF query and rosbag; MPD20 function-04 and per-axis dropout fake transport | `hand_node.py`, `core/joint_mapping.py`, `backends/mpd20.py` | MPD20 bus polling timing and partial-operation recovery are hardware-unverified | Repeat on target host for timing/dropout behavior |
| Command handling | Implemented and container-smoke-verified | ROS callbacks delegate to tested core; layered Mock launch publishes status | `hand_node.py`, `core/controller.py` | Physical command timing unverified | Deployment-host and hardware tests |
| Parameters | Implemented and container-verified | Runtime/backend/model/deployment overlay installation and launch parse | `config/runtime/`, `config/backends/`, `config/hand_models/`, `config/deployments/` | Dynamic parameter updates unsupported; physical values uncalibrated | Calibrate a per-hand deployment YAML |
| QoS | Implemented but not verified | Reliable default plus startup-selectable best-effort/depth and automated comparison | `hand_node.py`, `ros_experiment.py` | No Ubuntu result yet; single-host test only | Run full Ubuntu suite |
| Launch system | Implemented and container-verified | Humble headless and RViz launches, clean shutdown | launch files | Docker environment | Deployment-host smoke test remains useful |
| Safety limits | Implemented and verified | Boundary/non-finite/rate tests | `safety.py`, `test_safety.py` | Normalized, not physical limits | Obtain physical limits |
| Emergency stop | Implemented but not hardware-verified | Core latch plus active-hold path tests/build | `core/controller.py`, `core/driver.py`, `backends/mpd20.py`, `hand_node.py` | Active position hold is not torque-off | Add independent hardware E-stop and measure response |
| Timeout handling | Implemented and verified in software | Serial short-read/retry, per-axis quarantine/recovery and watchdog tests | `protocols.py`, `backends/mpd20.py`, `safety.py` | Hardware timeout values and intermittent-contact behavior untuned | Device dropout testing |
| Gesture library | Implemented and container-verified | Nine-entry generic catalogue plus separate three-pose MPD20 commissioning catalogue | `core/gestures.py`, `config/hand_models/*/*.json` | Physical poses are not verified | Calibrate each hardware gesture before loaded trials |
| Trajectory generation | Implemented and verified | Boundary/jerk/multi-axis tests | `trajectory.py`, `test_trajectory.py` | Normalized coordinates only | Validate physical mapping |
| Smooth transitions | Implemented and verified | Mock endpoint/cancellation-state and partial-start-feedback tests | `controller.py`, `test_controller.py` | Timing not real-time; partial poses omit unavailable axes | Measure on target |
| Nominal forward kinematics | Implemented and verified | Analytical unit test and workspace experiment | `kinematics.py`, `test_joint_mapping.py` | Assumed planar geometry only | Supply calibrated model for physical claims |
| Physical forward kinematics | Blocked by missing information | No calibrated geometry/mapping | — | Geometry, frames, axes absent | Supply verified model |
| Inverse kinematics | Blocked by missing information | FK prerequisite absent | — | No verified chain | Supply verified model |
| PID | Implemented and verified | Deterministic saturation/convergence tests | `pid.py`, `test_pid.py` | Gains not hardware tuned | Conduct controlled tuning |
| Nominal visualization | Implemented and container-verified | Xvfb/RViz/noVNC plus framebuffer screenshots | `urdf/`, `rviz/`, Mac Docker run | Assumed geometry; llvmpipe | Physical model/calibration remains absent |
| Isaac Sim 4.5 integration | Implemented; ROS side and Revo2 mapping container-verified; Isaac runtime pending | Xacro/URDF parse, bundled Revo2 6-active/5-mimic USD audit, six-joint publication, open/fist/V endpoint tests | `assets/revo2_right_hand/`, `isaacsim/launch_dex_hand.py`, `config/hand_models/revo2_right/`, `isaac_sim.launch.py`, `run_isaacsim.sh` | Isaac Sim 4.5 is unavailable on the development Mac | Run the documented Revo2 viewport and feedback-topic acceptance test on Ubuntu |
| Automated tests | Implemented and verified | 77 pure tests pass locally; historical 69-test Humble package run passed before the latest partial-operation change | `test/` | Latest ROS build and hardware tests pending | Rebuild on target and run physical acceptance suite |
| Experiments | Partially implemented | One-command E00--E07 collectors, analysis, and evidence indexing | `scripts/run_thesis_experiments.sh`, `tools/`, `experiments/` | ROS runtime execution pending on Ubuntu; no hardware | Execute full Ubuntu suite |
| Documentation | Implemented and verified | Requested audit documents present | `docs/` | Must track later target results | Update after each run |
