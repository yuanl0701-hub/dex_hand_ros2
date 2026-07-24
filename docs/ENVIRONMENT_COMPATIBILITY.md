# Environment Compatibility

| Capability | Current macOS | Ubuntu/ROS 2 Humble | Hardware required |
|---|---|---|---|
| Pure driver/mock/safety tests | Supported and verified | Supported | No |
| Protocol fake-transport tests | Supported and verified | Supported | No |
| Gesture/trajectory/PID tests | Supported and verified | Supported | No |
| Ruff and mypy | Supported | Supported if installed | No |
| ROS interface generation | Blocked by environment | Required | No |
| ROS node/launch tests | Blocked by environment | Required | No |
| Serial real-driver test | Python dependency absent locally | Supported with pyserial | Yes |
| RViz/model visualization | Model missing and ROS unavailable | ROS available, model still required | No |
| FK/IK | Geometry missing | Geometry still required | No |

Detected locally on 2026-07-23: macOS 26.5.2 ARM64, system Python 3.13.9,
Anaconda pytest/ruff/mypy available, and no `ros2`, `colcon`, `rclpy`, or
`pyserial`. No `cmake` executable is available in the current shell.

The historical generated tree was built under Linux/Python 3.10 and records
successful CMake build/install commands. That result applies only to the older
artifact snapshot and is not a current ROS verification.
