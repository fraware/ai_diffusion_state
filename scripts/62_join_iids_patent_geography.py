"""Join applicant city/province/address onto an IIDS-derived patent export."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.iids_geo_join import (  # noqa: E402
    KEY_COVERAGE_MIN_RATE,
    MIN_CITY_FILL,
    MIN_PROVINCE_FILL,
    TIERED_ROBUSTNESS_MIN_FILL,
    STRONG_ACCEPTANCE,
    discover_geography_supplement,
    evaluate_geography_acceptance,
    is_geography_template_path,
    join_patent_geography,
    production_key_coverage_thresholds,
)
from diffusion_state.iids_geo_stream import measure_geography_key_coverage  # noqa: E402
from diffusion_state.iids_paths import FILTERED_PATENT_IDS_FOR_GEO_OUTPUT  # noqa: E402
from diffusion_state.iids_patent_converter import DEFAULT_OUTPUT  # noqa: E402
from diffusion_state.patent_raw_sources import RAW_PATENTS_DIR  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="Join geography supplement onto IIDS patent CSV.")
    p.add_argument("--iids-csv", type=Path, default=DEFAULT_OUTPUT)
    p.add_argument("--geo-csv", type=Path, default=None)
    p.add_argument("--output", type=Path, default=None, help="Defaults to in-place update of --iids-csv")
    p.add_argument(
        "--fixture-smoke",
        action="store_true",
        help="CI only: run join; do not fail on minimum acceptance thresholds.",
    )
    p.add_argument(
        "--tiered-robustness",
        action="store_true",
        help="Use 60%% tiered robustness thresholds (not 80%% publication gate).",
    )
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
    input_rows = sum(1 for _ in open(args.iids_csv, encoding="utf-8-sig", errors="replace")) - 1
    _, stats = join_patent_geography(args.iids_csv, geo, output)
    out_rows = int(stats.get("rows", 0))
    if out_rows < max(500, int(input_rows * 0.95)):
        print(
            f"ERROR: join output rows {out_rows} << input {input_rows} — aborting.",
            file=sys.stderr,
        )
        return 1
    if FILTERED_PATENT_IDS_FOR_GEO_OUTPUT.exists():
        stats = measure_geography_key_coverage(geo, FILTERED_PATENT_IDS_FOR_GEO_OUTPUT)
        if args.tiered_robustness:
            from diffusion_state.iids_geo_join import GeographyThresholds

            thresholds = GeographyThresholds(
                city_fill=TIERED_ROBUSTNESS_MIN_FILL,
                rows=max(500, int(stats.get("n_keys", 0) * KEY_COVERAGE_MIN_RATE)),
                cities=50,
                industries=None,
            )
            label = "iids_keys_tiered_robustness"
        else:
            thresholds = production_key_coverage_thresholds(int(stats.get("n_keys", 0)))
            label = "iids_keys_post_join"
    else:
        from diffusion_state.iids_geo_join import MINIMUM_ACCEPTANCE

        thresholds = MINIMUM_ACCEPTANCE
        label = "minimum"
    ok_min, min_issues = evaluate_geography_acceptance(
        stats,
        thresholds=thresholds,
        label=label,
        min_province_fill=MIN_PROVINCE_FILL,
        min_key_match_rate=KEY_COVERAGE_MIN_RATE if FILTERED_PATENT_IDS_FOR_GEO_OUTPUT.exists() else None,
    )
    ok_strong, _ = evaluate_geography_acceptance(stats, thresholds=STRONG_ACCEPTANCE, label="strong")
    print(f"Joined geography from {geo.name}")
    print(
        f"rows={stats['rows']} city_fill={stats['city_fill_rate']:.1%} "
        f"province_fill={stats.get('province_fill_rate', 0):.1%} "
        f"key_match={stats.get('key_match_rate', 1):.1%} "
        f"unique_cities={stats['unique_cities']}"
    )
    print(f"Wrote: {output}")
    if ok_strong:
        print("Strong geography acceptance: passed")
    elif ok_min:
        print("Minimum geography acceptance: passed (strong thresholds not met)")
    elif args.fixture_smoke:
        print("Fixture smoke: join completed (minimum thresholds not evaluated)")
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
