#!/usr/bin/env bash
# Start the localhost browser interface for an already-running hand node.

set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
WEB_HOST="127.0.0.1"
WEB_PORT="8765"
OPEN_BROWSER="true"
WEB_ROS_DISTRO="${ROS_DISTRO:-jazzy}"

usage() {
  cat <<'EOF'
Usage: ./scripts/run_hand_web_ui.sh [options]

Options:
  --host ADDRESS    HTTP bind address (default: 127.0.0.1)
  --port PORT       HTTP port (default: 8765)
  --ros-distro NAME ROS 2 distribution (default: current environment or jazzy)
  --no-browser      Do not open the default browser automatically
  -h, --help        Show this help

The control/Isaac Sim node must already be running. Binding to a non-loopback
address exposes an unauthenticated ROS control interface to that network.
EOF
}

while (($#)); do
  case "$1" in
    --host)
      [[ $# -ge 2 ]] || { echo "Missing value for --host" >&2; exit 2; }
      WEB_HOST="$2"
      shift 2
      ;;
    --port)
      [[ $# -ge 2 ]] || { echo "Missing value for --port" >&2; exit 2; }
      WEB_PORT="$2"
      shift 2
      ;;
    --ros-distro)
      [[ $# -ge 2 ]] || { echo "Missing value for --ros-distro" >&2; exit 2; }
      WEB_ROS_DISTRO="$2"
      shift 2
      ;;
    --no-browser)
      OPEN_BROWSER="false"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ ! "$WEB_PORT" =~ ^[0-9]+$ ]] || ((WEB_PORT < 1 || WEB_PORT > 65535)); then
  echo "Port must be an integer between 1 and 65535." >&2
  exit 2
fi
ROS_SETUP="/opt/ros/${WEB_ROS_DISTRO}/setup.bash"
if [[ ! -f "$ROS_SETUP" ]]; then
  echo "ROS 2 setup was not found at $ROS_SETUP." >&2
  exit 2
fi
if [[ ! -f "$ROOT_DIR/install/setup.bash" ]]; then
  echo "Missing $ROOT_DIR/install/setup.bash; build the workspace first." >&2
  exit 2
fi

set +u
source "$ROS_SETUP"
source "$ROOT_DIR/install/setup.bash"
set -u

export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-0}"
export RMW_IMPLEMENTATION="${RMW_IMPLEMENTATION:-rmw_fastrtps_cpp}"

exec ros2 run dex_hand_ros2 hand_web_ui --ros-args \
  -p web_host:="$WEB_HOST" \
  -p web_port:="$WEB_PORT" \
  -p open_browser:="$OPEN_BROWSER"
