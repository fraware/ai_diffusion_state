"""Memory-efficient city-industry-year panel from reconstructed IIDS export."""
from __future__ import annotations

import csv
import re
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

from diffusion_state.patent_city_normalize import normalize_city, normalize_province
from diffusion_state.english_applicant_industry_rules import match_english_industry
from diffusion_state.patent_industry_map import load_industry_crosswalk
from diffusion_state.utils import contains_any, normalize_cn_text, read_yaml

YEAR_MIN = 2015
YEAR_MAX = 2024
PRIMARY_CONFIDENCE = frozenset({"high", "medium"})
INDUSTRY_MAPPING_PATH = Path(__file__).resolve().parents[2] / "configs" / "industry_mapping.yml"


@lru_cache(maxsize=1)
def _default_industry() -> tuple[str, str, str]:
    """IIDS export is pre-filtered industrial-AI; use medium for panel aggregation."""
    cfg = read_yaml(INDUSTRY_MAPPING_PATH)
    default = cfg.get("default", {})
    return (
        str(default.get("industry_code", "C34")),
        str(default.get("industry_label", "general_equipment")),
        "medium",
    )


@lru_cache(maxsize=1)
def _ipc_prefix_map() -> dict[str, tuple[str, str, str]]:
    """IPC prefix -> (code, label, confidence)."""
    out: dict[str, tuple[str, str, str]] = {}
    crosswalk = load_industry_crosswalk()
    for _, row in crosswalk.iterrows():
        prefixes = str(row.get("ipc_prefixes", "")).split(",")
        conf = str(row.get("mapping_confidence_default", "medium"))
        code = str(row["industry_code"])
        label = str(row.get("industry", row.get("industry_label", code)))
        for p in prefixes:
            p = p.strip().upper()
            if p and p not in out:
                out[p] = (code, label, conf)
    return out


def _ipc_prefix(ipc_or_cpc: str) -> str:
    text = str(ipc_or_cpc or "").strip().upper()
    m = re.match(r"([A-H]\d{2})", text)
    return m.group(1) if m else ""


@lru_cache(maxsize=1)
def _keyword_rules() -> tuple[tuple[tuple[str, ...], str, str, str], ...]:
    rules: list[tuple[tuple[str, ...], str, str, str]] = []
    crosswalk = load_industry_crosswalk()
    for _, row in crosswalk.iterrows():
        patterns = tuple(
            p.strip() for p in str(row.get("keyword_patterns", "")).split(",") if p.strip()
        )
        if not patterns:
            continue
        conf = str(row.get("mapping_confidence_default", "medium"))
        code = str(row["industry_code"])
        label = str(row.get("industry", row.get("industry_label", code)))
        rules.append((patterns, code, label, conf))
    return tuple(rules)


def _fast_industry_map(
    title: str,
    applicant_name: str,
    ipc_or_cpc: str,
) -> tuple[str, str, str]:
    prefix = _ipc_prefix(ipc_or_cpc)
    if prefix:
        hit = _ipc_prefix_map().get(prefix)
        if hit:
            return hit
    upper = f"{applicant_name} {title}".upper()
    en_hit = match_english_industry(upper)
    if en_hit:
        return en_hit
    text = normalize_cn_text(f"{title} {applicant_name}")
    for patterns, code, label, conf in _keyword_rules():
        if text and contains_any(text, patterns):
            return code, label, conf
    return _default_industry()


def _analysis_year(application_year: str, publication_year: str) -> int | None:
    for raw in (publication_year, application_year):
        text = str(raw or "").strip()
        if not text or text.lower() in {"nan", "none"}:
            continue
        try:
            y = int(float(text))
        except ValueError:
            continue
        if YEAR_MIN <= y <= YEAR_MAX:
            return y
    return None


def aggregate_iids_export_streaming(
    iids_csv: Path,
    *,
    chunksize: int = 250_000,
) -> tuple[list[dict[str, object]], dict[str, int]]:
    """Return panel rows and summary stats without materializing full long table."""
    _ipc_prefix_map()
    _default_industry()

    counts: dict[tuple[str, str, str, str, int], int] = defaultdict(int)
    n_rows = 0
    n_with_city = 0
    n_in_panel = 0

    with iids_csv.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        batch: list[dict[str, str]] = []
        for row in reader:
            batch.append(row)
            if len(batch) < chunksize:
                continue
            n_rows, n_with_city, n_in_panel = _consume_batch(
                batch, counts, n_rows, n_with_city, n_in_panel
            )
            batch = []
            print({"rows": n_rows, "panel_patents": n_in_panel}, flush=True)
        if batch:
            n_rows, n_with_city, n_in_panel = _consume_batch(
                batch, counts, n_rows, n_with_city, n_in_panel
            )

    panel: list[dict[str, object]] = []
    for (city, province, industry_code, industry, year), n in counts.items():
        panel.append(
            {
                "city": city,
                "province": province,
                "industry": industry,
                "industry_code": industry_code,
                "year": year,
                "ai_patents": n,
                "industrial_ai_patents": n,
                "source": "opendatalab_iids",
                "coverage_note": "iids_streaming_tiered_robustness",
            }
        )

    stats = {
        "n_rows": n_rows,
        "n_with_city": n_with_city,
        "n_panel_patents": n_in_panel,
        "n_panel_cells": len(panel),
        "city_fill_rate": round(n_with_city / max(n_rows, 1), 4),
    }
    return panel, stats


def _consume_batch(
    batch: list[dict[str, str]],
    counts: dict[tuple[str, str, str, str, int], int],
    n_rows: int,
    n_with_city: int,
    n_in_panel: int,
) -> tuple[int, int, int]:
    for row in batch:
        n_rows += 1
        city, prov_from_city, _evidence = normalize_city(
            str(row.get("applicant_city") or ""),
            str(row.get("applicant_province") or ""),
            str(row.get("applicant_address") or ""),
        )
        if not city:
            continue
        n_with_city += 1
        province = prov_from_city or normalize_province(str(row.get("applicant_province") or ""))
        year = _analysis_year(
            str(row.get("application_year") or ""),
            str(row.get("publication_year") or ""),
        )
        if year is None:
            continue

        code, label, conf = _fast_industry_map(
            str(row.get("patent_title") or ""),
            str(row.get("applicant_name") or ""),
            str(row.get("ipc_or_cpc") or ""),
        )
        if conf not in PRIMARY_CONFIDENCE:
            continue

        key = (city, province, code, label, year)
        counts[key] += 1
        n_in_panel += 1

    return n_rows, n_with_city, n_in_panel
