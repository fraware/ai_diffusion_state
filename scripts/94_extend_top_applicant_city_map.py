"""Append top-N applicants from P12 to top_applicant_city_map without clobbering fills."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_P12 = ROOT / "outputs/tables/table_P12_top_iids_applicants.csv"
DEFAULT_MAP = ROOT / "data/seed/top_applicant_city_map.csv"

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
    p.add_argument("--p12", type=Path, default=DEFAULT_P12)
    p.add_argument("--map", type=Path, default=DEFAULT_MAP)
    p.add_argument("--top-n", type=int, default=2000, help="Include P12 ranks 1..N")
    args = p.parse_args()

    if not args.p12.exists():
        print("ERROR: run scripts/87_report_iids_applicant_concentration.py first", file=sys.stderr)
        return 1

    existing: dict[str, dict[str, str]] = {}
    if args.map.exists():
        with args.map.open("r", encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                name = str(row.get("applicant_name") or "").strip()
                if name:
                    existing[name] = row

    added = 0
    with args.p12.open("r", encoding="utf-8-sig", newline="") as f:
        for i, row in enumerate(csv.DictReader(f), start=1):
            if i > args.top_n:
                break
            name = str(row.get("applicant_name") or "").strip()
            if not name or name in existing:
                continue
            existing[name] = {c: "" for c in COLUMNS}
            existing[name]["applicant_name"] = name
            added += 1

    ordered: list[dict[str, str]] = []
    seen: set[str] = set()
    with args.p12.open("r", encoding="utf-8-sig", newline="") as f:
        for i, row in enumerate(csv.DictReader(f), start=1):
            if i > args.top_n:
                break
            name = str(row.get("applicant_name") or "").strip()
            if not name or name not in existing or name in seen:
                continue
            ordered.append({c: str(existing[name].get(c) or "") for c in COLUMNS})
            ordered[-1]["applicant_name"] = name
            seen.add(name)

    args.map.parent.mkdir(parents=True, exist_ok=True)
    with args.map.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(ordered)

    filled = sum(1 for r in ordered if str(r.get("applicant_city") or "").strip())
    print(
        {
            "top_n": args.top_n,
            "rows": len(ordered),
            "added": added,
            "with_city": filled,
            "path": str(args.map),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
