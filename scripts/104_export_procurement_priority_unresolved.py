"""Export high-yield unresolved patent IDs for external CNIPA/Incopat geography procurement."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.procurement_priority_export import export_procurement_priority  # noqa: E402

DEFAULT_GEO = ROOT / "data/raw/patents/cnipa_patent_geography_2015_2024.csv"
DEFAULT_IIDS = ROOT / "data/raw/patents/opendatalab_iids_industrial_ai_patents_2015_2024_part1.csv"
DEFAULT_OUT = ROOT / "data/interim/iids_geo_procurement_priority_unresolved.csv"


def main() -> int:
    p = argparse.ArgumentParser(
        description="Build vendor procurement file from frozen geography unresolved rows."
    )
    p.add_argument("--geo", type=Path, default=DEFAULT_GEO)
    p.add_argument("--iids", type=Path, default=DEFAULT_IIDS)
    p.add_argument("--output", type=Path, default=DEFAULT_OUT)
    p.add_argument("--target-rows", type=int, default=900_000)
    args = p.parse_args()

    if not args.geo.exists():
        print(f"ERROR: missing {args.geo}", file=sys.stderr)
        return 1
    if not args.iids.exists():
        print(f"ERROR: missing {args.iids}", file=sys.stderr)
        return 1

    summary = export_procurement_priority(
        iids_csv=args.iids,
        geo_csv=args.geo,
        output_csv=args.output,
        target_rows=args.target_rows,
    )
    print(summary)
    return 0 if int(summary["rows_written"]) > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
