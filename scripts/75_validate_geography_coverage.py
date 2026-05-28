"""Validate geography coverage on the IIDS key list (Engineer A7)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.iids_geo_join import (  # noqa: E402
    MINIMUM_ACCEPTANCE,
    MIN_PROVINCE_FILL,
    KEY_COVERAGE_MIN_RATE,
    MIN_CITY_FILL,
    evaluate_geography_acceptance,
    is_geography_template_path,
    production_key_coverage_thresholds,
)
from diffusion_state.iids_geo_stream import measure_geography_key_coverage  # noqa: E402
from diffusion_state.iids_paths import (  # noqa: E402
    DEFAULT_GEO_OUTPUT,
    FILTERED_PATENT_IDS_FOR_GEO_OUTPUT,
)

REQUIRED_COLUMNS = (
    "patent_id",
    "applicant_city",
    "applicant_province",
    "applicant_address",
    "geo_source",
    "geo_match_confidence",
    "geo_notes",
)


def main() -> int:
    p = argparse.ArgumentParser(description="Validate geography CSV against IIDS keys.")
    p.add_argument("--geo-csv", type=Path, default=DEFAULT_GEO_OUTPUT)
    p.add_argument("--keys-csv", type=Path, default=FILTERED_PATENT_IDS_FOR_GEO_OUTPUT)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    if not args.geo_csv.exists():
        print(f"ERROR: geography file not found: {args.geo_csv}", file=sys.stderr)
        return 1
    if is_geography_template_path(args.geo_csv):
        print(f"ERROR: {args.geo_csv.name} is a template, not evidence.", file=sys.stderr)
        return 2
    if not args.keys_csv.exists():
        print(f"ERROR: keys file not found: {args.keys_csv}", file=sys.stderr)
        return 1

    import pandas as pd

    header = list(pd.read_csv(args.geo_csv, nrows=0).columns)
    missing = [c for c in REQUIRED_COLUMNS if c not in header]
    if missing and not all(
        c in header for c in ("patent_id", "applicant_city", "applicant_province", "applicant_address")
    ):
        print(f"ERROR: missing columns: {missing}", file=sys.stderr)
        return 3

    stats = measure_geography_key_coverage(args.geo_csv, args.keys_csv)
    n_keys = int(stats["n_keys"])
    thresholds = production_key_coverage_thresholds(n_keys)
    ok, issues = evaluate_geography_acceptance(
        stats,
        thresholds=thresholds,
        label="iids_keys",
        min_province_fill=MIN_PROVINCE_FILL,
        min_key_match_rate=KEY_COVERAGE_MIN_RATE,
    )

    report = {
        "geo_csv": str(args.geo_csv),
        "keys_csv": str(args.keys_csv),
        "required_columns_ok": not missing,
        "missing_columns": missing,
        "stats": stats,
        "thresholds": {
            "city_fill": MIN_CITY_FILL,
            "province_fill": MIN_PROVINCE_FILL,
            "key_match_rate": KEY_COVERAGE_MIN_RATE,
            "min_rows": thresholds.rows,
        },
        "passed": ok,
        "issues": issues,
    }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"rows(keys)={stats['rows']} key_match={stats['key_match_rate']:.1%}")
        print(f"city_fill={stats['city_fill_rate']:.1%} province_fill={stats['province_fill_rate']:.1%}")
        print(f"unique_cities={stats['unique_cities']}")
        for issue in issues:
            print(f"  - {issue}")
    return 0 if ok else 4


if __name__ == "__main__":
    raise SystemExit(main())
