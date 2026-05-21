#!/usr/bin/env bash
# Full PCS credibility sprint pipeline (Git Bash / Linux / macOS).
# Usage: bash scripts/run_pcs_pipeline.sh [--stub-controls]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

USE_STUB=0
if [[ "${1:-}" == "--stub-controls" ]] || [[ "${1:-}" == "-UseStubControls" ]]; then
  USE_STUB=1
fi

echo "==> build + geo-audit"
py -3 scripts/11_build_registry_supplement.py
py -3 scripts/10_build_audited_city_overrides.py || echo "WARN: geo-audit targets not met; continuing."

echo "==> panel"
py -3 scripts/04_build_city_year_panel.py

if [[ "$USE_STUB" -eq 1 ]]; then
  echo "==> city-controls-stub (CI only)"
  py -3 scripts/06b_install_city_controls_stub.py
  py -3 scripts/04_build_city_year_panel.py
elif compgen -G "data/raw/city_controls/*.csv" >/dev/null 2>&1; then
  echo "==> city-controls (production)"
  py -3 scripts/06_build_city_controls.py
  py -3 scripts/04_build_city_year_panel.py
else
  echo "SKIP city-controls (no raw EPS/NBS files)"
fi

echo "==> analysis"
py -3 scripts/05_run_baseline_models.py

echo "==> validate"
py -3 scripts/08_validate_sprint_outputs.py

echo "==> tests"
py -3 -m pytest -q

echo "PCS pipeline complete."
