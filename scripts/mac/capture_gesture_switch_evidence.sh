#!/usr/bin/env bash
set -euo pipefail

TASK_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASK_REPO_ROOT="$(cd "${TASK_SCRIPT_DIR}/../.." && pwd)"
TASK_COMPOSE="${TASK_REPO_ROOT}/docker/ros2_humble_sim/compose.yaml"
TASK_CONTAINER="ros2_humble_sim-rviz-1"
TASK_RUN_ID="${1:-gesture_switch_$(date -u +%Y%m%dT%H%M%SZ)}"
TASK_OUTPUT="${TASK_REPO_ROOT}/experiment_results/${TASK_RUN_ID}"
TASK_CONTAINER_OUTPUT="/workspace/experiment_results/${TASK_RUN_ID}"

mkdir -p "${TASK_OUTPUT}/screenshots" "${TASK_OUTPUT}/raw"

docker compose -f "${TASK_COMPOSE}" restart rviz
sleep 8

docker exec "${TASK_CONTAINER}" bash -lc \
  "source /opt/ros/humble/setup.bash; source /workspace/.experiment_work/mac_ros2/install/setup.bash; ros2 service call /dex_hand/emergency_stop std_srvs/srv/SetBool '{data: false}'" \
  >"${TASK_OUTPUT}/raw/recovery.txt"

capture_pose() {
  local gesture="$1"
  local speed="$2"

  {
    printf 'timestamp_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf 'gesture=%s\n' "${gesture}"
    printf 'speed=%s\n' "${speed}"
    docker exec "${TASK_CONTAINER}" bash -lc \
      "source /opt/ros/humble/setup.bash; source /workspace/.experiment_work/mac_ros2/install/setup.bash; ros2 topic pub --once /dex_hand/gesture_cmd dex_hand_interfaces/msg/GestureCmd \"{gesture: ${gesture}, speed: ${speed}}\""
  } >"${TASK_OUTPUT}/raw/${gesture}_command.txt"

  sleep 3

  docker exec "${TASK_CONTAINER}" bash -lc \
    "source /opt/ros/humble/setup.bash; source /workspace/.experiment_work/mac_ros2/install/setup.bash; ros2 topic echo --once /dex_hand/status --field data" \
    >"${TASK_OUTPUT}/raw/${gesture}_status.txt"
  docker exec "${TASK_CONTAINER}" bash -lc \
    "source /opt/ros/humble/setup.bash; source /workspace/.experiment_work/mac_ros2/install/setup.bash; ros2 topic echo --once /joint_states" \
    >"${TASK_OUTPUT}/raw/${gesture}_joint_states.yaml"
  docker exec "${TASK_CONTAINER}" bash -lc \
    "python3 /workspace/tools/capture_x11.py --output '${TASK_CONTAINER_OUTPUT}/screenshots/${gesture}.png'"
}

capture_pose fist 1.0
capture_pose vgesture 1.0
capture_pose open 1.0

docker exec "${TASK_CONTAINER}" bash -lc \
  "source /opt/ros/humble/setup.bash; source /workspace/.experiment_work/mac_ros2/install/setup.bash; python3 /workspace/tools/record_gesture_switch.py --output-dir '${TASK_CONTAINER_OUTPUT}/raw'" \
  >"${TASK_OUTPUT}/raw/gesture_switch_recorder.log" 2>&1

docker logs "${TASK_CONTAINER}" >"${TASK_OUTPUT}/raw/rviz_container.log" 2>&1
docker exec "${TASK_CONTAINER}" bash -lc \
  "source /opt/ros/humble/setup.bash; source /workspace/.experiment_work/mac_ros2/install/setup.bash; ros2 param get /dex_hand_node joint_directions" \
  >"${TASK_OUTPUT}/raw/joint_directions.txt"

(
  cd "${TASK_REPO_ROOT}"
  find "experiment_results/${TASK_RUN_ID}" -type f ! -name checksums.sha256 -print0 |
    sort -z |
    xargs -0 shasum -a 256 >"experiment_results/${TASK_RUN_ID}/checksums.sha256"
)

printf '%s\n' "${TASK_OUTPUT}"
