"""Manual pilot QA for normalized geography CSV (Engineer B, step B3)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATH = (
    ROOT / "data" / "raw" / "patents" / "cnipa_patent_geography_2015_2024.csv"
)


def _fill_rate(series: pd.Series) -> float:
    cleaned = series.astype(str).str.strip().replace({"nan": "", "None": ""})
    return float(cleaned.ne("").mean())


def main() -> int:
    p = argparse.ArgumentParser(
        description="Inspect normalized CNIPA geography pilot output.",
    )
    p.add_argument("--path", type=Path, default=DEFAULT_PATH)
    args = p.parse_args()

    if not args.path.exists():
        print(f"ERROR: missing {args.path}", file=sys.stderr)
        return 1

    df = pd.read_csv(args.path, low_memory=False, encoding="utf-8-sig")
    print("rows:", len(df))
    print("columns:", list(df.columns))

    for col in (
        "patent_id",
        "applicant_city",
        "applicant_province",
        "applicant_address",
        "geo_source",
        "geo_match_confidence",
    ):
        if col in df.columns:
            print(col, "fill:", round(_fill_rate(df[col]), 4))
        else:
            print(col, "fill: MISSING COLUMN")

    print(df.head(5).to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
