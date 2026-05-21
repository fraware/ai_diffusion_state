#!/usr/bin/env bash
# Full PCS credibility sprint pipeline (Git Bash / Linux / macOS).
# Usage: bash scripts/run_pcs_pipeline.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> purge stub controls (never used in paper pipeline)"
py -3 scripts/22_purge_stub_controls.py

echo "==> build + geo-audit"
py -3 scripts/11_build_registry_supplement.py
py -3 scripts/10_build_audited_city_overrides.py || echo "WARN: geo-audit targets not met; continuing."

echo "==> panel"
py -3 scripts/04_build_city_year_panel.py

if compgen -G "data/raw/city_controls/*.csv" >/dev/null 2>&1; then
  prod=0
  for f in data/raw/city_controls/*.csv; do
    case "$(basename "$f")" in
      *ci_stub*|*ingest_template*) ;;
      *) prod=1; break ;;
    esac
  done
  if [[ "$prod" -eq 1 ]]; then
    echo "==> city-controls (production)"
    py -3 scripts/06_build_city_controls.py
    py -3 scripts/04_build_city_year_panel.py
  else
    echo "SKIP city-controls (no production EPS/NBS files; stub/template excluded)"
  fi
else
  echo "SKIP city-controls (no raw EPS/NBS files)"
fi

echo "==> analysis"
py -3 scripts/05_run_baseline_models.py

echo "==> validate"
py -3 scripts/13_validate_geo_evidence.py
py -3 scripts/08_validate_sprint_outputs.py

echo "==> main paper tables"
py -3 scripts/12_build_main_paper_tables.py

echo "==> sync paper stats"
py -3 scripts/16_sync_paper_stats.py

echo "==> tests"
py -3 -m pytest -q

echo "==> PCS status"
py -3 scripts/15_pcs_status.py

echo "PCS pipeline complete."
