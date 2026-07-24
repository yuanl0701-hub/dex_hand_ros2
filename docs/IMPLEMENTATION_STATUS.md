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
| ROS 2 nodes | Implemented but not verified | Static source inspection | `hand_node.py`, `config_node.py` | `rclpy` unavailable on macOS | Build and launch on ROS 2 Humble |
| ROS 2 interfaces | Implemented but not verified | Dedicated interface package and inventory | `src/dex_hand_interfaces/msg/`, `srv/` | Post-split Humble build not yet captured | Run the Ubuntu experiment suite |
| State feedback | Implemented but not verified | Worker-based state polling publishes each motor | `hand_node.py` | Physical frequency/latency unknown | ROS and hardware test |
| Command handling | Implemented but not verified | ROS callbacks delegate to tested core | `hand_node.py`, `controller.py` | ROS integration unavailable | Launch tests |
| Parameters | Implemented but not verified | Declared parameters and YAML | `hand.yaml`, `hand_node.py` | Dynamic parameter updates unsupported | Target validation |
| QoS | Implemented but not verified | Reliable default plus startup-selectable best-effort/depth and automated comparison | `hand_node.py`, `ros_experiment.py` | No Ubuntu result yet; single-host test only | Run full Ubuntu suite |
| Launch system | Implemented but not verified | Fake-safe launch file | `hand.launch.py` | ROS launch unavailable | Target smoke test |
| Safety limits | Implemented and verified | Boundary/non-finite/rate tests | `safety.py`, `test_safety.py` | Normalized, not physical limits | Obtain physical limits |
| Emergency stop | Implemented but not verified | Core latch verified; ROS service static | `safety.py`, `hand_node.py` | No hardware torque-off semantics | Define hardware-safe stop |
| Timeout handling | Implemented and verified | Serial short-read/retry and watchdog tests | `protocols.py`, `safety.py` | Hardware timeout values untuned | Device testing |
| Gesture library | Implemented and verified | Load/validation/order tests | `gestures.py`, `gestures.yaml` | Motor mapping is not anatomical | Verify hand mapping |
| Trajectory generation | Implemented and verified | Boundary/jerk/multi-axis tests | `trajectory.py`, `test_trajectory.py` | Normalized coordinates only | Validate physical mapping |
| Smooth transitions | Implemented and verified | Mock endpoint/cancellation-state tests | `controller.py`, `test_controller.py` | Timing not real-time | Measure on target |
| Forward kinematics | Blocked by missing information | No URDF/link geometry | — | Geometry, frames, axes absent | Supply verified model |
| Inverse kinematics | Blocked by missing information | FK prerequisite absent | — | No verified chain | Supply verified model |
| PID | Implemented and verified | Deterministic saturation/convergence tests | `pid.py`, `test_pid.py` | Gains not hardware tuned | Conduct controlled tuning |
| Visualization | Blocked by missing information | No model or RViz config | — | URDF/meshes/frames absent | Supply model, then add RViz |
| Automated tests | Implemented and verified | Pure test suite passes locally | `test/` | ROS/hardware tests blocked | Run target suite |
| Experiments | Partially implemented | One-command E00--E07 collectors, analysis, and evidence indexing | `scripts/run_thesis_experiments.sh`, `tools/`, `experiments/` | ROS runtime execution pending on Ubuntu; no hardware | Execute full Ubuntu suite |
| Documentation | Implemented and verified | Requested audit documents present | `docs/` | Must track later target results | Update after each run |
