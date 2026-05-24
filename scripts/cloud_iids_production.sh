#!/usr/bin/env bash
# IIDS production on a cloud VM (300 GB+ disk). Do not use WSL home or repo laptop C:.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="${OPENXLAB_IIDS_SOURCES_DIR:-/mnt/iids_sources}"
STEP="${1:-status}"

cd "$REPO"

if [[ -z "${OPENXLAB_AK:-}" || -z "${OPENXLAB_SK:-}" ]]; then
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
    df -h "$TARGET" | tail -1
    echo "Runbook: docs/ATLAS_IIDS_CLEAN_RESTART_RUNBOOK.md (cloud VM section)"
    ;;
  docs)
    "$PYTHON" scripts/59_download_iids_patent_sources.py --target-dir "$TARGET"
    "$PYTHON" scripts/60_inspect_iids_patent_schema.py
    ;;
  detail)
    "$PYTHON" scripts/59_download_iids_patent_sources.py --detail-only --target-dir "$TARGET"
    find "$TARGET" -name 'base_patent_detail.sql' -type f
    ;;
  smoke-convert)
    DETAIL="$(find "$TARGET" -name 'base_patent_detail.sql' -type f | head -1)"
    [[ -n "$DETAIL" ]] || { echo "ERROR: base_patent_detail.sql not found under $TARGET" >&2; exit 2; }
    "$PYTHON" scripts/61_iids_sql_to_patent_csv.py --detail-sql "$DETAIL" --max-rows 50000 --production
    ;;
  full-convert)
    DETAIL="$(find "$TARGET" -name 'base_patent_detail.sql' -type f | head -1)"
    [[ -n "$DETAIL" ]] || { echo "ERROR: base_patent_detail.sql not found under $TARGET" >&2; exit 2; }
    "$PYTHON" scripts/61_iids_sql_to_patent_csv.py --detail-sql "$DETAIL" --production
    "$PYTHON" scripts/66_export_iids_patent_keys.py --production
    "$PYTHON" scripts/58_prepare_patent_source_manifest.py
    "$PYTHON" scripts/68_merge_patent_manifest_draft.py
    echo "Copy back data/raw/patents/opendatalab_iids_*.csv and manifest tables; delete SQL on VM."
    ;;
  *)
    echo "Usage: $0 {status|docs|detail|smoke-convert|full-convert}" >&2
    exit 2
    ;;
esac
