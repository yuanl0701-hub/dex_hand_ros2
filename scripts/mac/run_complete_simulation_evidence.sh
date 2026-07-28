#!/usr/bin/env bash
set -euo pipefail

TASK_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"${TASK_SCRIPT_DIR}/run_native_simulation.sh"
"${TASK_SCRIPT_DIR}/build_ros2_humble_container.sh"
"${TASK_SCRIPT_DIR}/run_ros2_headless_experiments.sh"

printf '%s\n' "Evidence complete. Start visual verification with:"
printf '  %s\n' "${TASK_SCRIPT_DIR}/start_rviz.sh"
