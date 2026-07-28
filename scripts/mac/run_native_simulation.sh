#!/usr/bin/env bash
set -euo pipefail

TASK_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASK_REPO_ROOT="$(cd "${TASK_SCRIPT_DIR}/../.." && pwd)"
TASK_PYTHON="${DEX_HAND_PYTHON:-/opt/anaconda3/bin/python3}"
TASK_OUTPUT_ROOT="${1:-${TASK_REPO_ROOT}/experiment_results}"
TASK_LOG_DIR="${TASK_OUTPUT_ROOT}/native_logs"

mkdir -p "${TASK_LOG_DIR}" /private/tmp/dex_hand_matplotlib
cd "${TASK_REPO_ROOT}"

PYTHONPATH=src/dex_hand_ros2 "${TASK_PYTHON}" -m pytest -q \
  src/dex_hand_ros2/test | tee "${TASK_LOG_DIR}/pytest.log"

TASK_RUN_PATH="$(
  PYTHONPATH=src/dex_hand_ros2 "${TASK_PYTHON}" \
    experiments/run_simulation_experiments.py --output "${TASK_OUTPUT_ROOT}" \
    | tail -n 1
)"

MPLCONFIGDIR=/private/tmp/dex_hand_matplotlib "${TASK_PYTHON}" \
  experiments/generate_thesis_assets.py --run-dir "${TASK_RUN_PATH}" \
  | tee "${TASK_LOG_DIR}/asset_generation.log"

printf '%s\n' "${TASK_RUN_PATH}"
