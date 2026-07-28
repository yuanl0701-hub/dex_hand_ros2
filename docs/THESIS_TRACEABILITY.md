# Thesis Traceability

The LaTeX template currently contains no Chapters 3–7. “Section” below denotes
the recommended future chapter role, not existing prose.

| Thesis Section | Supported Claim | Code Evidence | Test Evidence | Required Figure | Required Experiment | Readiness |
|---|---|---|---|---|---|---|
| Chapter 3: architecture | Layered ROS/core/driver design exists | `controller.py`, `driver.py`, `hand_node.py` | Pure core suite | Package and command-flow diagrams | ROS fake launch | Partially ready |
| Chapter 3: ROS interfaces | Compatibility topics/services are defined | `src/dex_hand_interfaces/msg/`, `srv/`, `hand_node.py` | None locally | Node topology | ROS interface/launch test | Blocked by environment |
| Chapter 4: communication | Strict Modbus/Feetech validation is implemented | `protocols.py`, `real_drivers.py` | Fake transport tests | Packet diagrams | Hardware packet verification | Partially ready |
| Chapter 4: safety | Limits, watchdog, and latched software stop exist | `safety.py` | Safety unit tests | Safety state diagram | Hardware stop-response test | Partially ready |
| Chapter 5: gesture control | A validated nine-preset library retains the three legacy vectors and supports precision, pointing, and communication poses | `gestures.py`, `gestures.yaml`, launch files | Nine-entry configuration, backward-compatibility tests, isolated Humble listing and `pinch_two` target response | Expanded USD gesture catalogue and gesture data-flow figure | Legacy three-preset ROS sequence retained; expanded catalogue loaded and one new preset exercised in an isolated ROS domain | Implemented and container-verified; full nine-preset sequence and hardware calibration remain pending |
| Chapter 5: trajectories | Quintic multi-axis generation exists | `trajectory.py` | Boundary and sampling tests | Position/velocity/acceleration/jerk plots | Algorithm export | Ready for technical drafting |
| Chapter 5: PID | Deterministic saturated PID exists | `pid.py`, `controller.py` | PID/mock convergence tests | Block/control-response figures | Mock then hardware response | Partially ready |
| Chapter 6: kinematics | No supportable claim | None | None | Finger-chain diagram | FK/IK validation | Blocked by missing information |
| Chapter 6: visualization | No supportable claim | None | None | RViz/TF figure | RViz launch | Blocked by missing information |
| Chapter 7: evaluation | Test methodology and schemas exist | `experiment.py`, `EXPERIMENT_PLAN.md` | Export test | Result plots after execution | ROS/hardware experiments | Blocked by experiments |
