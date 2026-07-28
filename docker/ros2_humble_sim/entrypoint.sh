#!/usr/bin/env bash
set -e
source /opt/ros/humble/setup.bash
if [[ -f /workspace/.experiment_work/mac_ros2/install/setup.bash ]]; then
  source /workspace/.experiment_work/mac_ros2/install/setup.bash
fi
exec "$@"
