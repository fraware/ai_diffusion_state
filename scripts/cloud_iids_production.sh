#!/usr/bin/env bash
# IIDS production on a cloud VM (300 GB+ disk). Do not use WSL home or repo laptop C:.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="${OPENXLAB_IIDS_SOURCES_DIR:-/mnt/iids_sources}"
STEP="${1:-status}"
LOG="${IIDS_CLOUD_LOG:-$REPO/outputs/logs/iids_cloud_production.log}"

cd "$REPO"
mkdir -p outputs/logs

_log() {
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" | tee -a "$LOG"
}

if [[ "$STEP" != "status" && ( -z "${OPENXLAB_AK:-}" || -z "${OPENXLAB_SK:-}" ) ]]; then
  echo "ERROR: set OPENXLAB_AK and OPENXLAB_SK" >&2
  exit 1
fi

export OPENXLAB_IIDS_SOURCES_DIR="$TARGET"
export OPENXLAB_INSECURE_SSL="${OPENXLAB_INSECURE_SSL:-1}"
export PYTHONUTF8=1

mkdir -p "$TARGET"
PYTHON="${PYTHON:-python3}"

case "$STEP" in
  status)
    "$PYTHON" scripts/67_atlas_iids_preflight.py
    "$PYTHON" scripts/69_iids_production_status.py --sources-dir "$TARGET"
    df -h "$TARGET" 2>/dev/null | tail -1 || true
    echo "Runbook: docs/ATLAS_IIDS_CLEAN_RESTART_RUNBOOK.md"
    ;;
  docs)
    _log "STEP docs"
    "$PYTHON" scripts/59_download_iids_patent_sources.py --target-dir "$TARGET" 2>&1 | tee -a "$LOG"
    "$PYTHON" scripts/60_inspect_iids_patent_schema.py 2>&1 | tee -a "$LOG"
    ;;
  detail)
    _log "STEP detail (base_patent_detail.sql only)"
    "$PYTHON" scripts/59_download_iids_patent_sources.py --detail-only --target-dir "$TARGET" 2>&1 | tee -a "$LOG"
    find "$TARGET" -name 'base_patent_detail.sql' -type f | tee -a "$LOG"
    ;;
  smoke-convert)
    DETAIL="$(find "$TARGET" -name 'base_patent_detail.sql' -type f | head -1)"
    [[ -n "$DETAIL" ]] || { echo "ERROR: base_patent_detail.sql not found under $TARGET" >&2; exit 2; }
    _log "STEP smoke-convert $DETAIL"
    "$PYTHON" scripts/61_iids_sql_to_patent_csv.py --detail-sql "$DETAIL" --max-rows 50000 --production 2>&1 | tee -a "$LOG"
    ;;
  full-convert)
    DETAIL="$(find "$TARGET" -name 'base_patent_detail.sql' -type f | head -1)"
    [[ -n "$DETAIL" ]] || { echo "ERROR: base_patent_detail.sql not found under $TARGET" >&2; exit 2; }
    _log "STEP full-convert $DETAIL"
    "$PYTHON" scripts/61_iids_sql_to_patent_csv.py --detail-sql "$DETAIL" --production 2>&1 | tee -a "$LOG"
    "$PYTHON" scripts/66_export_iids_patent_keys.py --production 2>&1 | tee -a "$LOG"
    "$PYTHON" scripts/58_prepare_patent_source_manifest.py 2>&1 | tee -a "$LOG"
    "$PYTHON" scripts/68_merge_patent_manifest_draft.py --warn-only 2>&1 | tee -a "$LOG" || true
    _log "STEP full-convert complete"
    echo "Next: bash scripts/cloud_iids_copyback.sh"
    ;;
  copy-pack)
    bash scripts/cloud_iids_copyback.sh "${2:-atlas_iids_filtered_outputs.tar.gz}"
    ;;
  *)
    echo "Usage: $0 {status|docs|detail|smoke-convert|full-convert|copy-pack}" >&2
    exit 2
    ;;
esac
