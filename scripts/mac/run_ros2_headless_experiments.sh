#!/usr/bin/env bash
set -euo pipefail

TASK_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASK_REPO_ROOT="$(cd "${TASK_SCRIPT_DIR}/../.." && pwd)"
TASK_COMPOSE="${TASK_REPO_ROOT}/docker/ros2_humble_sim/compose.yaml"
TASK_STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
TASK_RUN_REL="experiment_results/mac_ros2_${TASK_STAMP}"
TASK_RUN_DIR="${TASK_REPO_ROOT}/${TASK_RUN_REL}"

mkdir -p "${TASK_RUN_DIR}/environment"
cd "${TASK_REPO_ROOT}"

{
  sw_vers
  uname -a
  docker version
} > "${TASK_RUN_DIR}/environment/mac_and_docker.txt" 2>&1
git rev-parse HEAD > "${TASK_RUN_DIR}/environment/git_commit.txt"
git status --short > "${TASK_RUN_DIR}/environment/git_status.txt"
docker image inspect dex-hand-ros2-humble:local \
  --format '{{json .RepoDigests}} {{.Id}} {{.Architecture}}' \
  > "${TASK_RUN_DIR}/environment/container_image.txt"

docker compose -f "${TASK_COMPOSE}" run --rm \
  -e "DEX_HAND_EVIDENCE_REL=${TASK_RUN_REL}" \
  ros2-shell /workspace/scripts/mac/container_headless_experiment.sh

find "${TASK_RUN_DIR}" -type f ! -name checksums.sha256 -print0 \
  | sort -z | xargs -0 shasum -a 256 \
  > "${TASK_RUN_DIR}/checksums.sha256"
printf '%s\n' "${TASK_RUN_DIR}"
