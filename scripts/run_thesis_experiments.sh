#!/usr/bin/env bash
# Run all no-hardware experiments and generate a thesis evidence bundle.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
MODE="full"
if [[ "${1:-}" == "--quick" ]]; then
  MODE="quick"
elif [[ $# -gt 0 ]]; then
  echo "Usage: $0 [--quick]" >&2
  exit 2
fi

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "The full experiment suite must run on Ubuntu Linux." >&2
  exit 2
fi
if [[ ! -f /opt/ros/humble/setup.bash ]]; then
  echo "ROS 2 Humble is missing: /opt/ros/humble/setup.bash" >&2
  echo "Install ROS 2 Humble, then run scripts/bootstrap_ubuntu.sh." >&2
  exit 2
fi

cd "${REPO_ROOT}" || exit 2

set +u
source /opt/ros/humble/setup.bash
set -u

if [[ "${ROS_DISTRO:-}" != "humble" ]]; then
  echo "Expected ROS_DISTRO=humble, got ${ROS_DISTRO:-unset}." >&2
  exit 2
fi

if [[ "${MODE}" == "full" ]]; then
  E00_BUILD_RUNS="${DEX_E00_BUILD_RUNS:-3}"
  TIMING_RUNS="${DEX_TIMING_RUNS:-5}"
  TIMING_SAMPLES="${DEX_TIMING_SAMPLES:-600}"
  SAFETY_REPETITIONS="${DEX_SAFETY_REPETITIONS:-20}"
  RESOURCE_DURATION="${DEX_RESOURCE_DURATION:-60}"
else
  E00_BUILD_RUNS=1
  TIMING_RUNS=1
  TIMING_SAMPLES=30
  SAFETY_REPETITIONS=2
  RESOURCE_DURATION=5
fi

UTC_STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
GIT_SHORT="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
RUN_ID="${UTC_STAMP}_${GIT_SHORT}_${MODE}"
RUN_DIR="${REPO_ROOT}/experiments/runs/${RUN_ID}"
WORK_DIR="${REPO_ROOT}/.experiment_work/${RUN_ID}"
ARCHIVE_DIR="${REPO_ROOT}/experiments/archives"
STATUS_FILE="${RUN_DIR}/run_status.csv"

mkdir -p "${RUN_DIR}" "${WORK_DIR}" "${ARCHIVE_DIR}"
printf 'experiment,step,status,exit_code,log\n' > "${STATUS_FILE}"

FAILURES=0
NODE_PID=""
LOAD_PID=""
STRESS_PID=""

record_status() {
  local experiment="$1"
  local step="$2"
  local status="$3"
  local code="$4"
  local log_path="$5"
  printf '%s,%s,%s,%s,%s\n' \
    "${experiment}" "${step}" "${status}" "${code}" "${log_path}" \
    >> "${STATUS_FILE}"
}

run_logged() {
  local experiment="$1"
  local step="$2"
  local log_path="$3"
  shift 3
  mkdir -p "$(dirname "${log_path}")"
  {
    echo "started_at_utc=$(date -u --iso-8601=seconds)"
    printf 'command='
    printf '%q ' "$@"
    echo
    "$@"
  } 2>&1 | tee "${log_path}"
  local code=${PIPESTATUS[0]}
  echo "exit_code=${code}" | tee -a "${log_path}"
  echo "finished_at_utc=$(date -u --iso-8601=seconds)" | tee -a "${log_path}"
  if [[ ${code} -eq 0 ]]; then
    record_status "${experiment}" "${step}" "completed" "${code}" \
      "${log_path#${RUN_DIR}/}"
  else
    record_status "${experiment}" "${step}" "failed" "${code}" \
      "${log_path#${RUN_DIR}/}"
    FAILURES=$((FAILURES + 1))
  fi
  return "${code}"
}

stop_owned_process() {
  local pid="$1"
  if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
    kill -INT "${pid}" 2>/dev/null || true
    wait "${pid}" 2>/dev/null || true
  fi
}

cleanup() {
  stop_owned_process "${LOAD_PID}"
  stop_owned_process "${STRESS_PID}"
  stop_owned_process "${NODE_PID}"
}
trap cleanup EXIT INT TERM

echo "Run ID: ${RUN_ID}"
echo "Results: ${RUN_DIR}"
echo "Mode: ${MODE}"

mkdir -p "${RUN_DIR}/E00_environment"
run_logged E00 collect_environment \
  "${RUN_DIR}/E00_environment/collect_environment.log" \
  python3 tools/collect_environment.py \
  --output "${RUN_DIR}/E00_environment"

run_logged E00 rosdep \
  "${RUN_DIR}/E00_environment/rosdep.log" \
  rosdep install --from-paths src --ignore-src -r -y --rosdistro humble

printf 'run,exit_code,duration_s,build_log\n' \
  > "${RUN_DIR}/E00_environment/build_summary.csv"

PRIMARY_BUILD=""
PRIMARY_INSTALL=""
BUILD_READY=1
for run_number in $(seq 1 "${E00_BUILD_RUNS}"); do
  label="$(printf '%02d' "${run_number}")"
  build_base="${WORK_DIR}/build_${label}"
  install_base="${WORK_DIR}/install_${label}"
  log_base="${WORK_DIR}/colcon_log_${label}"
  build_log="${RUN_DIR}/E00_environment/build_run_${label}.log"
  started_seconds=${SECONDS}
  run_logged E00 "isolated_build_${label}" "${build_log}" \
    colcon --log-base "${log_base}" build \
    --build-base "${build_base}" \
    --install-base "${install_base}" \
    --symlink-install \
    --packages-up-to dex_hand_ros2
  build_code=$?
  duration_seconds=$((SECONDS - started_seconds))
  printf '%s,%s,%s,%s\n' \
    "${label}" "${build_code}" "${duration_seconds}" \
    "${build_log#${RUN_DIR}/}" \
    >> "${RUN_DIR}/E00_environment/build_summary.csv"
  if [[ ${build_code} -ne 0 ]]; then
    BUILD_READY=0
    break
  fi
  if [[ ${run_number} -eq 1 ]]; then
    PRIMARY_BUILD="${build_base}"
    PRIMARY_INSTALL="${install_base}"
  fi
done

if [[ ${BUILD_READY} -eq 1 && -n "${PRIMARY_INSTALL}" ]]; then
  set +u
  source "${PRIMARY_INSTALL}/setup.bash"
  set -u
  run_logged E00 inspect_interfaces \
    "${RUN_DIR}/E00_environment/interface_inspection.log" \
    bash -c \
    'ros2 pkg prefix dex_hand_interfaces &&
     ros2 pkg prefix dex_hand_ros2 &&
     ros2 interface show dex_hand_interfaces/msg/GestureCmd &&
     ros2 interface show dex_hand_interfaces/msg/MotorState &&
     ros2 interface show dex_hand_interfaces/srv/RunGesturePid'
else
  record_status E00 downstream_ros_experiments blocked 1 \
    "E00_environment/build_summary.csv"
fi

if [[ ${BUILD_READY} -eq 1 ]]; then
  mkdir -p "${RUN_DIR}/E01_tests"
  run_logged E01 colcon_test \
    "${RUN_DIR}/E01_tests/colcon_test.log" \
    colcon test \
    --build-base "${PRIMARY_BUILD}" \
    --install-base "${PRIMARY_INSTALL}" \
    --packages-select dex_hand_ros2
  run_logged E01 colcon_test_result \
    "${RUN_DIR}/E01_tests/colcon_test_result.log" \
    colcon test-result --test-result-base "${PRIMARY_BUILD}" --verbose
  run_logged E01 pure_pytest \
    "${RUN_DIR}/E01_tests/pytest.log" \
    env PYTHONPATH=src/dex_hand_ros2 \
    python3 -m pytest -q src/dex_hand_ros2/test

  mkdir -p "${RUN_DIR}/node"
  ros2 run dex_hand_ros2 hand_node \
    --ros-args \
    -p driver_type:=fake \
    -p status_pub_freq:=10.0 \
    > "${RUN_DIR}/node/dex_hand_node.log" 2>&1 &
  NODE_PID=$!
  node_ready=0
  for _ in $(seq 1 50); do
    if ! kill -0 "${NODE_PID}" 2>/dev/null; then
      break
    fi
    if ros2 node list 2>/dev/null | grep -qx '/dex_hand_node'; then
      node_ready=1
      break
    fi
    sleep 0.2
  done
  if [[ ${node_ready} -eq 1 ]]; then
    record_status runtime dex_hand_node_started completed 0 \
      "node/dex_hand_node.log"

    run_logged E02 functional \
      "${RUN_DIR}/E02_functional/experiment.log" \
      ros2 run dex_hand_ros2 ros_experiment functional \
      --output "${RUN_DIR}/E02_functional"

    for run_number in $(seq 1 "${TIMING_RUNS}"); do
      label="$(printf '%02d' "${run_number}")"
      run_logged E03 "idle_timing_${label}" \
        "${RUN_DIR}/E03_timing/idle_run_${label}/experiment.log" \
        ros2 run dex_hand_ros2 ros_experiment timing \
        --samples "${TIMING_SAMPLES}" \
        --condition reliable_idle \
        --output "${RUN_DIR}/E03_timing/idle_run_${label}"
    done

    if command -v stress-ng >/dev/null 2>&1; then
      cpu_workers=$(( $(nproc) - 1 ))
      if [[ ${cpu_workers} -lt 1 ]]; then
        cpu_workers=1
      fi
      for run_number in $(seq 1 "${TIMING_RUNS}"); do
        label="$(printf '%02d' "${run_number}")"
        stress_log="${RUN_DIR}/E03_timing/cpu_stress_run_${label}/stress_ng.log"
        mkdir -p "$(dirname "${stress_log}")"
        stress-ng --cpu "${cpu_workers}" \
          --timeout "$((TIMING_SAMPLES / 8 + 30))s" \
          --metrics-brief > "${stress_log}" 2>&1 &
        STRESS_PID=$!
        run_logged E03 "cpu_stress_timing_${label}" \
          "${RUN_DIR}/E03_timing/cpu_stress_run_${label}/experiment.log" \
          ros2 run dex_hand_ros2 ros_experiment timing \
          --samples "${TIMING_SAMPLES}" \
          --condition reliable_cpu_stress \
          --output "${RUN_DIR}/E03_timing/cpu_stress_run_${label}"
        stop_owned_process "${STRESS_PID}"
        STRESS_PID=""
      done
    else
      record_status E03 cpu_stress_timing skipped 0 \
        "stress-ng is not installed; run scripts/bootstrap_ubuntu.sh"
    fi

    run_logged E04 safety \
      "${RUN_DIR}/E04_safety/experiment.log" \
      ros2 run dex_hand_ros2 ros_experiment safety \
      --repetitions "${SAFETY_REPETITIONS}" \
      --output "${RUN_DIR}/E04_safety"

    mkdir -p "${RUN_DIR}/E07_resources"
    run_logged E07 idle_resource \
      "${RUN_DIR}/E07_resources/idle_monitor.log" \
      python3 tools/resource_monitor.py \
      --pid "${NODE_PID}" \
      --duration "${RESOURCE_DURATION}" \
      --condition idle \
      --output "${RUN_DIR}/E07_resources/idle.csv"

    ros2 run dex_hand_ros2 ros_experiment load \
      --duration "${RESOURCE_DURATION}" \
      --rate 20 \
      --output "${RUN_DIR}/E07_resources/load_client" \
      > "${RUN_DIR}/E07_resources/load_client.log" 2>&1 &
    LOAD_PID=$!
    run_logged E07 command_load_resource \
      "${RUN_DIR}/E07_resources/command_load_monitor.log" \
      python3 tools/resource_monitor.py \
      --pid "${NODE_PID}" \
      --duration "${RESOURCE_DURATION}" \
      --condition command_load_20hz \
      --output "${RUN_DIR}/E07_resources/command_load_20hz.csv"
    wait "${LOAD_PID}"
    load_code=$?
    if [[ ${load_code} -eq 0 ]]; then
      record_status E07 load_client completed 0 \
        "E07_resources/load_client.log"
    else
      record_status E07 load_client failed "${load_code}" \
        "E07_resources/load_client.log"
      FAILURES=$((FAILURES + 1))
    fi
    LOAD_PID=""

    # Repeat the idle timing condition with a best-effort offered/requested
    # profile while holding the machine, fake backend, depth and sample count
    # constant.
    stop_owned_process "${NODE_PID}"
    NODE_PID=""
    ros2 run dex_hand_ros2 hand_node \
      --ros-args \
      -p driver_type:=fake \
      -p status_pub_freq:=10.0 \
      -p qos_reliability:=best_effort \
      -p qos_depth:=10 \
      > "${RUN_DIR}/node/dex_hand_node_best_effort.log" 2>&1 &
    NODE_PID=$!
    best_effort_ready=0
    for _ in $(seq 1 50); do
      if ! kill -0 "${NODE_PID}" 2>/dev/null; then
        break
      fi
      if ros2 node list 2>/dev/null | grep -qx '/dex_hand_node'; then
        best_effort_ready=1
        break
      fi
      sleep 0.2
    done
    if [[ ${best_effort_ready} -eq 1 ]]; then
      record_status runtime best_effort_node_started completed 0 \
        "node/dex_hand_node_best_effort.log"
      for run_number in $(seq 1 "${TIMING_RUNS}"); do
        label="$(printf '%02d' "${run_number}")"
        run_logged E03 "best_effort_idle_timing_${label}" \
          "${RUN_DIR}/E03_timing/best_effort_idle_run_${label}/experiment.log" \
          ros2 run dex_hand_ros2 ros_experiment \
          --qos-reliability best_effort \
          timing \
          --samples "${TIMING_SAMPLES}" \
          --condition best_effort_idle \
          --output "${RUN_DIR}/E03_timing/best_effort_idle_run_${label}"
      done
    else
      record_status runtime best_effort_node_started failed 1 \
        "node/dex_hand_node_best_effort.log"
      FAILURES=$((FAILURES + 1))
    fi
  else
    record_status runtime dex_hand_node_started failed 1 \
      "node/dex_hand_node.log"
    FAILURES=$((FAILURES + 1))
  fi
  stop_owned_process "${NODE_PID}"
  NODE_PID=""
fi

run_logged E05_E06 algorithm_experiments \
  "${RUN_DIR}/algorithm_experiments.log" \
  env PYTHONPATH=src/dex_hand_ros2 \
  python3 tools/run_algorithm_experiments.py \
  --output "${RUN_DIR}"

run_logged analysis generate_thesis_materials \
  "${RUN_DIR}/analysis.log" \
  python3 tools/analyze_experiments.py --run "${RUN_DIR}"

(
  cd "${RUN_DIR}" || exit 1
  find . -type f ! -name checksums.sha256 -print0 \
    | sort -z \
    | xargs -0 sha256sum \
    > checksums.sha256
)
checksum_code=$?
if [[ ${checksum_code} -eq 0 ]]; then
  record_status archive checksums completed 0 checksums.sha256
  (
    cd "${RUN_DIR}" || exit 1
    find . -type f ! -name checksums.sha256 -print0 \
      | sort -z \
      | xargs -0 sha256sum \
      > checksums.sha256
  )
else
  record_status archive checksums failed "${checksum_code}" checksums.sha256
  FAILURES=$((FAILURES + 1))
fi

ARCHIVE_PATH="${ARCHIVE_DIR}/${RUN_ID}.tar.gz"
tar -czf "${ARCHIVE_PATH}" -C "${REPO_ROOT}/experiments/runs" "${RUN_ID}"
archive_code=$?
if [[ ${archive_code} -ne 0 ]]; then
  FAILURES=$((FAILURES + 1))
fi

echo
echo "Experiment suite finished."
echo "Run directory: ${RUN_DIR}"
echo "Archive: ${ARCHIVE_PATH}"
echo "Recorded failures: ${FAILURES}"
echo "Open ${RUN_DIR}/EVIDENCE_INDEX.md and ${STATUS_FILE} first."

if [[ ${FAILURES} -gt 0 ]]; then
  exit 1
fi
