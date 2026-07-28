#!/usr/bin/env bash
set -eo pipefail

source /opt/ros/humble/setup.bash
source /workspace/.experiment_work/mac_ros2/install/setup.bash
set -u

mkdir -p /tmp/fluxbox
Xvfb :1 -screen 0 1600x1000x24 -ac +extension GLX +render -noreset &
XVFB_PID=$!
sleep 2
fluxbox -display :1 > /tmp/fluxbox/fluxbox.log 2>&1 &
x11vnc -display :1 -forever -shared -nopw -rfbport 5900 \
  > /tmp/fluxbox/x11vnc.log 2>&1 &
websockify --web=/usr/share/novnc 6080 localhost:5900 \
  > /tmp/fluxbox/novnc.log 2>&1 &

cleanup() {
  jobs -pr | xargs -r kill
  wait || true
}
trap cleanup EXIT INT TERM

ros2 launch dex_hand_ros2 simulated_hand.launch.py use_rviz:=true &
LAUNCH_PID=$!
wait "$LAUNCH_PID"
kill "$XVFB_PID" 2>/dev/null || true
