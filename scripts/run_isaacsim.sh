#!/usr/bin/env bash
# Build the ROS 2 workspace, expand the Xacro, and start the Isaac Sim bridge.

set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
ISAAC_DIR="${ISAAC_SIM_PATH:-${HOME}/isaacsim}"
HEADLESS=false
SKIP_BUILD=false
SAVE_STAGE=""
COMMAND_TOPIC="/dex_hand/joint_command"
STATE_TOPIC="/isaac_joint_states"

usage() {
  cat <<'EOF'
Usage: ./scripts/run_isaacsim.sh [options]

Options:
  --isaac-sim-path PATH  Isaac Sim 4.5 directory containing python.sh
  --headless             Run Isaac Sim without a viewport
  --skip-build           Reuse the existing ROS 2 install directory
  --save-stage PATH      Export the prepared stage to a USD file
  --help                 Show this help

The ISAAC_SIM_PATH environment variable is used when --isaac-sim-path is not
given. Its default is ~/isaacsim.
EOF
}

while (($#)); do
  case "$1" in
    --isaac-sim-path)
      [[ $# -ge 2 ]] || { echo "Missing value for --isaac-sim-path" >&2; exit 2; }
      ISAAC_DIR="$2"
      shift 2
      ;;
    --headless)
      HEADLESS=true
      shift
      ;;
    --skip-build)
      SKIP_BUILD=true
      shift
      ;;
    --save-stage)
      [[ $# -ge 2 ]] || { echo "Missing value for --save-stage" >&2; exit 2; }
      SAVE_STAGE="$2"
      shift 2
      ;;
    --help|-h)
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

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "Isaac Sim 4.5 integration must be run on the Ubuntu workstation." >&2
  exit 2
fi
if [[ ! -f /opt/ros/humble/setup.bash ]]; then
  echo "ROS 2 Humble was not found at /opt/ros/humble/setup.bash." >&2
  exit 2
fi
if [[ ! -x "${ISAAC_DIR}/python.sh" ]]; then
  echo "Isaac Sim python.sh was not found at: ${ISAAC_DIR}/python.sh" >&2
  echo "Set ISAAC_SIM_PATH or pass --isaac-sim-path." >&2
  exit 2
fi
if ! command -v setsid >/dev/null; then
  echo "The required setsid command is unavailable (install util-linux)." >&2
  exit 2
fi

cd "$ROOT_DIR"
set +u
source /opt/ros/humble/setup.bash
set -u
export RMW_IMPLEMENTATION="${RMW_IMPLEMENTATION:-rmw_fastrtps_cpp}"

if [[ "$SKIP_BUILD" == false ]]; then
  rosdep install \
    --from-paths src \
    --ignore-src \
    --rosdistro humble \
    -r -y
  colcon build \
    --symlink-install \
    --packages-up-to dex_hand_ros2
fi

if [[ ! -f "$ROOT_DIR/install/setup.bash" ]]; then
  echo "Missing install/setup.bash; run without --skip-build first." >&2
  exit 2
fi
set +u
source "$ROOT_DIR/install/setup.bash"
set -u

WORK_DIR="$ROOT_DIR/.isaacsim"
GENERATED_DIR="$WORK_DIR/generated"
LOG_DIR="$WORK_DIR/logs"
mkdir -p "$GENERATED_DIR" "$LOG_DIR"

XACRO_PATH="$ROOT_DIR/src/dex_hand_ros2/urdf/virtual_dex_hand.urdf.xacro"
URDF_PATH="$GENERATED_DIR/virtual_dex_hand.urdf"
xacro "$XACRO_PATH" -o "$URDF_PATH"

ROS_LOG="$LOG_DIR/ros_controller.log"
setsid ros2 launch dex_hand_ros2 isaac_sim.launch.py \
  joint_command_topic:="$COMMAND_TOPIC" \
  >"$ROS_LOG" 2>&1 &
ROS_PID=$!

cleanup() {
  local exit_code=$?
  trap - EXIT INT TERM
  if kill -0 -- "-$ROS_PID" 2>/dev/null; then
    kill -INT -- "-$ROS_PID" 2>/dev/null || true
    for _ in {1..30}; do
      kill -0 -- "-$ROS_PID" 2>/dev/null || break
      sleep 0.1
    done
  fi
  if kill -0 -- "-$ROS_PID" 2>/dev/null; then
    kill -TERM -- "-$ROS_PID" 2>/dev/null || true
    for _ in {1..20}; do
      kill -0 -- "-$ROS_PID" 2>/dev/null || break
      sleep 0.1
    done
  fi
  if kill -0 -- "-$ROS_PID" 2>/dev/null; then
    echo "ROS launch did not stop after SIGTERM; forcing its process group to exit." >&2
    kill -KILL -- "-$ROS_PID" 2>/dev/null || true
  fi
  if [[ -n "${ROS_PID:-}" ]]; then
    wait "$ROS_PID" 2>/dev/null || true
  fi
  exit "$exit_code"
}
trap cleanup EXIT INT TERM

for _ in {1..40}; do
  if ros2 node list 2>/dev/null | grep -qx '/dex_hand_node'; then
    break
  fi
  if ! kill -0 "$ROS_PID" 2>/dev/null; then
    echo "ROS controller exited during startup. See: $ROS_LOG" >&2
    exit 1
  fi
  sleep 0.25
done

if ! ros2 node list 2>/dev/null | grep -qx '/dex_hand_node'; then
  echo "ROS controller did not become ready. See: $ROS_LOG" >&2
  exit 1
fi

ISAAC_ARGS=(
  "$ROOT_DIR/isaacsim/launch_dex_hand.py"
  --urdf "$URDF_PATH"
  --command-topic "$COMMAND_TOPIC"
  --state-topic "$STATE_TOPIC"
)
if [[ "$HEADLESS" == true ]]; then
  ISAAC_ARGS+=(--headless)
fi
if [[ -n "$SAVE_STAGE" ]]; then
  ISAAC_ARGS+=(--save-stage "$SAVE_STAGE")
fi

echo "ROS controller is ready (log: $ROS_LOG)"
echo "Starting Isaac Sim from: $ISAAC_DIR"
echo "Gesture command topic: /dex_hand/gesture_cmd"
echo "Isaac command topic:   $COMMAND_TOPIC"
echo "Isaac state topic:     $STATE_TOPIC"

"${ISAAC_DIR}/python.sh" "${ISAAC_ARGS[@]}"
