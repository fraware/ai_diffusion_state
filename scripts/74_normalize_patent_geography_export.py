"""Normalize raw CNIPA/Lens geography export to Atlas contract CSV."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.iids_geography_normalize import normalize_geography_export  # noqa: E402
from diffusion_state.iids_paths import DEFAULT_GEO_OUTPUT  # noqa: E402

RAW_DEFAULT = ROOT / "data" / "raw" / "patents" / "cnipa_patent_geography_2015_2024_raw.csv"


def main() -> int:
    p = argparse.ArgumentParser(description="Normalize geography raw export to contract CSV.")
    p.add_argument("--raw", type=Path, default=RAW_DEFAULT, help="Concatenated source export")
    p.add_argument("--output", type=Path, default=DEFAULT_GEO_OUTPUT, help="Normalized contract file")
    p.add_argument("--geo-source", default="", help="Default geo_source when absent in raw")
    args = p.parse_args()
    if not args.raw.exists():
        print(f"ERROR: raw export not found: {args.raw}", file=sys.stderr)
        return 1
    if args.output.exists():
        print(f"ERROR: refusing to overwrite existing output: {args.output}", file=sys.stderr)
        print("Remove or rename the file after validating a prior run.", file=sys.stderr)
        return 2
    stats = normalize_geography_export(
        args.raw,
        args.output,
        geo_source=args.geo_source,
    )
    print(f"Wrote {args.output}")
    print(
        f"rows={stats['rows']} city_fill={stats['city_fill_rate']:.1%} "
        f"province_fill={stats['province_fill_rate']:.1%}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
