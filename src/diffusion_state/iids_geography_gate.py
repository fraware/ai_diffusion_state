"""IIDS patent geography readiness gate for Atlas evidence chain."""
from __future__ import annotations

import csv
from pathlib import Path

from diffusion_state.iids_geo_join import (
    MIN_CITY_FILL,
    MIN_PROVINCE_FILL,
    KEY_COVERAGE_MIN_RATE,
    is_geography_template_path,
    load_geography_lookup,
    summarize_geography,
)
from diffusion_state.iids_geo_stream import measure_geography_key_coverage
from diffusion_state.iids_paths import (
    DEFAULT_GEO_OUTPUT,
    DEFAULT_IIDS_OUTPUT,
    FILTERED_PATENT_IDS_FOR_GEO_OUTPUT,
)
from diffusion_state.patent_raw_sources import is_real_export_filename

DEFAULT_CITY_PROVINCE_THRESHOLD = MIN_CITY_FILL
GEO_CONTRACT_COLUMNS = (
    "patent_id",
    "applicant_city",
    "applicant_province",
    "applicant_address",
    "geo_source",
    "geo_match_confidence",
    "geo_notes",
)


def _file_nonempty(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 0


def _csv_header(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        return next(reader, [])


def _count_csv_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
        return max(sum(1 for _ in csv.reader(f)) - 1, 0)


def collect_iids_geography_gate(
    *,
    iids_csv: Path | None = None,
    keys_csv: Path | None = None,
    geography_csv: Path | None = None,
    min_city_fill: float = DEFAULT_CITY_PROVINCE_THRESHOLD,
    min_province_fill: float = MIN_PROVINCE_FILL,
    min_key_match_rate: float = KEY_COVERAGE_MIN_RATE,
) -> dict:
    """Return IIDS geography procurement / evidence readiness flags."""
    iids_csv = iids_csv or DEFAULT_IIDS_OUTPUT
    keys_csv = keys_csv or FILTERED_PATENT_IDS_FOR_GEO_OUTPUT
    geography_csv = geography_csv or DEFAULT_GEO_OUTPUT
    iids_present = _file_nonempty(iids_csv) and is_real_export_filename(iids_csv.name)
    keys_present = _file_nonempty(keys_csv)
    n_keys_expected = _count_csv_rows(keys_csv) if keys_present else 0
    geo_path = geography_csv if geography_csv.exists() else None
    geo_present = bool(geo_path and not is_geography_template_path(geo_path))
    geo_is_template = bool(geo_path and is_geography_template_path(geo_path))

    city_fill = province_fill = key_match_rate = 0.0
    geo_rows = 0
    geo_validation_issues: list[str] = []
    geo_contract_ok = False
    coverage_stats: dict[str, float | int] = {}

    if geo_present and geo_path is not None:
        try:
            header = [c.strip() for c in _csv_header(geo_path)]
            geo_contract_ok = all(c in header for c in GEO_CONTRACT_COLUMNS) or all(
                c in header
                for c in (
                    "patent_id",
                    "applicant_city",
                    "applicant_province",
                    "applicant_address",
                )
            )
            lookup = load_geography_lookup(geo_path)
            file_stats = summarize_geography(lookup)
            geo_rows = int(file_stats.get("rows", 0))

            if keys_present:
                coverage_stats = measure_geography_key_coverage(geo_path, keys_csv)
                city_fill = float(coverage_stats.get("city_fill_rate", 0.0))
                province_fill = float(coverage_stats.get("province_fill_rate", 0.0))
                key_match_rate = float(coverage_stats.get("key_match_rate", 0.0))
            else:
                city_fill = float(file_stats.get("city_fill_rate", 0.0))
                province_fill = float(file_stats.get("province_fill_rate", 0.0))
                key_match_rate = 1.0
        except Exception as exc:
            geo_validation_issues = [f"geography file unreadable: {exc}"]

    fill_ok = (
        city_fill >= min_city_fill
        and province_fill >= min_province_fill
        and key_match_rate >= min_key_match_rate
    )
    iids_patent_export_ready = iids_present
    iids_geography_ready = bool(
        geo_present and geo_contract_ok and fill_ok and geo_rows > 0 and keys_present
    )
    ready_for_geography_procurement = bool(iids_patent_export_ready and keys_present)
    ready_for_evidence_chain = bool(
        iids_patent_export_ready and keys_present and iids_geography_ready
    )

    if not iids_patent_export_ready:
        recommended_next = "Import opendatalab_iids_industrial_ai_patents_2015_2024_part1.csv"
    elif not keys_present:
        recommended_next = "python scripts/66_export_iids_patent_keys.py --production"
    elif not geo_present:
        recommended_next = (
            "Export geography per docs/ATLAS_IIDS_GEOGRAPHY_PROCUREMENT_BRIEF.md; "
            "make atlas-iids-geo-key-batches; build cnipa_patent_geography_2015_2024.csv"
        )
    elif not iids_geography_ready:
        recommended_next = (
            "Improve cnipa_patent_geography_2015_2024.csv: "
            f"city>={min_city_fill:.0%} province>={min_province_fill:.0%} "
            f"key_match>={min_key_match_rate:.0%} on IIDS keys"
        )
    else:
        recommended_next = "make atlas-iids-control-evidence-chain"

    return {
        "iids_patent_export_ready": iids_patent_export_ready,
        "iids_geography_keys_ready": keys_present,
        "iids_geography_ready": iids_geography_ready,
        "geography_present": geo_present,
        "geography_is_template": geo_is_template,
        "geography_contract_ok": geo_contract_ok,
        "geography_city_fill_rate": round(city_fill, 4),
        "geography_province_fill_rate": round(province_fill, 4),
        "geography_key_match_rate": round(key_match_rate, 4),
        "geography_rows": geo_rows,
        "geography_key_rows_expected": n_keys_expected,
        "geography_fill_threshold": min_city_fill,
        "geography_key_coverage": coverage_stats,
        "ready_for_geography_procurement": ready_for_geography_procurement,
        "ready_for_evidence_chain": ready_for_evidence_chain,
        "real_iids_patent_export_present": iids_patent_export_ready,
        "recommended_next": recommended_next,
        "geography_validation_issues": geo_validation_issues,
        "artifact_paths": {
            "iids_csv": str(iids_csv),
            "keys_csv": str(keys_csv),
            "geography_csv": str(geography_csv),
        },
    }
