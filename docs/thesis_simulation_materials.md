# Thesis simulation materials

## Scope

This implementation is a **lightweight kinematic and actuator-level,
software-in-the-loop simulation** with a **parameterized virtual dexterous
hand**. It is not a digital twin, contact simulator, hardware calibration, or
evidence of physical actuator performance. `MockMotorDriver` remains the
instantaneous deterministic test double; `SimulatedMotorDriver` is a separate
dynamic backend.

## Actuator model

For motor \(i\), the unsaturated plant is
\(\dot q_i^*=(q_{i,target}-q_i)/\tau\). Desired velocity is clamped to
\(\pm v_{max}\), its per-step change to \(\pm a_{max}\Delta t\), and
semi-implicit Euler integration computes
\(q_{k+1}=\mathrm{clip}(q_k+v_{k+1}\Delta t,q_{min},q_{max})\).

Defaults are \(\tau=0.20\) s, \(v_{max}=250\) normalized %/s,
\(a_{max}=1500\) normalized %/s², 100 Hz, zero delay/deadband/noise, and seed
6048. `step(dt)` owns time advancement and creates no background thread.
Position, velocity and acceleration are modeled; effort is unavailable.

Optional explicit faults/non-idealities include command delay/drop, noise,
deadband, stuck/disconnected/stale feedback, bias, reduced velocity, limit hit
and logical over-temperature. They are disabled by default.

## Mapping, URDF and TF

Normalized positions map as
\(\theta=\theta_{min}+f(\theta_{max}-\theta_{min})\), where
\(f=(u-u_{min})/(u_{max}-u_{min})\), reversed for `direction=-1`, then scaled
and offset. The YAML uses `motor_1_joint` through `motor_6_joint`; it makes no
anatomical claim.

The Xacro uses an assumed 90 x 75 x 18 mm palm-like box, five generic
digit-like links, and one additional generic link. All dimensions, axes and
limits are nominal visualization assumptions. `dex_hand_node` publishes
`JointState` names, positions and velocities (empty effort);
`robot_state_publisher` derives TF.

## Nominal forward kinematics

The experiment-only planar finger uses lengths (0.045, 0.030, 0.022) m and
mimic ratios (1.0, 0.7, 0.5). With cumulative angles
\(\phi_j=\sum_{k=1}^{j}r_k\theta\),
\(x=\sum l_j\cos\phi_j\), \(y=\sum l_j\sin\phi_j\).
This supports nominal fingertip paths/workspace only; it is not a calibrated
physical model.

## Experiments, metrics and provenance

The accepted run is `experiment_results/20260725_170324`. It contains:

- 25, 50 and 100 normalized-% step responses;
- direct versus quintic 0--100 motion;
- `open_pose`, `pose_a`, and `closed_pose` synchronized transitions;
- open-loop versus position-command PID (not torque/current PID);
- input/watchdog/emergency-stop/stuck/feedback-unavailable cases;
- 241 nominal workspace samples over 0--1.2 rad.

Rise time is first entry above 90% amplitude. Settling time is first entry
after which all samples stay within max(2% amplitude, 0.2 normalized %).
Overshoot is directed peak excess divided by amplitude; steady-state error is
absolute final error.

Raw CSV generates 12 figure families: step response, target/actual,
velocity/acceleration, direct/quintic, jerk, PID response/error, gesture
transition, fingertip path/workspace, fault response and timeline. Processed
CSV generates step, trajectory, PID and safety tables. Each figure is exported
as PDF, SVG and PNG.

## Thesis recommendations and claim boundary

- Chapter 3: simulated backend beside mock/physical adapters; JointState/TF
  flow and virtual model.
- Chapter 4: explicit stepping, locking, mapping, ROS timer and reset services.
- Chapter 5: plant equation, mapping, quintic transitions, nominal kinematics
  and position-command PID.
- Chapter 6: deterministic software-in-the-loop methodology and metrics.
- Chapter 7: only regenerated results, always labeled simulated.
- Chapter 8: claim lightweight simulation implementation; list physical
  calibration, contact dynamics and hardware comparison as future work.

The title *Design and Implementation of a ROS 2-Based Dexterous Hand
Simulation Control System* is now better supported, but ROS runtime evidence is
still required on Ubuntu 22.04/Humble.

Pure-Python model/mapping tests and simulation experiments are verified.
ROS 2 Humble ARM64 build/test, JointState, TF, rosbag, online fault service,
RViz rendering and clean shutdown were runtime-verified in Docker on the
current Mac (`mac_ros2_20260725T103359Z`). This supports software-in-the-loop
and containerized ROS integration claims, not native macOS ROS, physical
geometry, force, torque, contact, temperature, hard real-time or hardware
performance claims.
