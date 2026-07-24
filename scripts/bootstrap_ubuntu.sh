#!/usr/bin/env bash
# Install the non-hardware dependencies used by the thesis experiment suite.

set -euo pipefail

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "This bootstrap script supports Ubuntu Linux only." >&2
  exit 2
fi
if [[ ! -f /opt/ros/humble/setup.bash ]]; then
  echo "ROS 2 Humble was not found at /opt/ros/humble/setup.bash." >&2
  exit 2
fi

sudo apt update
sudo apt install -y \
  python3-colcon-common-extensions \
  python3-pytest \
  python3-rosdep \
  python3-serial \
  ros-humble-rmw-fastrtps-cpp \
  stress-ng

if [[ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]]; then
  sudo rosdep init
fi
rosdep update

echo "Ubuntu experiment dependencies are ready."
