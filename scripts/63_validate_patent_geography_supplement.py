"""Validate a patent geography supplement before joining to IIDS exports."""
from __future__ import annotations

import argparse
import json
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
    validate_geography_supplement,
)
from diffusion_state.patent_raw_sources import RAW_PATENTS_DIR  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="Validate patent geography supplement acceptance thresholds.")
    p.add_argument("--geo-csv", type=Path, default=None)
    p.add_argument("--json", action="store_true")
    p.add_argument(
        "--fixture-smoke",
        action="store_true",
        help="CI only: validate schema/presence, skip minimum row/city thresholds.",
    )
    args = p.parse_args()

    geo = args.geo_csv or discover_geography_supplement(RAW_PATENTS_DIR)
    if geo is None or not geo.exists():
        print(
            "ERROR: no geography supplement found.\n"
            "Create data/raw/patents/cnipa_patent_geography_2015_2024.csv from "
            "data/raw/patents/cnipa_patent_geography_template.csv",
            file=sys.stderr,
        )
        return 1
    if is_geography_template_path(geo):
        print(f"ERROR: {geo.name} is a schema template, not evidence.", file=sys.stderr)
        return 1

    stats, messages = validate_geography_supplement(geo)
    if args.fixture_smoke:
        ok_min = stats.get("rows", 0) > 0 and stats.get("city_fill_rate", 0) > 0
        ok_strong = False
        min_issues = [] if ok_min else ["fixture smoke: empty geography"]
    else:
        ok_min, min_issues = evaluate_geography_acceptance(stats, thresholds=MINIMUM_ACCEPTANCE, label="minimum")
        ok_strong, _ = evaluate_geography_acceptance(stats, thresholds=STRONG_ACCEPTANCE, label="strong")
    report = {
        "geo_csv": str(geo),
        "stats": stats,
        "minimum_acceptance": ok_min,
        "strong_acceptance": ok_strong,
        "messages": messages,
    }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Geography supplement: {geo.name}")
        print(
            f"rows={stats['rows']} city_fill={stats['city_fill_rate']:.1%} "
            f"unique_cities={stats['unique_cities']}"
        )
        for msg in messages:
            print(f"- {msg}")
    if not ok_min:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
