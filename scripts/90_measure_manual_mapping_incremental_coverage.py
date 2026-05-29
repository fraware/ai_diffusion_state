"""Measure incremental coverage from manual top-applicant mappings (table P13)."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.china_city_gazetteer import first_applicant_name  # noqa: E402

DEFAULT_IIDS = ROOT / "data/raw/patents/opendatalab_iids_industrial_ai_patents_2015_2024_part1.csv"
DEFAULT_NAME_INFERRED = (
    ROOT / "data/raw/patents/cnipa_patent_geography_2015_2024_applicant_name_inferred.csv"
)
DEFAULT_TOP_MAP = ROOT / "data/seed/top_applicant_city_map.csv"
DEFAULT_OUTPUT = ROOT / "outputs/tables/table_P13_manual_mapping_incremental_coverage.csv"

P13_COLUMNS = [
    "manual_applicants_total",
    "manual_applicants_with_city",
    "patents_with_manual_applicant",
    "manual_patents_already_name_token_covered",
    "manual_patents_incremental",
    "manual_incremental_share",
    "name_token_city_fill",
    "tiered_city_fill_after_manual",
]


def _load_manual_filled(path: Path) -> dict[str, dict[str, str]]:
    filled: dict[str, dict[str, str]] = {}
    total = 0
    if not path.exists():
        return filled
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
        for row in csv.DictReader(f):
            total += 1
            name = str(row.get("applicant_name") or "").strip()
            city = str(row.get("applicant_city") or "").strip()
            if name and city:
                filled[name] = row
    return filled


def _load_name_token_patent_ids(path: Path) -> set[str]:
    ids: set[str] = set()
    if not path.exists():
        return ids
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
        for row in csv.DictReader(f):
            conf = str(row.get("geo_match_confidence") or "").strip()
            city = str(row.get("applicant_city") or "").strip()
            if conf == "applicant_name_city_token" and city:
                pid = str(row.get("patent_id") or "").strip()
                if pid:
                    ids.add(pid)
    return ids


def measure(
    *,
    iids_csv: Path,
    name_inferred_csv: Path,
    top_map_csv: Path,
) -> dict[str, float | int]:
    manual_filled = _load_manual_filled(top_map_csv)
    manual_applicants_total = 0
    manual_applicants_with_city = len(manual_filled)

    with top_map_csv.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
        manual_applicants_total = sum(1 for _ in csv.DictReader(f))

    name_token_ids = _load_name_token_patent_ids(name_inferred_csv)

    n_iids = 0
    n_name_token = 0
    patents_with_manual = 0
    manual_already = 0
    manual_incremental = 0

    with iids_csv.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
        for row in csv.DictReader(f):
            n_iids += 1
            pid = str(row.get("patent_id") or "").strip()
            app = first_applicant_name(str(row.get("applicant_name") or ""))

            if pid in name_token_ids:
                n_name_token += 1

            if app in manual_filled:
                patents_with_manual += 1
                if pid in name_token_ids:
                    manual_already += 1
                else:
                    manual_incremental += 1

            if n_iids % 500_000 == 0:
                print("processed", n_iids, flush=True)

    name_token_fill = n_name_token / n_iids if n_iids else 0.0
    tiered_after = (n_name_token + manual_incremental) / n_iids if n_iids else 0.0
    manual_share = manual_incremental / n_iids if n_iids else 0.0

    return {
        "manual_applicants_total": manual_applicants_total,
        "manual_applicants_with_city": manual_applicants_with_city,
        "patents_with_manual_applicant": patents_with_manual,
        "manual_patents_already_name_token_covered": manual_already,
        "manual_patents_incremental": manual_incremental,
        "manual_incremental_share": round(manual_share, 6),
        "name_token_city_fill": round(name_token_fill, 6),
        "tiered_city_fill_after_manual": round(tiered_after, 6),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--iids", type=Path, default=DEFAULT_IIDS)
    p.add_argument("--name-inferred", type=Path, default=DEFAULT_NAME_INFERRED)
    p.add_argument("--top-map", type=Path, default=DEFAULT_TOP_MAP)
    p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = p.parse_args()

    if not args.iids.exists():
        print(f"ERROR: missing {args.iids}", file=sys.stderr)
        return 1

    stats = measure(
        iids_csv=args.iids,
        name_inferred_csv=args.name_inferred,
        top_map_csv=args.top_map,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=P13_COLUMNS)
        writer.writeheader()
        writer.writerow(stats)

    print(stats)
    print("wrote", args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
