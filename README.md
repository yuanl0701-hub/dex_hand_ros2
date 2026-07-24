# DEX Hand ROS 2 Control

This repository contains a safety-oriented ROS 2 control package for a
six-motor dexterous hand. The safe default is a deterministic mock backend.
Current command units are normalized percent (`0..100`); they are not radians
and the logical labels `motor_1` through `motor_6` are not anatomical joint
names.

## Verified locally

- Driver abstraction and deterministic mock backend.
- Central input validation, emergency-stop state, watchdog, and rate limits.
- Modbus RTU and Feetech packet construction/validation with fake transports.
- Validated gesture library.
- Multi-axis quintic trajectories.
- Deterministic PID control.
- CSV and metadata export for theoretical trajectory output.

These modules are covered by pure Python tests. ROS 2 node execution and real
hardware behavior are not verified on the current macOS system.

## ROS 2 target

The target is Ubuntu 22.04 with ROS 2 Humble:

```bash
cd /path/to/workspace
rosdep install --from-paths src --ignore-src -r -y --rosdistro humble
colcon build --symlink-install --packages-select dex_hand_ros2
source install/setup.bash
colcon test --packages-select dex_hand_ros2
colcon test-result --verbose
ros2 launch dex_hand_ros2 hand.launch.py driver_type:=fake
```

Real hardware must be selected explicitly:

```bash
ros2 launch dex_hand_ros2 hand.launch.py \
  driver_type:=mpd20 serial_port:=/dev/ttyUSB0
```

Do not run configuration services against powered hardware without confirming
the device model, protocol, IDs, baud rate, and recovery procedure.

## Local core tests

```bash
PYTHONPATH=src/dex_hand_ros2 pytest -q src/dex_hand_ros2/test
ruff check src/dex_hand_ros2/dex_hand_ros2 src/dex_hand_ros2/test
PYTHONPATH=src/dex_hand_ros2 mypy src/dex_hand_ros2/dex_hand_ros2 \
  --exclude '(hand_node|config_node|gesture_cli)\.py'
```

See `docs/IMPLEMENTATION_STATUS.md`, `docs/ENVIRONMENT_COMPATIBILITY.md`, and
`docs/ROS2_INTERFACE_INVENTORY.md` before making implementation or thesis
claims.
