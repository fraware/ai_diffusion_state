"""Build city-industry-year panel from IIDS export via streaming (tiered robustness path)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.iids_streaming_patent_panel import aggregate_iids_export_streaming  # noqa: E402
from diffusion_state.utils import write_csv  # noqa: E402

DEFAULT_IIDS = ROOT / "data/raw/patents/opendatalab_iids_industrial_ai_patents_2015_2024_part1.csv"
DEFAULT_OUT = ROOT / "data/processed/industrial_ai_patents_city_industry_year.csv"
DEFAULT_TABLES = ROOT / "outputs/tables"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--iids", type=Path, default=DEFAULT_IIDS)
    p.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = p.parse_args()

    if not args.iids.exists():
        print(f"ERROR: missing {args.iids}", file=sys.stderr)
        return 1

    panel_rows, stats = aggregate_iids_export_streaming(args.iids)
    panel = pd.DataFrame(panel_rows)
    if panel.empty:
        print("ERROR: empty panel", file=sys.stderr)
        return 1

    write_csv(panel, args.output)
    tables = DEFAULT_TABLES
    tables.mkdir(parents=True, exist_ok=True)

    top_cities = (
        panel.groupby(["city", "province"], as_index=False)["industrial_ai_patents"]
        .sum()
        .sort_values("industrial_ai_patents", ascending=False)
        .head(25)
    )
    top_inds = (
        panel.groupby(["industry_code", "industry"], as_index=False)["industrial_ai_patents"]
        .sum()
        .sort_values("industrial_ai_patents", ascending=False)
        .head(25)
    )
    write_csv(top_cities, tables / "table_A3_top_cities_industrial_ai_patents.csv")
    write_csv(top_inds, tables / "table_A4_top_industries_industrial_ai_patents.csv")

    print(
        {
            **stats,
            "n_cities": int(panel["city"].nunique()),
            "n_industries": int(panel["industry_code"].nunique()),
            "output": str(args.output),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
