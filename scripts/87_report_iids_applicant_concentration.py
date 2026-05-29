"""Streaming applicant-frequency report for IIDS patent CSV (table P12)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data/raw/patents/opendatalab_iids_industrial_ai_patents_2015_2024_part1.csv"
DEFAULT_OUTPUT = ROOT / "outputs/tables/table_P12_top_iids_applicants.csv"


def first_applicant(name: str) -> str:
    text = str(name or "").strip()
    if not text:
        return ""
    return text.split(";")[0].split("|")[0].split(",")[0].strip()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    p.add_argument("--chunksize", type=int, default=250_000)
    args = p.parse_args()

    if not args.input.exists():
        print(f"ERROR: missing {args.input}", file=sys.stderr)
        return 1

    usecols = ["patent_id", "applicant_name", "application_year", "search_keyword"]
    counts: dict[str, int] = {}
    n = 0

    for chunk in pd.read_csv(
        args.input,
        usecols=usecols,
        chunksize=args.chunksize,
        encoding="utf-8-sig",
        low_memory=False,
    ):
        n += len(chunk)
        names = chunk["applicant_name"].fillna("").astype(str)
        for name in names:
            first = first_applicant(name)
            if first:
                counts[first] = counts.get(first, 0) + 1
        print("processed", n, "unique applicants", len(counts), flush=True)

    out = pd.DataFrame(
        [{"applicant_name": k, "patent_count": v} for k, v in counts.items()]
    ).sort_values("patent_count", ascending=False)

    total_patents = int(out["patent_count"].sum())
    out["cum_patents"] = out["patent_count"].cumsum()
    out["cum_share"] = out["cum_patents"] / total_patents

    args.output.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.output, index=False, encoding="utf-8-sig")

    print("total rows:", n)
    print(out.head(50).to_string(index=False))
    for top_n in (100, 500, 1000, 5000):
        cov = out.head(top_n)["patent_count"].sum() / total_patents
        print(f"coverage top {top_n}:", round(cov, 4))
    print("wrote", args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
