#!/usr/bin/env bash
# Build the ROS 2 workspace, expand the Xacro, and start the Isaac Sim bridge.

set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
ISAAC_DIR="${ISAAC_SIM_PATH:-${HOME}/isaacsim}"
ISAAC_PYTHON="${ISAAC_PYTHON:-}"
HEADLESS=false
SKIP_BUILD=false
SAVE_STAGE=""
COMMAND_TOPIC="/dex_hand/joint_command"
STATE_TOPIC="/isaac_joint_states"
BUNDLED_REVO2_USD="$ROOT_DIR/assets/revo2_right_hand/revo2_right_hand.usd"
REVO2_USD="${REVO2_USD_PATH:-$BUNDLED_REVO2_USD}"

usage() {
  cat <<'EOF'
Usage: ./scripts/run_isaacsim.sh [options]

Options:
  --isaac-sim-path PATH  Isaac Sim 4.5 directory containing python.sh
  --isaac-python PATH    Conda/Python executable containing Isaac Sim 4.5
  --headless             Run Isaac Sim without a viewport
  --skip-build           Reuse the existing ROS 2 install directory
  --revo2-usd PATH       Use the supplied Revo2 articulated USD instead of Xacro
  --nominal-xacro        Use the lightweight Xacro instead of bundled Revo2 USD
  --save-stage PATH      Export the prepared stage to a USD file
  --help                 Show this help

The ISAAC_SIM_PATH environment variable is used when --isaac-sim-path is not
given. Its default is ~/isaacsim. The repository's bundled Revo2 right-hand
asset is selected by default; REVO2_USD_PATH or --revo2-usd can override it.
When an active Conda environment contains the isaacsim package, its Python is
selected automatically. ISAAC_PYTHON or --isaac-python can select it explicitly.
EOF
}

while (($#)); do
  case "$1" in
    --isaac-sim-path)
      [[ $# -ge 2 ]] || { echo "Missing value for --isaac-sim-path" >&2; exit 2; }
      ISAAC_DIR="$2"
      shift 2
      ;;
    --isaac-python)
      [[ $# -ge 2 ]] || { echo "Missing value for --isaac-python" >&2; exit 2; }
      ISAAC_PYTHON="$2"
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
    --revo2-usd)
      [[ $# -ge 2 ]] || { echo "Missing value for --revo2-usd" >&2; exit 2; }
      REVO2_USD="$2"
      shift 2
      ;;
    --nominal-xacro)
      REVO2_USD=""
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
if ! command -v setsid >/dev/null; then
  echo "The required setsid command is unavailable (install util-linux)." >&2
  exit 2
fi
if [[ -n "$REVO2_USD" && ! -f "$REVO2_USD" ]]; then
  echo "Revo2 USD was not found at: $REVO2_USD" >&2
  exit 2
fi

if [[ -n "$ISAAC_PYTHON" ]]; then
  if [[ ! -x "$ISAAC_PYTHON" ]]; then
    echo "Isaac Sim Python is not executable: $ISAAC_PYTHON" >&2
    exit 2
  fi
elif [[ -n "${CONDA_PREFIX:-}" ]] \
  && command -v python >/dev/null \
  && python -c 'import importlib.util, sys; sys.exit(0 if importlib.util.find_spec("isaacsim") else 1)'; then
  ISAAC_PYTHON="$(command -v python)"
elif [[ -x "${ISAAC_DIR}/python.sh" ]]; then
  ISAAC_PYTHON="${ISAAC_DIR}/python.sh"
else
  echo "No Isaac Sim Python runtime was found." >&2
  echo "Activate its Conda environment, pass --isaac-python, or set ISAAC_SIM_PATH." >&2
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
CONFIG_FILE="$ROOT_DIR/src/dex_hand_ros2/config/hand_models/generic_six_axis/ros_parameters.yaml"

if [[ -n "$REVO2_USD" ]]; then
  CONFIG_FILE="$ROOT_DIR/src/dex_hand_ros2/config/hand_models/revo2_right/ros_parameters.yaml"
else
  xacro "$XACRO_PATH" -o "$URDF_PATH"
fi

ROS_LOG="$LOG_DIR/ros_controller.log"
setsid ros2 launch dex_hand_ros2 isaac_sim.launch.py \
  hand_model_config:="$CONFIG_FILE" \
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
  --command-topic "$COMMAND_TOPIC"
  --state-topic "$STATE_TOPIC"
)
if [[ -n "$REVO2_USD" ]]; then
  ISAAC_ARGS+=(--usd "$REVO2_USD")
else
  ISAAC_ARGS+=(--urdf "$URDF_PATH")
fi
if [[ "$HEADLESS" == true ]]; then
  ISAAC_ARGS+=(--headless)
fi
if [[ -n "$SAVE_STAGE" ]]; then
  ISAAC_ARGS+=(--save-stage "$SAVE_STAGE")
fi

echo "ROS controller is ready (log: $ROS_LOG)"
echo "Isaac Sim Python:       $ISAAC_PYTHON"
echo "Gesture command topic: /dex_hand/gesture_cmd"
echo "Isaac command topic:   $COMMAND_TOPIC"
echo "Isaac state topic:     $STATE_TOPIC"
if [[ -n "$REVO2_USD" ]]; then
  echo "Simulation asset:      Revo2 USD ($REVO2_USD)"
else
  echo "Simulation asset:      nominal Xacro/URDF"
fi

"$ISAAC_PYTHON" "${ISAAC_ARGS[@]}"
