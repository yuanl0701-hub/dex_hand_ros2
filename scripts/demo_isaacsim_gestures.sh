#!/usr/bin/env bash
# Publish the complete gesture catalogue while Isaac Sim is running.

set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
INTERVAL_SECONDS="${GESTURE_INTERVAL_SECONDS:-2.0}"
SPEED="${GESTURE_SPEED:-1.0}"

if [[ ! -f /opt/ros/humble/setup.bash ]]; then
  echo "ROS 2 Humble was not found at /opt/ros/humble/setup.bash." >&2
  exit 2
fi
if [[ ! -f "$ROOT_DIR/install/setup.bash" ]]; then
  echo "Missing $ROOT_DIR/install/setup.bash; start run_isaacsim.sh first." >&2
  exit 2
fi

set +u
source /opt/ros/humble/setup.bash
source "$ROOT_DIR/install/setup.bash"
set -u

if (($#)); then
  GESTURES=("$@")
else
  GESTURES=(
    open
    fist
    vgesture
    pinch_two
    pinch_three
    pinch_side
    point
    thumbs_up
    gesture_666
    open
  )
fi

if ! ros2 node list 2>/dev/null | grep -qx '/dex_hand_node'; then
  echo "/dex_hand_node is not running. Start ./scripts/run_isaacsim.sh first." >&2
  exit 1
fi

for gesture in "${GESTURES[@]}"; do
  echo "Publishing gesture: $gesture (speed=$SPEED)"
  ros2 topic pub --once \
    /dex_hand/gesture_cmd \
    dex_hand_interfaces/msg/GestureCmd \
    "{gesture: '${gesture}', speed: ${SPEED}}"
  sleep "$INTERVAL_SECONDS"
done

echo "Gesture sequence completed."
