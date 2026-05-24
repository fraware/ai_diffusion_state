#!/usr/bin/env bash
# Package cloud VM artifacts for copy to the control laptop (no SQL, no OpenXLab cache).
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

ARCHIVE="${1:-atlas_iids_filtered_outputs.tar.gz}"
PYTHON="${PYTHON:-python3}"

IIDS_CSV="data/raw/patents/opendatalab_iids_industrial_ai_patents_2015_2024_part1.csv"
MANIFEST_DRAFT="data/raw/patents/patent_source_manifest_draft.csv"
MANIFEST="data/raw/patents/patent_source_manifest.csv"
KEYS_P9="outputs/tables/table_P9_iids_patent_keys_for_geography.csv"
KEYS_ALIAS="data/raw/patents/iids_filtered_patent_ids_for_geography.csv"
GEO="data/raw/patents/cnipa_patent_geography_2015_2024.csv"
P0="outputs/tables/table_P0_patent_export_schema_diagnostics.csv"

missing=0
for f in "$IIDS_CSV" "$MANIFEST_DRAFT"; do
  if [[ ! -f "$f" ]]; then
    echo "WARN: missing $f" >&2
    missing=$((missing + 1))
  fi
done
if [[ $missing -gt 0 ]]; then
  echo "ERROR: run cloud_iids_production.sh full-convert before copy-back." >&2
  exit 2
fi

# Ensure keys alias exists when production CSV is present.
if [[ -f "$IIDS_CSV" && ! -f "$KEYS_ALIAS" ]]; then
  "$PYTHON" scripts/66_export_iids_patent_keys.py --production
fi

INCLUDE=(
  "$IIDS_CSV"
  "$MANIFEST_DRAFT"
  "$KEYS_P9"
  "$KEYS_ALIAS"
  "$P0"
)
[[ -f "$MANIFEST" ]] && INCLUDE+=("$MANIFEST")
[[ -f "$GEO" ]] && INCLUDE+=("$GEO")
[[ -d outputs/logs ]] && INCLUDE+=(outputs/logs)

tar -czf "$ARCHIVE" "${INCLUDE[@]}" 2>/dev/null || {
  # GNU tar on Linux; fall back without logs if empty.
  tar -czf "$ARCHIVE" \
    "$IIDS_CSV" \
    "$MANIFEST_DRAFT" \
    "$KEYS_P9" \
    "$KEYS_ALIAS" \
    "$P0" \
    $(test -f "$MANIFEST" && echo "$MANIFEST") \
    $(test -f "$GEO" && echo "$GEO")
}

sha256sum "$ARCHIVE" > "${ARCHIVE}.sha256"
ls -lh "$ARCHIVE" "${ARCHIVE}.sha256"

cat <<EOF

Copy-back package ready: $ARCHIVE
Do NOT copy base_patent_detail.sql or $OPENXLAB_IIDS_SOURCES_DIR.

On control laptop (after scp):
  tar -xzf $ARCHIVE -C <repo>
On the control laptop:

  make atlas-iids-import-copyback ARCHIVE=atlas_iids_filtered_outputs.tar.gz
  # Windows: powershell -File scripts/import_iids_copyback.ps1 -Archive atlas_iids_filtered_outputs.tar.gz
  make atlas-iids-geography-brief
  make atlas-iids-control-evidence-chain

EOF
