"""Pre-fill top_applicant_city_map.csv from table P12 for manual review."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_P12 = ROOT / "outputs/tables/table_P12_top_iids_applicants.csv"
DEFAULT_OUT = ROOT / "data/seed/top_applicant_city_map.csv"

COLUMNS = [
    "applicant_name",
    "applicant_city",
    "applicant_province",
    "source_url",
    "geo_match_confidence",
    "notes",
]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, default=DEFAULT_P12)
    p.add_argument("--output", type=Path, default=DEFAULT_OUT)
    p.add_argument("--top-n", type=int, default=500)
    args = p.parse_args()

    if not args.input.exists():
        print(f"ERROR: run scripts/87_report_iids_applicant_concentration.py first", file=sys.stderr)
        return 1

    top = pd.read_csv(args.input, encoding="utf-8-sig").head(args.top_n)
    out = pd.DataFrame(
        {
            "applicant_name": top["applicant_name"],
            "applicant_city": "",
            "applicant_province": "",
            "source_url": "",
            "geo_match_confidence": "",
            "notes": "",
        }
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.output, index=False, encoding="utf-8-sig")
    print({"rows": len(out), "output": str(args.output)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
