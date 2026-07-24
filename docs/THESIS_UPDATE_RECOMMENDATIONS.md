# Thesis Update Recommendations

## Ready for technical drafting

- Quintic trajectory derivation and software design, supported by
  `trajectory.py` and its deterministic boundary tests.
- Source recovery, reproducibility, environment separation, and audit method.
- Mock-backend architecture, explicitly described as functional simulation.

## Partially ready

- Overall software architecture and ROS interface design: source exists, but
  current ROS execution still requires target verification.
- Protocol handling: packet validation is tested with fake transports, while
  physical-device semantics remain unverified.
- Safety and PID design: pure behavior is tested; hardware stop semantics and
  tuning are not.

## Blocked

- FK, IK, `JointState`, TF, ros2_control, and RViz require verified geometry and
  motor-to-joint mapping.
- Communication latency, jitter, tracking error, PID response metrics, and
  screenshots require actual experiments.
- Literature-supported claims require a separate verified reference workflow.

## Recommended figures

Use the Mermaid architecture, command-flow, feedback-flow, and safety-state
diagrams as drafting sources. Generate trajectory plots only from exported
algorithm data and label them theoretical. Do not insert mock curves as
physical experimental results.
