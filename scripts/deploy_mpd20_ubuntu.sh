#!/usr/bin/env bash
# Build, preflight and launch the physical MPD20 hand on Ubuntu 22.04/Humble.

set -euo pipefail

TASK_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASK_REPO_ROOT="$(cd "${TASK_SCRIPT_DIR}/.." && pwd)"
TASK_PORT=""
TASK_BAUDRATE="115200"
TASK_IDS="1,2,3,4,5,6"
TASK_CONFIG="${TASK_REPO_ROOT}/src/dex_hand_ros2/config/deployments/mpd20_hand.example.yaml"
TASK_GESTURES="${TASK_REPO_ROOT}/src/dex_hand_ros2/config/hand_models/mpd20_six_axis/commissioning_gestures.json"
TASK_MOTION="false"
TASK_SKIP_BUILD="false"

usage() {
  echo "Usage: $0 --port /dev/ttyUSB0 [options]"
  echo "  --ids 1,2,3,4,5,6      configured Modbus IDs"
  echo "  --baudrate 115200       serial baud rate"
  echo "  --config FILE           physical-hand ROS parameter file"
  echo "  --gestures FILE         hardware-calibrated gesture file"
  echo "  --enable-motion         allow position-register writes"
  echo "  --skip-build            reuse the existing install tree"
}

while (($#)); do
  case "$1" in
    --port)
      TASK_PORT="${2:-}"
      shift 2
      ;;
    --ids)
      TASK_IDS="${2:-}"
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
    --enable-motion)
      TASK_MOTION="true"
      shift
      ;;
    --skip-build)
      TASK_SKIP_BUILD="true"
      shift
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

if [[ -z "${TASK_PORT}" ]]; then
  echo "--port is required" >&2
  usage >&2
  exit 2
fi
if [[ "$(uname -s)" != "Linux" ]]; then
  echo "Physical deployment is supported on Ubuntu Linux, not $(uname -s)." >&2
  exit 2
fi
if [[ ! -f /opt/ros/humble/setup.bash ]]; then
  echo "ROS 2 Humble was not found at /opt/ros/humble/setup.bash." >&2
  exit 2
fi
if [[ ! -e "${TASK_PORT}" ]]; then
  echo "Serial device does not exist: ${TASK_PORT}" >&2
  exit 2
fi
if [[ ! -r "${TASK_PORT}" || ! -w "${TASK_PORT}" ]]; then
  echo "Serial device is not readable/writable by the current user: ${TASK_PORT}" >&2
  echo "Add the user to dialout, log out/in, and retry." >&2
  exit 2
fi
if [[ ! -f "${TASK_CONFIG}" || ! -f "${TASK_GESTURES}" ]]; then
  echo "Config or gesture file does not exist." >&2
  exit 2
fi

# shellcheck disable=SC1091
source /opt/ros/humble/setup.bash
cd "${TASK_REPO_ROOT}"

if [[ "${TASK_SKIP_BUILD}" != "true" ]]; then
  command -v colcon >/dev/null || {
    echo "colcon is not installed." >&2
    exit 2
  }
  colcon build --symlink-install --packages-up-to dex_hand_ros2
fi
if [[ ! -f "${TASK_REPO_ROOT}/install/setup.bash" ]]; then
  echo "install/setup.bash is missing; run without --skip-build first." >&2
  exit 2
fi
# shellcheck disable=SC1091
source "${TASK_REPO_ROOT}/install/setup.bash"

ros2 run dex_hand_ros2 mpd20_preflight \
  --port "${TASK_PORT}" \
  --baudrate "${TASK_BAUDRATE}" \
  --ids "${TASK_IDS}"

exec ros2 launch dex_hand_ros2 mpd20_hand.launch.py \
  deployment_config:="${TASK_CONFIG}" \
  gesture_file:="${TASK_GESTURES}" \
  serial_port:="${TASK_PORT}" \
  baudrate:="${TASK_BAUDRATE}" \
  motion_enabled:="${TASK_MOTION}"
