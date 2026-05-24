"""Build patent geography supplement from CNIPA/Lens export files."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.iids_geo_join import (  # noqa: E402
    MINIMUM_ACCEPTANCE,
    STRONG_ACCEPTANCE,
    build_geography_from_export,
    discover_patent_export_file,
    evaluate_geography_acceptance,
    summarize_geography,
)
from diffusion_state.iids_patent_converter import DEFAULT_OUTPUT  # noqa: E402
from diffusion_state.patent_raw_sources import RAW_PATENTS_DIR  # noqa: E402

OUTPUT_DEFAULT = RAW_PATENTS_DIR / "cnipa_patent_geography_2015_2024.csv"


def main() -> int:
    p = argparse.ArgumentParser(description="Build cnipa_patent_geography CSV from CNIPA/Lens export.")
    p.add_argument("--export", type=Path, default=None, help="Source export CSV (auto-discover if omitted)")
    p.add_argument("--iids-csv", type=Path, default=DEFAULT_OUTPUT, help="Filter to IIDS patent_id keys")
    p.add_argument("--output", type=Path, default=OUTPUT_DEFAULT)
    p.add_argument("--source-label", default="")
    p.add_argument("--source-url", default="")
    p.add_argument("--skip-iids-filter", action="store_true")
    args = p.parse_args()

    export_path = discover_patent_export_file(args.export)
    if export_path is None:
        print(
            "ERROR: no CNIPA/Lens export found under data/raw/patents/.\n"
            "Place cnipa_industrial_ai_patents_*.csv or lens_industrial_ai_patents_*.csv with address fields.",
            file=sys.stderr,
        )
        return 1

    iids_csv = None if args.skip_iids_filter else args.iids_csv
    rows = build_geography_from_export(
        export_path,
        iids_csv=iids_csv,
        source_label=args.source_label,
        source_url=args.source_url,
    )
    if rows.empty:
        print("ERROR: geography builder produced zero rows.", file=sys.stderr)
        return 2

    args.output.parent.mkdir(parents=True, exist_ok=True)
    rows.to_csv(args.output, index=False, encoding="utf-8-sig", quoting=csv.QUOTE_MINIMAL)
    stats = summarize_geography(rows)
    ok_min, min_issues = evaluate_geography_acceptance(stats, thresholds=MINIMUM_ACCEPTANCE, label="minimum")
    ok_strong, _ = evaluate_geography_acceptance(stats, thresholds=STRONG_ACCEPTANCE, label="strong")
    print(f"Built geography supplement from {export_path.name}")
    print(f"rows={stats['rows']} city_fill={stats['city_fill_rate']:.1%} unique_cities={stats['unique_cities']}")
    print(f"Wrote: {args.output}")
    if ok_strong:
        print("Strong geography acceptance: passed")
    elif ok_min:
        print("Minimum geography acceptance: passed")
    else:
        for issue in min_issues:
            print(f"WARNING: {issue}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
