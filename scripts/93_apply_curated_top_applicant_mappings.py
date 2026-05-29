"""Apply curated institution registry to top_applicant_city_map (no overwrite)."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.top_applicant_institutions import (  # noqa: E402
    CURATED_LOCATIONS,
    is_foreign_applicant,
)

MAP_PATH = ROOT / "data/seed/top_applicant_city_map.csv"
P15_PATH = ROOT / "outputs/tables/table_P15_applicant_manual_mapping_priority.csv"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--map", type=Path, default=MAP_PATH)
    p.add_argument("--max-new", type=int, default=0, help="Cap new fills (0=all)")
    p.add_argument("--min-priority", choices=("high", "medium", "any"), default="high")
    p.add_argument(
        "--scope",
        choices=("priority", "map"),
        default="priority",
        help="priority=P15 filter; map=any applicant row present in the map file",
    )
    p.add_argument("--mark-foreign", action="store_true", default=True)
    args = p.parse_args()

    allowed: set[str] | None = None
    if args.scope == "map" or args.min_priority == "any":
        allowed = None
    elif P15_PATH.exists():
        allowed = set()
        with P15_PATH.open("r", encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                pr = str(row.get("manual_mapping_priority") or "")
                if args.min_priority == "high" and pr != "high":
                    continue
                if args.min_priority == "medium" and pr not in {"high", "medium"}:
                    continue
                allowed.add(str(row.get("applicant_name") or "").strip())

    rows: list[dict[str, str]] = []
    new_fills = 0
    foreign_marked = 0
    skipped_existing = 0

    with args.map.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        for row in reader:
            name = str(row.get("applicant_name") or "").strip()
            has_city = bool(str(row.get("applicant_city") or "").strip())

            if not has_city and args.mark_foreign and is_foreign_applicant(name):
                row["notes"] = "Foreign parent entity; not mapped to CN city for Atlas."
                foreign_marked += 1
            elif (
                not has_city
                and name in CURATED_LOCATIONS
                and (allowed is None or name in allowed)
            ):
                if args.max_new and new_fills >= args.max_new:
                    pass
                else:
                    city, prov, url, conf, notes = CURATED_LOCATIONS[name]
                    row["applicant_city"] = city
                    row["applicant_province"] = prov
                    row["source_url"] = url
                    row["geo_match_confidence"] = conf
                    row["notes"] = notes
                    new_fills += 1
            elif has_city and name in CURATED_LOCATIONS:
                skipped_existing += 1

            rows.append(row)

    with args.map.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(
        {
            "new_fills": new_fills,
            "skipped_existing": skipped_existing,
            "foreign_marked": foreign_marked,
            "total_with_city": sum(
                1 for r in rows if str(r.get("applicant_city") or "").strip()
            ),
            "path": str(args.map),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
