#!/usr/bin/env bash
# Start the partially commissioned MPD20 hand on Ubuntu with ROS 2 Jazzy.

set -euo pipefail

TASK_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASK_REPO_ROOT="$(cd "${TASK_SCRIPT_DIR}/.." && pwd)"
TASK_ROS_DISTRO="jazzy"
TASK_PORT="/dev/ttyUSB0"
TASK_BAUDRATE="115200"
TASK_CONFIG="${TASK_REPO_ROOT}/src/dex_hand_ros2/config/deployments/lab_hand_001.yaml"
TASK_GESTURES="${TASK_REPO_ROOT}/src/dex_hand_ros2/config/hand_models/mpd20_six_axis/commissioning_gestures.json"
TASK_MOTION="false"
TASK_BUILD="false"

usage() {
  echo "Usage: $0 [options]"
  echo "  --enable-motion         permit physical position writes"
  echo "  --build                 rebuild dex_hand_ros2 before launch"
  echo "  --port DEVICE           serial port (default: /dev/ttyUSB0)"
  echo "  --baudrate RATE         serial baud rate (default: 115200)"
  echo "  --config FILE           per-hand deployment YAML"
  echo "  --gestures FILE         physical gesture JSON"
  echo "  --ros-distro NAME       installed ROS 2 distro (default: jazzy)"
}

while (($#)); do
  case "$1" in
    --enable-motion)
      TASK_MOTION="true"
      shift
      ;;
    --build)
      TASK_BUILD="true"
      shift
      ;;
    --port)
      TASK_PORT="${2:-}"
      shift 2
      ;;
    --baudrate)
      TASK_BAUDRATE="${2:-}"
      shift 2
      ;;
    --config)
      TASK_CONFIG="${2:-}"
      shift 2
      ;;
    --gestures)
      TASK_GESTURES="${2:-}"
      shift 2
      ;;
    --ros-distro)
      TASK_ROS_DISTRO="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

TASK_ROS_SETUP="/opt/ros/${TASK_ROS_DISTRO}/setup.bash"

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "Physical MPD20 launch requires Linux." >&2
  exit 2
fi
if [[ ! -f "${TASK_ROS_SETUP}" ]]; then
  echo "ROS 2 setup not found: ${TASK_ROS_SETUP}" >&2
  exit 2
fi
if [[ ! -e "${TASK_PORT}" ]]; then
  echo "Serial device does not exist: ${TASK_PORT}" >&2
  exit 2
fi
if [[ ! -r "${TASK_PORT}" || ! -w "${TASK_PORT}" ]]; then
  echo "Serial device is not readable/writable: ${TASK_PORT}" >&2
  echo "Add the user to dialout, log out/in, and retry." >&2
  exit 2
fi
if [[ ! -f "${TASK_CONFIG}" ]]; then
  echo "Deployment config not found: ${TASK_CONFIG}" >&2
  echo "Copy mpd20_hand.example.yaml to lab_hand_001.yaml and calibrate it first." >&2
  exit 2
fi
if [[ ! -f "${TASK_GESTURES}" ]]; then
  echo "Gesture file not found: ${TASK_GESTURES}" >&2
  exit 2
fi
if command -v fuser >/dev/null && fuser "${TASK_PORT}" >/dev/null 2>&1; then
  echo "Serial device is already in use: ${TASK_PORT}" >&2
  fuser -v "${TASK_PORT}" >&2 || true
  exit 2
fi

# ROS 2 generated setup files are not guaranteed to be safe under `set -u`:
# they can read optional environment variables before assigning defaults.
# Keep nounset enabled for this script, but suspend it while sourcing them.
set +u
# shellcheck disable=SC1090
source "${TASK_ROS_SETUP}"
set -u
cd "${TASK_REPO_ROOT}"

if [[ "${TASK_BUILD}" == "true" || ! -f install/setup.bash ]]; then
  command -v colcon >/dev/null || {
    echo "colcon is not installed." >&2
    exit 2
  }
  colcon build --symlink-install --packages-up-to dex_hand_ros2
fi

if [[ ! -f install/setup.bash ]]; then
  echo "install/setup.bash is missing; rerun with --build." >&2
  exit 2
fi

set +u
# shellcheck disable=SC1091
source install/setup.bash
set -u

echo "Starting MPD20 hand"
echo "  ROS distro: ${TASK_ROS_DISTRO}"
echo "  serial: ${TASK_PORT} @ ${TASK_BAUDRATE}"
echo "  config: ${TASK_CONFIG}"
echo "  gestures: ${TASK_GESTURES}"
echo "  physical motion enabled: ${TASK_MOTION}"

exec ros2 launch dex_hand_ros2 mpd20_hand.launch.py \
  deployment_config:="${TASK_CONFIG}" \
  gesture_file:="${TASK_GESTURES}" \
  serial_port:="${TASK_PORT}" \
  baudrate:="${TASK_BAUDRATE}" \
  motion_enabled:="${TASK_MOTION}"
