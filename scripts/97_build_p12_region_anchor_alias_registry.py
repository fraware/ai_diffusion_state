"""Build runtime exact-alias registry from P12 applicants with a single region anchor."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.region_anchors import single_region_anchor  # noqa: E402
from diffusion_state.top_applicant_institutions import is_foreign_applicant  # noqa: E402

DEFAULT_P12 = ROOT / "outputs/tables/table_P12_top_iids_applicants.csv"
DEFAULT_OUT = ROOT / "data/seed/p12_region_anchor_aliases.json"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--p12", type=Path, default=DEFAULT_P12)
    p.add_argument("--output", type=Path, default=DEFAULT_OUT)
    p.add_argument("--top-n", type=int, default=25000, help="P12 rows (0 = all)")
    args = p.parse_args()

    aliases: dict[str, dict[str, str]] = {}
    with args.p12.open("r", encoding="utf-8-sig", newline="") as f:
        import csv

        for i, row in enumerate(csv.DictReader(f), start=1):
            if args.top_n and i > args.top_n:
                break
            name = str(row.get("applicant_name") or "").strip()
            if not name or is_foreign_applicant(name):
                continue
            upper = re.sub(r"\s+", " ", name.upper())
            anchor = single_region_anchor(upper)
            if not anchor:
                continue
            token, city, province = anchor
            conf = (
                "university_location"
                if upper.startswith("UNIV ") or upper.startswith("INST ")
                else "official_headquarters_page"
            )
            aliases[name] = {
                "applicant_city": city,
                "applicant_province": province,
                "geo_match_confidence": conf,
                "geo_notes": f"P12 region anchor '{token}' (generated registry).",
            }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(aliases, indent=2, ensure_ascii=False), encoding="utf-8")
    print({"top_n": args.top_n, "aliases": len(aliases), "output": str(args.output)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
