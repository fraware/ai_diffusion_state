"""Workstream A: build industrial AI patent city-industry-year panel."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.build_industrial_ai_patents import build_industrial_ai_patents
from diffusion_state.fetch_patents_cset import fetch_cset_patent_database
from diffusion_state.utils import PROJECT_ROOT


def main() -> int:
    patents_dir = PROJECT_ROOT / "data" / "raw" / "patents"
    patents_dir.mkdir(parents=True, exist_ok=True)

    has_micro = any(
        patents_dir.glob(p)
        for p in ("cnipa_*.csv", "cnipa_*.csv.gz", "patents_normalized*.csv")
    )
    if not has_micro:
        print(
            "NOTE: no CNIPA/normalized patent files in data/raw/patents/. "
            "Fetching CSET for taxonomy validation only."
        )
        fetch_cset_patent_database(patents_dir)

    include_cset = not has_micro
    panel = build_industrial_ai_patents(
        patents_dir=patents_dir,
        include_cset_validation=include_cset,
    )
    print(f"industrial_ai_patents_city_industry_year.csv: {len(panel)} rows")
    if panel.empty:
        print(
            "City-industry panel empty until CNIPA microdata is added. "
            "See data/raw/patents/README.md and docs/source_notes/industrial_ai_patents.md."
        )
        return 0
    print(
        f"  cities={panel['city'].nunique()} industries={panel['industry_code'].nunique()} "
        f"years={panel['year'].min()}-{panel['year'].max()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
