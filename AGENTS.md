# Project Agent Guide

## Purpose

This repository implements a ROS 2 control system for a six-motor dexterous
hand. It includes hardware-independent control algorithms, serial driver
adapters, a deterministic mock backend, ROS 2 nodes, tests, experiment
tooling, and thesis traceability documentation.

## Supported environments

- Pure Python core and unit tests: Python 3.10 or newer on macOS or Linux.
- ROS 2 package: Ubuntu 22.04 with ROS 2 Humble is the target runtime.
- Real drivers: require the matching serial device and verified device
  protocol. Hardware tests are never implied by mock tests.

## Package structure

- `src/dex_hand_ros2/dex_hand_ros2/`: Python implementation.
- `src/dex_hand_ros2/msg/`, `srv/`: compatibility ROS interfaces.
- `src/dex_hand_ros2/config/`, `launch/`: runtime configuration.
- `src/dex_hand_ros2/test/`: pure and ROS-aware tests.
- `docs/`: audits, plans, evidence logs, and thesis traceability.

## Commands

Pure Python:

```bash
python3 -m compileall src/dex_hand_ros2/dex_hand_ros2
python3 -m pytest -q src/dex_hand_ros2/test
ruff check src/dex_hand_ros2/dex_hand_ros2 src/dex_hand_ros2/test
mypy src/dex_hand_ros2/dex_hand_ros2
```

Target ROS 2 environment:

```bash
rosdep install --from-paths src --ignore-src -r -y --rosdistro humble
colcon build --symlink-install --packages-select dex_hand_ros2
source install/setup.bash
colcon test --packages-select dex_hand_ros2
colcon test-result --verbose
```

## Conventions

- Use type annotations and docstrings for public Python APIs.
- Keep algorithms independent of ROS 2 and physical I/O.
- Validate all external values, dimensions, identifiers, and finite numbers.
- Units in the current control core are normalized percent (`0..100`), not
  radians. Logical names such as `motor_1` are not anatomical joint names.
- Preserve existing ROS names and wire shapes unless a documented migration
  is approved.

## Forbidden operations

- Do not use Isaac Sim or add Isaac Sim dependencies or assets.
- Do not guess link geometry, joint axes, physical limits, register maps, or
  experimental results.
- Do not run destructive Git commands, rewrite history, commit, or push unless
  explicitly requested.
- Do not require real hardware by default; the mock backend is the safe default.

## Academic integrity and status

Never fabricate measurements, figures, screenshots, references, test results,
or implementation claims. Use only: Implemented and verified; Implemented but
not verified; Partially implemented; Placeholder only; Planned; Not
implemented; Cannot be determined; Blocked by environment; Blocked by missing
information.

## Documentation

After each milestone, record exact commands and results in
`docs/CHANGELOG_IMPLEMENTATION.md`, then update implementation status and
thesis traceability. Historical logs are evidence of historical execution only.
