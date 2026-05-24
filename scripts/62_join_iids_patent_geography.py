"""Join applicant city/province/address onto an IIDS-derived patent export."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.iids_geo_join import (  # noqa: E402
    MINIMUM_ACCEPTANCE,
    STRONG_ACCEPTANCE,
    discover_geography_supplement,
    evaluate_geography_acceptance,
    is_geography_template_path,
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
            "Use data/raw/patents/cnipa_patent_geography_template.csv as the schema guide.",
            file=sys.stderr,
        )
        return 1
    if is_geography_template_path(geo):
        print(f"ERROR: {geo.name} is a schema template, not evidence.", file=sys.stderr)
        return 1
    if not args.iids_csv.exists():
        print(f"ERROR: IIDS export not found: {args.iids_csv}", file=sys.stderr)
        return 1

    output = args.output or args.iids_csv
    _, stats = join_patent_geography(args.iids_csv, geo, output)
    ok_min, min_issues = evaluate_geography_acceptance(stats, thresholds=MINIMUM_ACCEPTANCE, label="minimum")
    ok_strong, _ = evaluate_geography_acceptance(stats, thresholds=STRONG_ACCEPTANCE, label="strong")
    print(f"Joined geography from {geo.name}")
    print(
        f"rows={stats['rows']} city_fill={stats['city_fill_rate']:.1%} "
        f"({stats['rows_with_city']} rows) unique_cities={stats['unique_cities']}"
    )
    print(f"Wrote: {output}")
    if ok_strong:
        print("Strong geography acceptance: passed")
    elif ok_min:
        print("Minimum geography acceptance: passed (strong thresholds not met)")
    else:
        for issue in min_issues:
            print(f"WARNING: {issue}", file=sys.stderr)
        print(
            "WARNING: minimum geography acceptance failed — do not continue to evidence claims.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
