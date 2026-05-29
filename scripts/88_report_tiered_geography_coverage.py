"""Coverage report for tiered or name-inferred geography CSV."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GEO = ROOT / "data/raw/patents/cnipa_patent_geography_2015_2024_applicant_name_inferred.csv"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--path", type=Path, default=DEFAULT_GEO)
    args = p.parse_args()

    if not args.path.exists():
        print(f"ERROR: missing {args.path}", file=sys.stderr)
        return 1

    df = pd.read_csv(args.path, low_memory=False, encoding="utf-8-sig")
    print("rows:", len(df))
    for col in ["applicant_city", "applicant_province", "applicant_address"]:
        if col in df.columns:
            fill = (
                df[col]
                .astype(str)
                .str.strip()
                .replace({"nan": "", "None": ""})
                .ne("")
                .mean()
            )
            print(col, "fill:", round(fill, 4))

    if "geo_match_confidence" in df.columns:
        print(df["geo_match_confidence"].value_counts(dropna=False).head(20))
    print(df.head(20).to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
