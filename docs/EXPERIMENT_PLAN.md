# Experiment Plan

No results are claimed here.

| Experiment | Prerequisite | Raw fields | Analysis | Current readiness |
|---|---|---|---|---|
| Quintic boundary verification | Pure trajectory module | time, position, velocity, acceleration, jerk | Boundary residuals and extrema | Implemented and verified |
| Mock PID response | Mock backend and fixed sample time | time, target, state, effort, gains | Rise/settling/overshoot/steady-state error | Planned |
| ROS message frequency/jitter | ROS 2 target | monotonic send/receive timestamps, sequence | rate, period, jitter | Blocked by environment |
| Serial command-response latency | Hardware and protocol validation | monotonic request/response timestamps, packet result | latency distribution/timeouts | Blocked by environment |
| Hardware trajectory tracking | Safe hardware procedure | commanded/measured normalized positions and timestamps | RMS/max error | Blocked by missing information |
| FK/IK consistency | Verified model | pose, joint vector, iterations, error, runtime | FK–IK–FK error | Blocked by missing information |

All datasets must include a JSON sidecar with data kind, units, configuration,
UTC creation time, and Git commit. `algorithm_output` and `mock_fixture` must
never be presented as hardware measurements. Empty result directories do not
constitute experiment evidence.
