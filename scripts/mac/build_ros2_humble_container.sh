#!/usr/bin/env bash
set -euo pipefail

TASK_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASK_REPO_ROOT="$(cd "${TASK_SCRIPT_DIR}/../.." && pwd)"
TASK_COMPOSE="${TASK_REPO_ROOT}/docker/ros2_humble_sim/compose.yaml"

docker compose -f "${TASK_COMPOSE}" build ros2-shell
