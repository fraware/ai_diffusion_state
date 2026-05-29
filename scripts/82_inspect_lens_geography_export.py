"""Inspect Lens geography export CSV (smoke or batch pilot)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SMOKE = ROOT / "data/interim/iids_geo_exports/iids_geo_export_smoke_025.csv"
DEFAULT_BATCH = ROOT / "data/interim/iids_geo_exports/iids_geo_export_batch_001.csv"


def _fill_rate(series: pd.Series) -> float:
    cleaned = series.astype(str).str.strip().replace({"nan": "", "None": ""})
    return float(cleaned.ne("").mean())


def inspect(path: Path, head: int) -> int:
    if not path.exists():
        print(f"ERROR: missing {path}", file=sys.stderr)
        return 1

    df = pd.read_csv(path, low_memory=False, encoding="utf-8-sig")
    print("rows:", len(df))
    print("columns:", list(df.columns))
    print(df.head(head).to_string())

    for col in (
        "patent_id",
        "applicant_address",
        "applicant_city",
        "applicant_province",
    ):
        if col in df.columns:
            print(col, "fill:", round(_fill_rate(df[col]), 4))
        else:
            print(col, "fill: MISSING COLUMN")

    if "geo_match_confidence" in df.columns:
        print("\nmatch confidence:")
        print(df["geo_match_confidence"].value_counts(dropna=False).head(20))

    if "applicant_address" in df.columns:
        mask = df["applicant_address"].astype(str).str.len() > 5
        if mask.any():
            print("\nexamples with address:")
            print(df.loc[mask].head(10).to_string())

    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--path", type=Path, default=None)
    p.add_argument("--smoke", action="store_true", help="Inspect smoke_025 export")
    p.add_argument("--batch-001", action="store_true", help="Inspect batch_001 export")
    p.add_argument("--head", type=int, default=25)
    args = p.parse_args()

    if args.path is not None:
        path = args.path
    elif args.batch_001:
        path = DEFAULT_BATCH
    else:
        path = DEFAULT_SMOKE

    return inspect(path, args.head)


if __name__ == "__main__":
    raise SystemExit(main())
