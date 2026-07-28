# Implementation Status

Status reflects the current source and tests, not README claims or historical
build products.

| Module | Status | Evidence | Related files | Problems | Required work |
|---|---|---|---|---|---|
| Source recovery | Implemented and verified | Exact SHA fetch matched `7424eae…` | `RECOVERY_PROVENANCE.md` | Original gitlink had no mapping | Preserve provenance |
| Low-level driver abstraction | Implemented and verified | Pure unit tests | `driver.py`, `test_driver.py` | Synchronous API | Consider async transport only after profiling |
| Protocol handling | Implemented and verified | Fake-transport CRC/checksum tests | `protocols.py`, `test_protocols.py` | Hardware timing unverified | Run device protocol tests |
| MPD20 backend | Implemented but not verified | Static implementation and packet tests | `real_drivers.py` | Register semantics inherited from snapshot | Verify against device/manual |
| HTS20L backend | Partially implemented | Position adapter present | `real_drivers.py` | Baud-code map unavailable | Supply authoritative map |
| Feetech backend | Implemented but not verified | Status/checksum validation tested with fake transport | `real_drivers.py` | Device response behavior unverified | Hardware test |
| Mock backend | Implemented and verified | Deterministic state and validation tests | `driver.py`, `test_driver.py` | No physical dynamics | Keep claims limited to functional simulation |
| Simulated motor backend | Implemented and verified | Explicit-step, limits, seed, fault and PID tests; retained run `20260725_170324` | `sim_driver.py`, `test_sim_driver.py` | Nominal plant parameters | Identify from hardware before physical claims |
| ROS 2 nodes | Implemented and container-verified | Humble ARM64 colcon/launch run `103359Z` | `hand_node.py`, `config_node.py` | Native macOS ROS unavailable | Repeat on deployment Ubuntu if required |
| ROS 2 interfaces | Implemented and container-verified | Humble build plus online SetSimFault call | `src/dex_hand_interfaces/msg/`, `srv/` | Hardware services unverified | Hardware test separately |
| State feedback | Implemented and container-verified | JointState ~99.98 Hz, TF query and rosbag | `hand_node.py`, `joint_mapping.py` | Docker scheduling | Repeat on target host for timing |
| Command handling | Implemented but not verified | ROS callbacks delegate to tested core | `hand_node.py`, `controller.py` | ROS integration unavailable | Launch tests |
| Parameters | Implemented but not verified | Declared parameters and YAML | `hand.yaml`, `hand_node.py` | Dynamic parameter updates unsupported | Target validation |
| QoS | Implemented but not verified | Reliable default plus startup-selectable best-effort/depth and automated comparison | `hand_node.py`, `ros_experiment.py` | No Ubuntu result yet; single-host test only | Run full Ubuntu suite |
| Launch system | Implemented and container-verified | Humble headless and RViz launches, clean shutdown | launch files | Docker environment | Deployment-host smoke test remains useful |
| Safety limits | Implemented and verified | Boundary/non-finite/rate tests | `safety.py`, `test_safety.py` | Normalized, not physical limits | Obtain physical limits |
| Emergency stop | Implemented but not verified | Core latch verified; ROS service static | `safety.py`, `hand_node.py` | No hardware torque-off semantics | Define hardware-safe stop |
| Timeout handling | Implemented and verified | Serial short-read/retry and watchdog tests | `protocols.py`, `safety.py` | Hardware timeout values untuned | Device testing |
| Gesture library | Implemented and container-verified | Nine-entry load/validation/order/backward-compatibility tests; isolated Humble service listing and `pinch_two` execution | `gestures.py`, `gestures.yaml`, launch files, `test_gestures.py` | Added presets are illustrative normalized software mappings; hardware execution is not verified | Calibrate on hardware before physical use |
| Trajectory generation | Implemented and verified | Boundary/jerk/multi-axis tests | `trajectory.py`, `test_trajectory.py` | Normalized coordinates only | Validate physical mapping |
| Smooth transitions | Implemented and verified | Mock endpoint/cancellation-state tests | `controller.py`, `test_controller.py` | Timing not real-time | Measure on target |
| Nominal forward kinematics | Implemented and verified | Analytical unit test and workspace experiment | `kinematics.py`, `test_joint_mapping.py` | Assumed planar geometry only | Supply calibrated model for physical claims |
| Physical forward kinematics | Blocked by missing information | No calibrated geometry/mapping | — | Geometry, frames, axes absent | Supply verified model |
| Inverse kinematics | Blocked by missing information | FK prerequisite absent | — | No verified chain | Supply verified model |
| PID | Implemented and verified | Deterministic saturation/convergence tests | `pid.py`, `test_pid.py` | Gains not hardware tuned | Conduct controlled tuning |
| Nominal visualization | Implemented and container-verified | Xvfb/RViz/noVNC plus framebuffer screenshots | `urdf/`, `rviz/`, Mac Docker run | Assumed geometry; llvmpipe | Physical model/calibration remains absent |
| Isaac Sim 4.5 integration | Implemented; ROS side container-verified; Isaac runtime pending | URDF parse/build, six-joint command publication, open/fist endpoint test | `isaacsim/launch_dex_hand.py`, `isaac_sim.launch.py`, `run_isaacsim.sh` | Isaac Sim 4.5 is unavailable on the development Mac | Run the documented viewport and feedback-topic acceptance test on Ubuntu |
| Automated tests | Implemented and verified | Pure test suite passes locally | `test/` | ROS/hardware tests blocked | Run target suite |
| Experiments | Partially implemented | One-command E00--E07 collectors, analysis, and evidence indexing | `scripts/run_thesis_experiments.sh`, `tools/`, `experiments/` | ROS runtime execution pending on Ubuntu; no hardware | Execute full Ubuntu suite |
| Documentation | Implemented and verified | Requested audit documents present | `docs/` | Must track later target results | Update after each run |
