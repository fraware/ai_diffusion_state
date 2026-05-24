#!/usr/bin/env bash
# Quick status for the WSL IIDS download (run from Windows: wsl bash scripts/wsl_iids_status.sh)
set -euo pipefail
REPO="/mnt/c/Users/mateo/ai_diffusion_state"
IIDS_DIR="${HOME}/iids_sources"
LOG="/mnt/c/Users/mateo/ai_diffusion_state/outputs/logs/iids_wsl_production.log"
echo "=== IIDS WSL download status $(date -Is) ==="
df -h "${HOME}" | tail -1
if [[ -d "${IIDS_DIR}" ]]; then
  du -sh "${IIDS_DIR}" || true
  find "${IIDS_DIR}" -name 'base_patent_detail.sql' -type f -exec ls -lh {} \; 2>/dev/null || true
  find "${IIDS_DIR}" -path '*/.cache/*.odl' | wc -l | xargs -I{} echo "partial chunks: {}"
else
  echo "No ${IIDS_DIR} yet"
fi
if [[ -f "${LOG}" ]]; then
  echo "--- log tail ---"
  tail -n 3 "${LOG}" || true
fi
if [[ -x "${REPO}/.venv-wsl/bin/python" ]]; then
  "${REPO}/.venv-wsl/bin/python" "${REPO}/scripts/69_iids_production_status.py" 2>/dev/null || true
fi
