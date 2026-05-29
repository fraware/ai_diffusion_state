"""Merge tiered patent geography: exact external > manual top applicant > name token."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.iids_geography_normalize import CONTRACT_COLUMNS  # noqa: E402

DEFAULT_KEYS = ROOT / "data/raw/patents/iids_filtered_patent_ids_for_geography.csv"
DEFAULT_NAME_INFERRED = (
    ROOT / "data/raw/patents/cnipa_patent_geography_2015_2024_applicant_name_inferred.csv"
)
DEFAULT_TOP_MAP = ROOT / "data/seed/top_applicant_city_map.csv"
DEFAULT_EXTERNAL_GLOB = "cnipa_patent_geography_2015_2024_external*.csv"
DEFAULT_OUTPUT = ROOT / "data/raw/patents/cnipa_patent_geography_2015_2024.csv"

EXACT_CONFIDENCE_PREFIXES = (
    "exact_publication_number",
    "exact_publication_number_address_parsed",
)

MANUAL_CONFIDENCE = frozenset(
    {
        "official_headquarters_page",
        "university_location",
        "public_registry_address",
        "manually_curated_top_applicant",
    }
)

NAME_TOKEN_CONFIDENCE = "applicant_name_city_token"


def _non_empty(val: str) -> bool:
    return bool(str(val or "").strip())


def _load_csv_by_patent(path: Path, key_col: str = "patent_id") -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    out: dict[str, dict[str, str]] = {}
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
        for row in csv.DictReader(f):
            pid = str(row.get(key_col) or row.get("publication_number") or "").strip()
            if pid:
                out[pid] = row
    return out


def _load_top_applicant_map(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    out: dict[str, dict[str, str]] = {}
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
        for row in csv.DictReader(f):
            name = str(row.get("applicant_name") or "").strip()
            city = str(row.get("applicant_city") or "").strip()
            if not name or not city:
                continue
            out[name] = row
    return out


def _is_exact_tier(confidence: str) -> bool:
    c = str(confidence or "").strip()
    return any(c.startswith(p) for p in EXACT_CONFIDENCE_PREFIXES) and c != "not_found"


def _row_from_manual(name: str, manual: dict[str, str]) -> dict[str, str]:
    conf = str(manual.get("geo_match_confidence") or "manually_curated_top_applicant").strip()
    city = str(manual.get("applicant_city") or "").strip()
    province = str(manual.get("applicant_province") or "").strip()
    source_url = str(manual.get("source_url") or "").strip()
    notes = str(manual.get("notes") or "").strip()
    return {
        "applicant_city": city,
        "applicant_province": province,
        "applicant_address": f"{city}, {province}, CN (curated top applicant)",
        "geo_source": source_url or "top_applicant_city_map.csv",
        "geo_match_confidence": conf,
        "geo_notes": notes or f"Curated mapping for applicant: {name[:120]}",
    }


def _blank_row() -> dict[str, str]:
    return {c: "" for c in CONTRACT_COLUMNS if c != "patent_id"}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--keys", type=Path, default=DEFAULT_KEYS)
    p.add_argument("--name-inferred", type=Path, default=DEFAULT_NAME_INFERRED)
    p.add_argument("--top-map", type=Path, default=DEFAULT_TOP_MAP)
    p.add_argument("--external", type=Path, default=None, help="Exact external geography CSV")
    p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    p.add_argument("--iids", type=Path, default=ROOT / "data/raw/patents/opendatalab_iids_industrial_ai_patents_2015_2024_part1.csv")
    args = p.parse_args()

    if not args.keys.exists():
        print(f"ERROR: missing keys {args.keys}", file=sys.stderr)
        return 1

    external_path = args.external
    if external_path is None:
        candidates = sorted((ROOT / "data/raw/patents").glob(DEFAULT_EXTERNAL_GLOB))
        external_path = candidates[0] if candidates else None

    external = _load_csv_by_patent(external_path) if external_path else {}
    name_geo = _load_csv_by_patent(args.name_inferred)
    top_map = _load_top_applicant_map(args.top_map)

    # patent_id -> applicant_name from IIDS (streaming)
    applicant_by_patent: dict[str, str] = {}
    if args.iids.exists() and top_map:
        with args.iids.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
            for row in csv.DictReader(f):
                pid = str(row.get("patent_id") or "").strip()
                if pid and pid not in applicant_by_patent:
                    applicant_by_patent[pid] = str(row.get("applicant_name") or "").strip()

    tier_counts: dict[str, int] = {}
    n_keys = 0
    n_city = 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.keys.open("r", encoding="utf-8-sig", errors="replace", newline="") as f_keys:
        reader = csv.DictReader(f_keys)
        with args.output.open("w", encoding="utf-8-sig", newline="") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=list(CONTRACT_COLUMNS))
            writer.writeheader()

            for key_row in reader:
                pid = str(
                    key_row.get("patent_id")
                    or key_row.get("publication_number")
                    or ""
                ).strip()
                if not pid:
                    continue
                n_keys += 1

                merged = _blank_row()
                tier = "unresolved"

                ext = external.get(pid, {})
                ext_conf = str(ext.get("geo_match_confidence") or "").strip()
                if ext and _is_exact_tier(ext_conf) and _non_empty(ext.get("applicant_city", "")):
                    merged = {c: str(ext.get(c, "") or "").strip() for c in CONTRACT_COLUMNS if c != "patent_id"}
                    tier = "exact_publication_number"

                if tier == "unresolved":
                    app_name = applicant_by_patent.get(pid, "")
                    first = app_name.split(";")[0].split("|")[0].split(",")[0].strip()
                    manual = top_map.get(first, {})
                    if manual:
                        merged = _row_from_manual(first, manual)
                        tier = "manually_curated_top_applicant"

                if tier == "unresolved":
                    inferred = name_geo.get(pid, {})
                    inf_conf = str(inferred.get("geo_match_confidence") or "").strip()
                    if inf_conf == NAME_TOKEN_CONFIDENCE and _non_empty(
                        inferred.get("applicant_city", "")
                    ):
                        merged = {
                            c: str(inferred.get(c, "") or "").strip()
                            for c in CONTRACT_COLUMNS
                            if c != "patent_id"
                        }
                        tier = NAME_TOKEN_CONFIDENCE

                writer.writerow({"patent_id": pid, **merged})
                tier_counts[tier] = tier_counts.get(tier, 0) + 1
                if _non_empty(merged.get("applicant_city", "")):
                    n_city += 1

    print(
        {
            "keys": n_keys,
            "city_fill": round(n_city / max(n_keys, 1), 4),
            "tier_counts": tier_counts,
            "external_rows": len(external),
            "name_inferred_rows": len(name_geo),
            "top_map_applicants": len(top_map),
            "output": str(args.output),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
