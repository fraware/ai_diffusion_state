#!/usr/bin/env bash
# Run IIDS production on WSL (uses ~950 GB WSL disk, not the 38 GB Windows C: partition).
set -euo pipefail

REPO="/mnt/c/Users/mateo/ai_diffusion_state"
IIDS_DIR="${HOME}/iids_sources"
VENV="${REPO}/.venv-wsl"
LOG="${REPO}/outputs/logs/iids_wsl_production.log"

mkdir -p "${REPO}/outputs/logs" "${IIDS_DIR}"

cd "${REPO}"
if [[ ! -x "${VENV}/bin/python" ]]; then
  python3 -m venv "${VENV}"
fi
# shellcheck disable=SC1091
source "${VENV}/bin/activate"
PYTHON="${VENV}/bin/python"
if ! "${PYTHON}" -c "import openxlab, pandas" 2>/dev/null; then
  pip install -q -U pip "requests~=2.28.2" openxlab pandas pyarrow
  pip install -q -e ".[dev]"
fi

export OPENXLAB_IIDS_SOURCES_DIR="${IIDS_DIR}"
export OPENXLAB_INSECURE_SSL="${OPENXLAB_INSECURE_SSL:-1}"
export PYTHONUTF8=1

exec > >(tee -a "${LOG}") 2>&1
echo "=== IIDS WSL production $(date -Is) ==="
echo "IIDS sources: ${IIDS_DIR}"
df -h "${HOME}" | tail -1

if [[ -z "${OPENXLAB_AK:-}" || -z "${OPENXLAB_SK:-}" ]]; then
  echo "ERROR: OPENXLAB_AK / OPENXLAB_SK not set in environment"
  exit 1
fi

"${PYTHON}" scripts/67_atlas_iids_preflight.py --json

if [[ ! -f "${IIDS_DIR}/Gracie___IIDS/base_patent_detail.sql" ]] && \
   [[ ! -f "${IIDS_DIR}/base_patent_detail.sql" ]]; then
  echo "Starting detail-only SQL download (~136 GB)..."
  "${PYTHON}" scripts/59_download_iids_patent_sources.py --detail-only --target-dir "${IIDS_DIR}"
  dl_code=$?
  if [[ ${dl_code} -ne 0 ]]; then
    echo "ERROR: IIDS SQL download failed (exit ${dl_code}). See ${LOG}"
    exit ${dl_code}
  fi
else
  echo "SQL detail file already present; skipping download."
fi

DETAIL_SQL="$("${PYTHON}" - <<'PY'
from pathlib import Path
import os
import sys
sys.path.insert(0, "src")
from diffusion_state.iids_patent_converter import find_iids_sql_paths
p = Path(os.environ["OPENXLAB_IIDS_SOURCES_DIR"])
d, _ = find_iids_sql_paths(p)
print(d or "")
PY
)"
if [[ -z "${DETAIL_SQL}" || ! -f "${DETAIL_SQL}" ]]; then
  echo "ERROR: base_patent_detail.sql not found after download"
  exit 2
fi

echo "Converting: ${DETAIL_SQL}"
"${PYTHON}" scripts/64_run_atlas_iids_pipeline.py \
  --detail-sql "${DETAIL_SQL}" \
  --skip-geo \
  --production

"${PYTHON}" scripts/58_prepare_patent_source_manifest.py
"${PYTHON}" scripts/68_merge_patent_manifest_draft.py

echo "=== Phase 1 complete $(date -Is) ==="
"${PYTHON}" scripts/69_iids_production_status.py --json || true
echo "Next: build cnipa_patent_geography_2015_2024.csv from CNIPA/Lens export using table_P9 keys"
