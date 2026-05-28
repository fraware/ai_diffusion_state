"""Concatenate per-batch CNIPA/Lens geography exports into one raw CSV (Engineer A5)."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INDIR = ROOT / "data" / "interim" / "iids_geo_exports"
RAW_DEFAULT = ROOT / "data" / "raw" / "patents" / "cnipa_patent_geography_2015_2024_raw.csv"


def concat_exports(indir: Path, output: Path, pattern: str = "*.csv") -> int:
    files = sorted(indir.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No CSV files matching {pattern} in {indir}")

    output.parent.mkdir(parents=True, exist_ok=True)
    rows_written = 0
    writer = None
    with output.open("w", encoding="utf-8-sig", newline="") as f_out:
        for fp in files:
            with fp.open("r", encoding="utf-8-sig", errors="replace", newline="") as f_in:
                reader = csv.DictReader(f_in)
                if not reader.fieldnames:
                    continue
                if writer is None:
                    writer = csv.DictWriter(f_out, fieldnames=reader.fieldnames)
                    writer.writeheader()
                for row in reader:
                    writer.writerow(row)
                    rows_written += 1
    return rows_written


def main() -> int:
    p = argparse.ArgumentParser(description="Concatenate batch geography exports.")
    p.add_argument("--indir", type=Path, default=DEFAULT_INDIR)
    p.add_argument("--output", type=Path, default=RAW_DEFAULT)
    p.add_argument("--pattern", default="*.csv")
    args = p.parse_args()
    if not args.indir.exists():
        print(f"ERROR: input directory not found: {args.indir}", file=sys.stderr)
        print("Place per-batch CNIPA/Lens exports under data/interim/iids_geo_exports/", file=sys.stderr)
        return 1
    if args.output.exists():
        print(f"ERROR: refusing to overwrite {args.output}", file=sys.stderr)
        return 2
    try:
        n = concat_exports(args.indir, args.output, pattern=args.pattern)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {args.output} ({n:,} rows from {len(list(args.indir.glob(args.pattern)))} files)")
    print("Next: make atlas-iids-geo-normalize")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
