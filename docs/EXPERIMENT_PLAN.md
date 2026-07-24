# Experiment Plan

No results are claimed here.

| Experiment | Prerequisite | Raw fields | Analysis | Current readiness |
|---|---|---|---|---|
| Reproducible Humble build | Ubuntu 22.04 and ROS 2 Humble | environment, commands, exit status, duration | three-run success/failure table | Collector implemented; post-split run pending |
| Automated verification | Built workspace | pytest/colcon logs and exit status | test counts and failures | Implemented; Ubuntu execution pending |
| ROS functional matrix | Fake node and generated interfaces | case, expected, observed, elapsed time | pass/fail matrix | Collector implemented; Ubuntu execution pending |
| Quintic boundary verification | Pure trajectory module | time, position, velocity, acceleration, jerk | boundary residuals and extrema | Collector implemented and locally smoke-tested |
| Deterministic PID response | PID algorithm with explicit fixed sample time | time, target, state, effort, gains | convergence, error, iterations, saturation | Collector implemented and locally smoke-tested |
| ROS message frequency/jitter/QoS | ROS 2 target | monotonic send/receive timestamps and matches | rate, period, jitter, loss; reliable vs best-effort | Collector implemented; Ubuntu execution pending |
| Software safety timing | ROS 2 fake node | monotonic trigger/status timestamps | watchdog and service-to-state latency | Collector implemented; Ubuntu execution pending |
| Process resource use | Linux fake node process | CPU, RSS, threads, time | idle/load descriptive statistics | Collector implemented; Ubuntu execution pending |
| Serial command-response latency | Hardware and protocol validation | monotonic request/response timestamps, packet result | latency distribution/timeouts | Blocked by environment |
| Hardware trajectory tracking | Safe hardware procedure | commanded/measured normalized positions and timestamps | RMS/max error | Blocked by missing information |
| FK/IK consistency | Verified model | pose, joint vector, iterations, error, runtime | FK–IK–FK error | Blocked by missing information |

All run bundles include environment and algorithm metadata, exact logs, a
status table, an evidence index, and SHA-256 checksums. `algorithm_output`,
`environment_record`, and `ros2_virtual_backend_measurement` must never be
presented as hardware measurements. Empty or failed result directories do not
constitute successful experiment evidence.
