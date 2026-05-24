#!/usr/bin/env bash
# Extract cloud VM tarball into repo root and verify copy-back artifacts.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
ARCHIVE="${1:-}"
SKIP_VERIFY="${SKIP_VERIFY:-0}"

if [[ -z "$ARCHIVE" ]]; then
  echo "Usage: $0 atlas_iids_filtered_outputs.tar.gz" >&2
  exit 2
fi
if [[ ! -f "$ARCHIVE" ]]; then
  echo "ERROR: archive not found: $ARCHIVE" >&2
  exit 2
fi

cd "$REPO"
echo "Extracting $ARCHIVE into $REPO ..."
tar -xzf "$ARCHIVE" -C "$REPO"

if [[ "$SKIP_VERIFY" != "1" ]]; then
  python3 scripts/70_verify_iids_copyback.py
  python3 scripts/71_geography_procurement_brief.py
fi

echo ""
echo "Next: obtain cnipa_patent_geography_2015_2024.csv, then:"
echo "  make atlas-iids-control-evidence-chain"
