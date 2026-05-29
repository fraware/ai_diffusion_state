"""Fill blank top_applicant_city_map rows using single-hit region-anchor rules."""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.region_anchors import single_region_anchor  # noqa: E402
from diffusion_state.top_applicant_institutions import is_foreign_applicant  # noqa: E402

DEFAULT_MAP = ROOT / "data/seed/top_applicant_city_map.csv"


def _confidence(name: str) -> str:
    upper = re.sub(r"\s+", " ", name.upper())
    if upper.startswith("UNIV ") or upper.startswith("INST "):
        return "university_location"
    if "GRID" in upper or "POWER" in upper:
        return "official_headquarters_page"
    return "official_headquarters_page"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--map", type=Path, default=DEFAULT_MAP)
    args = p.parse_args()

    rows: list[dict[str, str]] = []
    filled = 0
    with args.map.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        for row in reader:
            name = str(row.get("applicant_name") or "").strip()
            has_city = bool(str(row.get("applicant_city") or "").strip())
            if not has_city and name and not is_foreign_applicant(name):
                upper = re.sub(r"\s+", " ", name.upper())
                anchor = single_region_anchor(upper)
                if anchor:
                    token, city, province = anchor
                    row["applicant_city"] = city
                    row["applicant_province"] = province
                    row["geo_match_confidence"] = _confidence(name)
                    row["source_url"] = "region_anchor_rules"
                    row["notes"] = f"Single region anchor '{token}' (auto-seeded)."
                    filled += 1
            rows.append(row)

    with args.map.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    with_city = sum(1 for r in rows if str(r.get("applicant_city") or "").strip())
    print({"anchor_fills": filled, "total_with_city": with_city, "rows": len(rows)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
