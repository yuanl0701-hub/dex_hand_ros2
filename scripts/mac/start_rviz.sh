#!/usr/bin/env bash
set -euo pipefail

TASK_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASK_REPO_ROOT="$(cd "${TASK_SCRIPT_DIR}/../.." && pwd)"
TASK_COMPOSE="${TASK_REPO_ROOT}/docker/ros2_humble_sim/compose.yaml"

cd "${TASK_REPO_ROOT}"
docker compose -f "${TASK_COMPOSE}" up -d rviz
printf '%s\n' "RViz noVNC: http://localhost:6080/vnc.html"
