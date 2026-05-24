"""Join applicant city/province/address onto an IIDS-derived patent export."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.iids_geo_join import (  # noqa: E402
    discover_geography_supplement,
    join_patent_geography,
)
from diffusion_state.iids_patent_converter import DEFAULT_OUTPUT  # noqa: E402
from diffusion_state.patent_raw_sources import RAW_PATENTS_DIR  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="Join geography supplement onto IIDS patent CSV.")
    p.add_argument("--iids-csv", type=Path, default=DEFAULT_OUTPUT)
    p.add_argument("--geo-csv", type=Path, default=None)
    p.add_argument("--output", type=Path, default=None, help="Defaults to in-place update of --iids-csv")
    args = p.parse_args()

    geo = args.geo_csv or discover_geography_supplement(RAW_PATENTS_DIR)
    if geo is None or not geo.exists():
        print(
            "ERROR: no geography supplement found.\n"
            "Place cnipa_patent_geography_*.csv (or lens_patent_geography_*.csv) at data/raw/patents/\n"
            "with columns: patent_id/publication_number + applicant_city/province/address.",
            file=sys.stderr,
        )
        return 1
    if not args.iids_csv.exists():
        print(f"ERROR: IIDS export not found: {args.iids_csv}", file=sys.stderr)
        return 1

    output = args.output or args.iids_csv
    _, stats = join_patent_geography(args.iids_csv, geo, output)
    print(f"Joined geography from {geo.name}")
    print(f"rows={stats['rows']} city_fill={stats['city_fill_rate']:.1%} ({stats['rows_with_city']} rows)")
    print(f"Wrote: {output}")
    if stats["city_fill_rate"] < 0.8:
        print(
            "WARNING: city fill below 80% — Atlas patent_layer_ready may still fail until geography is complete.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
