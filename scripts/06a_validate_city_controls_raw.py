"""Validate EPS/NBS raw city-control files before make city-controls."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd

from diffusion_state.build_city_controls import COLUMN_ALIASES, REQUIRED_COLUMNS
from diffusion_state.panel_controls import _is_production_raw_file

RAW_DIR = ROOT / "data" / "raw" / "city_controls"


def main() -> int:
    all_files = list(RAW_DIR.glob("*.csv")) + list(RAW_DIR.glob("*.xlsx")) + list(RAW_DIR.glob("*.xls"))
    files = [p for p in all_files if _is_production_raw_file(p)]
    if not files:
        print("BLOCKER: no production EPS/NBS files in data/raw/city_controls/")
        print("  (ingest_template and ci_stub are excluded)")
        if all_files:
            print("  found non-production files:", ", ".join(p.name for p in all_files))
        return 1

    frames = []
    for path in files:
        try:
            if path.suffix.lower() in {".xlsx", ".xls"}:
                df = pd.read_excel(path)
            else:
                df = pd.read_csv(path)
            df = df.rename(columns={c: COLUMN_ALIASES.get(c, c) for c in df.columns})
            frames.append(df)
        except Exception as exc:
            print(f"FAIL read {path.name}: {exc}")
            return 1

    raw = pd.concat(frames, ignore_index=True)
    missing = [c for c in REQUIRED_COLUMNS if c not in raw.columns]
    if missing:
        print("FAIL missing columns:", ", ".join(missing))
        return 1

    n_city_year = raw.drop_duplicates(subset=["city", "year"]).shape[0]
    print(f"OK {len(files)} raw file(s); {n_city_year} city-year rows; columns complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
