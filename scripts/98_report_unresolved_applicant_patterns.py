"""Report top unresolved first-applicant patterns for procurement (table P16)."""
from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.tiered_geography_resolve import (  # noqa: E402
    UNRESOLVED_LABEL,
    resolve_tiered_geography,
)

DEFAULT_IIDS = ROOT / "data/raw/patents/opendatalab_iids_industrial_ai_patents_2015_2024_part1.csv"
DEFAULT_MAP = ROOT / "data/seed/top_applicant_city_map.csv"
DEFAULT_OUT = ROOT / "outputs/tables/table_P16_unresolved_applicant_patterns.csv"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--iids", type=Path, default=DEFAULT_IIDS)
    p.add_argument("--top-map", type=Path, default=DEFAULT_MAP)
    p.add_argument("--output", type=Path, default=DEFAULT_OUT)
    p.add_argument("--limit", type=int, default=2_000_000)
    p.add_argument("--top-k", type=int, default=200)
    args = p.parse_args()

    top_map: dict[str, dict[str, str]] = {}
    with args.top_map.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            name = str(row.get("applicant_name") or "").strip()
            if name and str(row.get("applicant_city") or "").strip():
                top_map[name] = row

    from diffusion_state.applicant_name_parsing import first_applicant_name

    counts: Counter[str] = Counter()
    n = 0
    with args.iids.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            n += 1
            pid = str(row.get("patent_id") or "").strip()
            app = str(row.get("applicant_name") or "")
            _, tier = resolve_tiered_geography(
                patent_id=pid, applicant_name=app, external={}, top_map=top_map
            )
            if tier == UNRESOLVED_LABEL:
                first = first_applicant_name(app) or "(blank)"
                counts[first] += 1
            if n >= args.limit:
                break
            if n % 500_000 == 0:
                print("processed", n, flush=True)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["applicant_name", "unresolved_patent_count", "share_of_unresolved"]
        )
        writer.writeheader()
        total_unres = sum(counts.values())
        for name, cnt in counts.most_common(args.top_k):
            writer.writerow(
                {
                    "applicant_name": name,
                    "unresolved_patent_count": cnt,
                    "share_of_unresolved": round(cnt / total_unres, 6) if total_unres else 0,
                }
            )

    print(
        {
            "rows_scanned": n,
            "unresolved": total_unres,
            "unresolved_rate": round(total_unres / max(n, 1), 4),
            "output": str(args.output),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
