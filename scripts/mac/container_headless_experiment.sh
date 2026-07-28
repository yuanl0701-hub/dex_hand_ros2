#!/usr/bin/env bash
set -eo pipefail

source /opt/ros/humble/setup.bash
set -u
cd /workspace

TASK_RUN_DIR="/workspace/${DEX_HAND_EVIDENCE_REL:?DEX_HAND_EVIDENCE_REL is required}"
TASK_WORK_DIR="/workspace/.experiment_work/mac_ros2"
TASK_BUILD_DIR="${TASK_WORK_DIR}/build"
TASK_INSTALL_DIR="${TASK_WORK_DIR}/install"
TASK_LOG_DIR="${TASK_WORK_DIR}/log"
TASK_LAUNCH_PID=""
TASK_BAG_PID=""

mkdir -p \
  "${TASK_RUN_DIR}/build" \
  "${TASK_RUN_DIR}/tests" \
  "${TASK_RUN_DIR}/ros_graph" \
  "${TASK_RUN_DIR}/rosbags" \
  "${TASK_RUN_DIR}/raw" \
  "${TASK_RUN_DIR}/screenshots"

terminate_process() {
  local process_id="$1"
  if ! kill -0 -- "-${process_id}" 2>/dev/null; then
    return
  fi
  kill -INT -- "-${process_id}" 2>/dev/null || true
  for _ in $(seq 1 20); do
    if ! kill -0 -- "-${process_id}" 2>/dev/null; then
      return
    fi
    sleep 0.25
  done
  kill -TERM -- "-${process_id}" 2>/dev/null || true
}

cleanup() {
  if [[ -n "${TASK_BAG_PID}" ]]; then
    terminate_process "${TASK_BAG_PID}"
    wait "${TASK_BAG_PID}" 2>/dev/null || true
  fi
  if [[ -n "${TASK_LAUNCH_PID}" ]]; then
    terminate_process "${TASK_LAUNCH_PID}"
    wait "${TASK_LAUNCH_PID}" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

rosdep install --from-paths src --ignore-src -r -y --rosdistro humble \
  --skip-keys python3-serial \
  2>&1 | tee "${TASK_RUN_DIR}/build/rosdep.log"

colcon --log-base "${TASK_LOG_DIR}" build \
  --symlink-install \
  --packages-up-to dex_hand_ros2 \
  --build-base "${TASK_BUILD_DIR}" \
  --install-base "${TASK_INSTALL_DIR}" \
  2>&1 | tee "${TASK_RUN_DIR}/build/colcon_build.log"

set +u
source "${TASK_INSTALL_DIR}/setup.bash"
set -u

colcon --log-base "${TASK_LOG_DIR}" test \
  --packages-select dex_hand_ros2 \
  --build-base "${TASK_BUILD_DIR}" \
  --install-base "${TASK_INSTALL_DIR}" \
  2>&1 | tee "${TASK_RUN_DIR}/tests/colcon_test.log"

colcon test-result \
  --test-result-base "${TASK_BUILD_DIR}" \
  --verbose 2>&1 | tee "${TASK_RUN_DIR}/tests/colcon_test_result.log"

setsid ros2 launch dex_hand_ros2 simulated_hand.launch.py use_rviz:=false \
  > "${TASK_RUN_DIR}/ros_graph/launch.log" 2>&1 &
TASK_LAUNCH_PID=$!

for _ in $(seq 1 60); do
  if ros2 topic list 2>/dev/null | grep -qx "/joint_states"; then
    break
  fi
  sleep 0.5
done

if ! ros2 topic list | grep -qx "/joint_states"; then
  echo "/joint_states was not discovered" >&2
  exit 1
fi

ros2 node list > "${TASK_RUN_DIR}/ros_graph/nodes.txt"
ros2 topic list -t > "${TASK_RUN_DIR}/ros_graph/topics.txt"
ros2 service list -t > "${TASK_RUN_DIR}/ros_graph/services.txt"
ros2 param dump /dex_hand_node > "${TASK_RUN_DIR}/ros_graph/dex_hand_parameters.yaml"
ros2 topic echo --once /joint_states \
  > "${TASK_RUN_DIR}/raw/joint_states_once.yaml"
ros2 topic echo --once --full-length /dex_hand/status \
  > "${TASK_RUN_DIR}/raw/status_initial.yaml"
timeout 8 ros2 topic hz /joint_states \
  > "${TASK_RUN_DIR}/raw/joint_states_frequency.txt" 2>&1 || true
timeout 5 ros2 run tf2_ros tf2_echo base_link motor_1_link \
  > "${TASK_RUN_DIR}/raw/tf_base_to_motor_1.txt" 2>&1 || true

setsid ros2 bag record \
  -o "${TASK_RUN_DIR}/rosbags/sim_session" \
  /joint_states /tf /tf_static /dex_hand/status /dex_hand/motor_state \
  > "${TASK_RUN_DIR}/rosbags/record.log" 2>&1 &
TASK_BAG_PID=$!
sleep 2

for TASK_GESTURE in open fist vgesture; do
  ros2 topic pub --once /dex_hand/gesture_cmd dex_hand_interfaces/msg/GestureCmd \
    "{gesture: ${TASK_GESTURE}, speed: 1.0}" \
    >> "${TASK_RUN_DIR}/raw/gesture_commands.log" 2>&1
  sleep 1
done

ros2 service call /dex_hand/sim/set_fault dex_hand_interfaces/srv/SetSimFault \
  "{motor_id: 1, fault_type: motor_stuck, value: 0.0, enabled: true}" \
  > "${TASK_RUN_DIR}/raw/set_fault_response.txt"
sleep 1
ros2 topic echo --once --full-length /dex_hand/status \
  > "${TASK_RUN_DIR}/raw/status_fault_active.yaml"
ros2 service call /dex_hand/sim/clear_faults std_srvs/srv/Trigger "{}" \
  > "${TASK_RUN_DIR}/raw/clear_faults_response.txt"
ros2 service call /dex_hand/sim/reset std_srvs/srv/Trigger "{}" \
  > "${TASK_RUN_DIR}/raw/reset_response.txt"

terminate_process "${TASK_BAG_PID}"
wait "${TASK_BAG_PID}" || true
TASK_BAG_PID=""
ros2 bag info "${TASK_RUN_DIR}/rosbags/sim_session" \
  > "${TASK_RUN_DIR}/rosbags/info.txt"

terminate_process "${TASK_LAUNCH_PID}"
wait "${TASK_LAUNCH_PID}" || true
TASK_LAUNCH_PID=""

if pgrep -f "dex_hand_node|robot_state_publisher" > /dev/null; then
  echo "ROS processes remained after launch shutdown" >&2
  pgrep -af "dex_hand_node|robot_state_publisher" >&2
  exit 1
fi

printf 'headless_ros2_experiment,passed\n' \
  > "${TASK_RUN_DIR}/HEADLESS_STATUS.csv"
