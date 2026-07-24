# Source Recovery Provenance

- Parent repository baseline: `665395d175882320303474bc9ff659c792371cf2`.
- Broken gitlink: `src/dex_hand_ros2`.
- Required nested commit: `7424eae0d385ee0b16c2331a339872c0d33d08cf`.
- Authoritative remote: `git@github.com:yuanl0701-hub/dex_hand_ros2.git`.
- Recovery check: an exact-SHA fetch succeeded and resolved to the required
  commit.

The recovered tree contained `package.xml`, `setup.py`, `setup.cfg`,
`pyproject.toml`, two node files, two message paths, and an empty
`hand_driver.py`. `GestureCmd.msg` was also empty. The generated `build/`,
`install/`, and `log/` directories preserved evidence of later uncommitted
work, but were not used as an authoritative replacement. Compatibility names
from those artifacts were retained while implementation was rebuilt on the
verified commit.

Generated artifacts recorded historical Linux paths under
`/home/airs01/yl/ros2_ws_v1.0` and successful historical CMake build/install
commands on 2026-06-15. They do not establish that the current source passes a
ROS 2 build.
