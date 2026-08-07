# Environment Compatibility

| Capability | Current macOS | Ubuntu/ROS 2 Humble | Hardware required |
|---|---|---|---|
| Pure driver/mock/safety tests | Supported and verified | Supported | No |
| Protocol fake-transport tests | Supported and verified | Supported | No |
| Gesture/trajectory/PID tests | Supported and verified | Supported | No |
| Ruff and mypy | Supported | Supported if installed | No |
| ROS interface generation | Verified through ARM64 Humble Docker | Supported and verified in container | No |
| ROS node/launch tests | Verified through ARM64 Humble Docker | Supported and verified in container | No |
| MPD20 launch/config installation | Verified through ARM64 Humble Docker | Supported | No |
| Serial real-driver test | No local physical serial device | Supported with pyserial | Yes |
| RViz/model visualization | Model missing and ROS unavailable | ROS available, model still required | No |
| FK/IK | Geometry missing | Geometry still required | No |

The native macOS shell has no ROS 2 installation. The bundled ARM64 Ubuntu
22.04/ROS 2 Humble Docker workflow builds both packages, runs package tests and
parses the MPD20 launch arguments. Physical serial verification must still run
on the Ubuntu deployment computer connected to the hand.

The historical generated tree was built under Linux/Python 3.10 and records
successful CMake build/install commands. That result applies only to the older
artifact snapshot and is not a current ROS verification.
