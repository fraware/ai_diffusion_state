"""Validate sprint deliverables exist; report city-controls blocker explicitly."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.panel_controls import controls_available
from diffusion_state.utils import PROJECT_ROOT
import pandas as pd

REQUIRED_TABLES = [
    "table_1_dataset_summary.csv",
    "table_2_top_smart_factory_cities.csv",
    "table_3_pilot_zone_adoption_models.csv",
    "table_6_hub_exclusion_robustness.csv",
    "table_9_city_resolution_audit.csv",
    "table_timing_diagnostic_coefficients.csv",
]

OPTIONAL_TABLES = [
    "table_5_controlled_adoption_models.csv",
    "table_7_pilot_city_balance.csv",
    "table_8_matched_adoption_models.csv",
    "table_10_export_bridge_audit.csv",
    "table_11_export_sector_descriptives.csv",
    "table_12_export_models_revised.csv",
    "table_13_city_industry_adoption_models.csv",
]

BLOCKER = PROJECT_ROOT / "data" / "raw" / "city_controls"
PANEL = PROJECT_ROOT / "data" / "processed" / "analysis_city_year_panel.csv"


def main() -> int:
    tables_dir = PROJECT_ROOT / "outputs" / "tables"
    missing = [t for t in REQUIRED_TABLES if not (tables_dir / t).exists()]
    if missing:
        print("MISSING required tables:", ", ".join(missing))
        return 1

    print("OK required tables:", len(REQUIRED_TABLES))

    for t in OPTIONAL_TABLES:
        path = tables_dir / t
        status = "present" if path.exists() else "absent"
        print(f"  optional {t}: {status}")

    raw_controls = list(BLOCKER.glob("*.csv")) + list(BLOCKER.glob("*.xlsx")) + list(BLOCKER.glob("*.xls"))
    if not raw_controls:
        print("BLOCKER: no EPS/NBS files in data/raw/city_controls/ — controlled models cannot run.")
    else:
        print(f"City controls raw files: {len(raw_controls)}")

    if PANEL.exists():
        panel = pd.read_csv(PANEL)
        if controls_available(panel):
            print("OK city controls merged into analysis panel for adoption years.")
        else:
            print("WARN controls file exists but panel missing adoption-year control values.")

    t5 = tables_dir / "table_5_controlled_adoption_models.csv"
    if t5.exists():
        m = pd.read_csv(t5)
        if (m["term"] == "skipped").any():
            print("Table 5 status: skipped until city controls ingest.")

    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
