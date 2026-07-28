# Simulation implementation audit

Audit date: 2026-07-25. This is the Phase 1 baseline for the lightweight
software-in-the-loop simulator.

## Verified from source

- `GenericMotorDriver` is a synchronous, normalized-percent (`0..100` by
  default) interface. Its public command names are `set_single_position` and
  `set_multiple_positions`; reads return a value or `None`.
- `MockMotorDriver` is thread-safe, deterministic, and changes its stored
  position immediately. Existing tests depend on that behaviour.
- `HandController` composes a driver, `GestureLibrary`, `SafetyController`,
  synchronized quintic trajectories, and one `PIDController` per logical
  motor.
- Safety validates finite position/rate limits and provides watchdog,
  emergency-stop, recovery, fault, and shutdown states.
- ROS interfaces include the existing gesture, direct-position, PID-position,
  PID-configuration and motor-state topics; gesture and emergency-stop
  services; configuration parameters; and the `dex_hand_interfaces` messages
  and services inventoried in `docs/ROS2_INTERFACE_INVENTORY.md`.
- The configured identifiers are six logical IDs `(1,2,3,4,5,6)`. Source
  comments explicitly state that they are not anatomical joint names.
- No URDF, Xacro, mesh, `robot_description`, `/joint_states`, or TF publisher
  existed at this audit baseline.
- Pure-Python tests cover the mock driver, protocols, real-driver adapters,
  controller, gestures, trajectory, PID, safety, and experiment utilities.
- Thesis Chapters 5--7 describe algorithm-only tests and explicitly state that
  validated kinematics and motor-to-joint calibration are absent.

## Inferred but not verified

- Legacy gesture names (`open`, `fist`, `vgesture`) suggest intended hand
  postures, but do not establish which motor actuates which anatomical joint.
- Real-driver class names and protocol adapters indicate intended hardware
  families, but do not establish geometry, torque, actuator dynamics, or a
  calibrated joint mapping.

## Missing at baseline

- Dynamic actuator plant, fault injection, motor velocity/acceleration state.
- Configured motor-to-joint coordinate mapping and forward kinematics.
- Virtual robot model, JointState/TF publication, RViz and simulation launch.
- Dynamic-plant experiments and traceable simulation-specific thesis assets.
- ROS 2 runtime evidence on the current macOS host.

## Proposed simulation assumptions

- Six independent first-order position actuators in normalized-percent units,
  with explicit velocity and acceleration saturation.
- A fixed-step deterministic simulation by default; optional seeded noise and
  explicit faults are disabled by default.
- Six generic active revolute joints named `motor_1_joint` through
  `motor_6_joint`.
- A palm and five visually recognizable fingers made from primitive geometry.
  Dimensions, axes, limits, and the sixth joint placement are nominal
  visualization assumptions, not measured hardware properties.
- A planar three-link demonstration finger whose downstream two joints mimic
  the generic active coordinate at documented ratios. Its workspace is a
  nominal virtual workspace, not a calibrated physical workspace.

## Compatibility boundary

`MockMotorDriver`, existing topic/service names, message wire shapes, and
unknown-backend errors remain unchanged. The simulated backend is selected
explicitly with `driver_type=simulated`; all ROS-dependent additions remain
outside the pure-Python model and mapping modules.
