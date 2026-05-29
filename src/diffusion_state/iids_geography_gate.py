"""IIDS patent geography readiness gate for Atlas evidence chain."""
from __future__ import annotations

import csv
from pathlib import Path

from diffusion_state.iids_geo_join import (
    MIN_CITY_FILL,
    MIN_PROVINCE_FILL,
    TIERED_ROBUSTNESS_MIN_FILL,
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
TIERED_GEO_FILENAME = "cnipa_patent_geography_2015_2024.csv"
NAME_INFERRED_GEO = (
    Path(__file__).resolve().parents[2]
    / "data/raw/patents/cnipa_patent_geography_2015_2024_applicant_name_inferred.csv"
)

EXACT_CONFIDENCE_PREFIXES = (
    "exact_publication_number",
)

TIERED_CONFIDENCE_VALUES = frozenset(
    {
        "applicant_name_city_token",
        "manually_curated_top_applicant",
        "official_headquarters_page",
        "university_location",
        "public_registry_address",
        "ambiguous_unresolved",
    }
)

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


def _confidence_tier_counts(geo_path: Path, keys_csv: Path) -> dict[str, int | float]:
    """Count geo_match_confidence tiers on the IIDS key list."""
    geo_by_pid: dict[str, dict[str, str]] = {}
    with geo_path.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
        for row in csv.DictReader(f):
            pid = str(row.get("patent_id") or row.get("publication_number") or "").strip()
            if pid and pid not in geo_by_pid:
                geo_by_pid[pid] = row

    key_ids: list[str] = []
    with keys_csv.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
        for row in csv.DictReader(f):
            pid = str(row.get("patent_id") or row.get("publication_number") or "").strip()
            if pid:
                key_ids.append(pid)

    tier_counts: dict[str, int] = {}
    n_exact_city = 0
    n_tiered_city = 0
    n_city = 0

    for pid in key_ids:
        geo = geo_by_pid.get(pid, {})
        conf = str(geo.get("geo_match_confidence") or "").strip() or "unresolved"
        city = str(geo.get("applicant_city") or "").strip()
        tier_counts[conf] = tier_counts.get(conf, 0) + 1
        if city:
            n_city += 1
            if any(conf.startswith(p) for p in EXACT_CONFIDENCE_PREFIXES) and conf != "not_found":
                n_exact_city += 1
            elif conf in TIERED_CONFIDENCE_VALUES or conf.startswith("applicant_name"):
                n_tiered_city += 1

    n_keys = len(key_ids) or 1
    return {
        "n_keys": len(key_ids),
        "n_city_on_keys": n_city,
        "n_exact_city_on_keys": n_exact_city,
        "n_tiered_city_on_keys": n_tiered_city,
        "exact_city_share_on_keys": round(n_exact_city / n_keys, 4),
        "tiered_city_share_on_keys": round(n_tiered_city / n_keys, 4),
        "tier_counts": tier_counts,
    }


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

    tier_stats: dict[str, int | float] = {}
    exact_geography_ready = False
    tiered_geography_ready = False
    if geo_present and geo_path is not None and keys_present:
        try:
            tier_stats = _confidence_tier_counts(geo_path, keys_csv)
            exact_share = float(tier_stats.get("exact_city_share_on_keys", 0.0))
            tiered_share = float(tier_stats.get("tiered_city_share_on_keys", 0.0))
            # Exact-ready: coverage thresholds met AND majority of geocoded keys are exact-tier.
            exact_geography_ready = bool(
                fill_ok and exact_share >= min_city_fill * 0.95
            )
            # Tiered-ready: coverage thresholds on keys; allows name-token + curated tiers.
            tiered_geography_ready = bool(
                fill_ok
                and (exact_share + tiered_share) >= min_city_fill
            )
        except Exception as exc:
            geo_validation_issues.append(f"tier audit failed: {exc}")

    iids_patent_export_ready = iids_present
    # Preserve strict flag: exact publication-number geography only.
    iids_geography_ready = bool(
        geo_present
        and geo_contract_ok
        and exact_geography_ready
        and geo_rows > 0
        and keys_present
    )
    ready_for_geography_procurement = bool(iids_patent_export_ready and keys_present)
    ready_for_evidence_chain = bool(
        iids_patent_export_ready and keys_present and iids_geography_ready
    )
    ready_for_tiered_evidence_chain = bool(
        iids_patent_export_ready and keys_present and tiered_geography_ready
    )
    tiered_robustness_ready = bool(
        iids_patent_export_ready
        and keys_present
        and city_fill >= TIERED_ROBUSTNESS_MIN_FILL
        and province_fill >= TIERED_ROBUSTNESS_MIN_FILL
        and key_match_rate >= min_key_match_rate
    )
    ready_for_tiered_robustness_patent_layer = bool(
        iids_patent_export_ready and keys_present and tiered_robustness_ready
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
    elif tiered_robustness_ready and not tiered_geography_ready:
        recommended_next = (
            f"Tiered robustness frozen at {city_fill:.1%} ({TIERED_ROBUSTNESS_MIN_FILL:.0%}+). "
            "Diagnostics: make atlas-iids-frozen-verify. "
            "Procurement: make atlas-iids-procurement-priority-unresolved then "
            "make atlas-iids-external-geo-pipeline; evidence: make atlas-iids-control-evidence-chain."
        )
    elif tiered_geography_ready and not iids_geography_ready:
        recommended_next = (
            "Tiered geography meets 80% tiered gate (ready_for_tiered_evidence_chain). "
            "Exact chain still requires external exact_publication_number* geography. "
            "Do not claim exact publication-number geocoding."
        )
    elif not tiered_geography_ready:
        recommended_next = (
            "Build tiered geography: make atlas-iids-applicant-concentration; "
            "make atlas-iids-name-geography; make atlas-iids-tiered-geography-merge; "
            f"target city>={min_city_fill:.0%} on IIDS keys"
        )
    else:
        recommended_next = "make atlas-iids-control-evidence-chain"

    return {
        "iids_patent_export_ready": iids_patent_export_ready,
        "iids_geography_keys_ready": keys_present,
        "iids_geography_ready": iids_geography_ready,
        "exact_geography_ready": exact_geography_ready,
        "tiered_geography_ready": tiered_geography_ready,
        "ready_for_tiered_evidence_chain": ready_for_tiered_evidence_chain,
        "tiered_robustness_ready": tiered_robustness_ready,
        "ready_for_tiered_robustness_patent_layer": ready_for_tiered_robustness_patent_layer,
        "tiered_robustness_fill_threshold": TIERED_ROBUSTNESS_MIN_FILL,
        "geography_tier_stats": tier_stats,
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
