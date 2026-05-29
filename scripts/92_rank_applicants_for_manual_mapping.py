"""Rank top applicants by incremental manual-mapping value (table P15)."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.china_city_gazetteer import (  # noqa: E402
    first_applicant_name,
    match_city_from_applicant_name,
)

DEFAULT_P12 = ROOT / "outputs/tables/table_P12_top_iids_applicants.csv"
DEFAULT_NAME_INFERRED = (
    ROOT / "data/raw/patents/cnipa_patent_geography_2015_2024_applicant_name_inferred.csv"
)
DEFAULT_IIDS = ROOT / "data/raw/patents/opendatalab_iids_industrial_ai_patents_2015_2024_part1.csv"
DEFAULT_OUTPUT = ROOT / "outputs/tables/table_P15_applicant_manual_mapping_priority.csv"

FOREIGN_MARKERS = (
    "SAMSUNG",
    "LG ",
    "LG CHEMICAL",
    "LG DISPLAY",
    "LG ELECTRONICS",
    "TOYOTA",
    "QUALCOMM",
    "INTEL ",
    "INTEL CORP",
    "MICROSOFT",
    "SONY",
    "FORD ",
    "GM GLOBAL",
    "HONDA",
    "CANON",
    "FANUC",
    "BOSCH",
    "PANASONIC",
    "MITSUBISHI",
    "ERICSSON",
    "TOKYO ELECTRON",
    "TAIWAN SEMICONDUCTOR",
    "SEMICONDUCTOR MFG INT",
    "NOKIA",
    "NXP",
    "APPLE INC",
    "GOOGLE",
    "AMAZON",
    "HEWLETT",
    "ORACLE",
    "NVIDIA",
)


def is_foreign(name: str) -> bool:
    upper = name.upper()
    return any(m in upper for m in FOREIGN_MARKERS)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--p12", type=Path, default=DEFAULT_P12)
    p.add_argument("--iids", type=Path, default=DEFAULT_IIDS)
    p.add_argument("--name-inferred", type=Path, default=DEFAULT_NAME_INFERRED)
    p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    p.add_argument("--top-n", type=int, default=500)
    args = p.parse_args()

    top_names: list[str] = []
    with args.p12.open("r", encoding="utf-8-sig", newline="") as f:
        for i, row in enumerate(csv.DictReader(f)):
            if i >= args.top_n:
                break
            name = str(row.get("applicant_name") or "").strip()
            if name:
                top_names.append(name)

    top_set = set(top_names)
    name_token_ids: set[str] = set()
    with args.name_inferred.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if str(row.get("geo_match_confidence") or "").strip() != "applicant_name_city_token":
                continue
            if str(row.get("applicant_city") or "").strip():
                pid = str(row.get("patent_id") or "").strip()
                if pid:
                    name_token_ids.add(pid)

    stats: dict[str, dict[str, int | str | bool]] = {
        n: {
            "applicant_name": n,
            "patent_count": 0,
            "already_name_token_covered": 0,
            "incremental_patents": 0,
            "has_city_token_in_name": bool(match_city_from_applicant_name(n)),
            "is_foreign": is_foreign(n),
        }
        for n in top_names
    }

    with args.iids.open("r", encoding="utf-8-sig", newline="") as f:
        for i, row in enumerate(csv.DictReader(f)):
            app = first_applicant_name(str(row.get("applicant_name") or ""))
            if app not in top_set:
                continue
            stats[app]["patent_count"] = int(stats[app]["patent_count"]) + 1
            pid = str(row.get("patent_id") or "").strip()
            if pid in name_token_ids:
                stats[app]["already_name_token_covered"] = (
                    int(stats[app]["already_name_token_covered"]) + 1
                )
            if i and i % 500_000 == 0:
                print("processed", i, flush=True)

    rows: list[dict[str, object]] = []
    for name in top_names:
        s = stats[name]
        patents = int(s["patent_count"])
        covered = int(s["already_name_token_covered"])
        incremental = patents - covered
        s["incremental_patents"] = incremental
        s["incremental_share_of_applicant"] = round(incremental / patents, 4) if patents else 0.0
        rows.append(s)

    rows.sort(key=lambda r: int(r["incremental_patents"]), reverse=True)

    fieldnames = [
        "applicant_name",
        "patent_count",
        "already_name_token_covered",
        "incremental_patents",
        "incremental_share_of_applicant",
        "has_city_token_in_name",
        "is_foreign",
        "manual_mapping_priority",
    ]
    for row in rows:
        if row["is_foreign"]:
            row["manual_mapping_priority"] = "skip_foreign"
        elif row["has_city_token_in_name"]:
            row["manual_mapping_priority"] = "low_token_likely_covered"
        elif int(row["incremental_patents"]) >= 1000:
            row["manual_mapping_priority"] = "high"
        elif int(row["incremental_patents"]) > 0:
            row["manual_mapping_priority"] = "medium"
        else:
            row["manual_mapping_priority"] = "low"

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    high = sum(1 for r in rows if r["manual_mapping_priority"] == "high")
    print({"top_n": args.top_n, "high_priority_applicants": high, "output": str(args.output)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
