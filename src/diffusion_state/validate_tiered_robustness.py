"""Validation gates for tiered IIDS robustness extension (60%+ geography, not publication F1)."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from diffusion_state.utils import PROJECT_ROOT

YEAR_MIN = 2015
YEAR_MAX = 2024
TIERED_MIN_CITIES = 50
TIERED_MIN_INDUSTRIES = 5
TIERED_MIN_INDUSTRIES_WITH_PATENTS = 10
TIERED_MIN_PATENTS = 500_000
TIERED_MIN_CITY_FILL = 0.60
TIERED_YEAR_END_MIN = 2020
TIERED_MIN_DISTINCT_YEARS = 6


def validate_tiered_robustness_panel(
    panel_path: Path | None = None,
) -> tuple[bool, list[str]]:
    panel_path = panel_path or (
        PROJECT_ROOT / "data" / "processed" / "industrial_ai_patents_city_industry_year.csv"
    )
    issues: list[str] = []

    if not panel_path.exists():
        return False, [f"MISSING panel: {panel_path}"]

    panel = pd.read_csv(panel_path)
    if panel.empty:
        return False, ["Panel is empty"]

    required = {"city", "province", "industry_code", "industry", "year", "industrial_ai_patents"}
    missing = required - set(panel.columns)
    if missing:
        issues.append(f"Panel missing columns: {sorted(missing)}")

    total = int(panel["industrial_ai_patents"].sum())
    if total < TIERED_MIN_PATENTS:
        issues.append(f"Panel patent count {total:,} below {TIERED_MIN_PATENTS:,}")

    n_cities = int(panel["city"].nunique())
    if n_cities < TIERED_MIN_CITIES:
        issues.append(f"Only {n_cities} cities (need {TIERED_MIN_CITIES}+)")

    n_inds = int(panel["industry_code"].nunique())
    if n_inds < TIERED_MIN_INDUSTRIES:
        issues.append(f"Only {n_inds} industries (need {TIERED_MIN_INDUSTRIES}+)")

    years = panel["year"].dropna().astype(int)
    if len(years):
        if years.min() < YEAR_MIN or years.max() > YEAR_MAX:
            issues.append(f"Years outside {YEAR_MIN}-{YEAR_MAX}: {years.min()}-{years.max()}")

    if panel.duplicated(subset=["city", "industry_code", "year"]).any():
        issues.append("Duplicate city-industry-year keys")

    return len(issues) == 0, issues


def validate_industrial_ai_patents_phase1_tiered(
    panel_path: Path | None = None,
) -> list[str]:
    """Phase-1 checks for streaming IIDS panel (no long ingest or taxonomy categories)."""
    panel_path = panel_path or (
        PROJECT_ROOT / "data" / "processed" / "industrial_ai_patents_city_industry_year.csv"
    )
    ok, issues = validate_tiered_robustness_panel(panel_path)
    if not ok:
        return issues

    panel = pd.read_csv(panel_path)
    errors: list[str] = []

    null_keys = panel[
        panel["city"].isna()
        | panel["province"].isna()
        | panel["industry_code"].isna()
        | panel["year"].isna()
    ]
    if len(null_keys):
        errors.append(f"{len(null_keys)} rows missing city/province/industry/year")

    years = panel["year"].dropna().astype(int)
    if years.min() > YEAR_MIN:
        errors.append(f"panel starts after {YEAR_MIN}: min year {int(years.min())}")
    if years.max() < TIERED_YEAR_END_MIN:
        errors.append(
            f"panel ends before {TIERED_YEAR_END_MIN}: max year {int(years.max())} "
            "(reconstructed IIDS may omit late years until SQL re-convert)"
        )
    if years.nunique() < TIERED_MIN_DISTINCT_YEARS:
        errors.append(
            f"need {TIERED_MIN_DISTINCT_YEARS}+ distinct years; got {int(years.nunique())}"
        )

    cities_nz = panel.groupby("city")["industrial_ai_patents"].sum()
    if int((cities_nz > 0).sum()) < TIERED_MIN_CITIES:
        errors.append(f"need {TIERED_MIN_CITIES}+ cities with patents")

    inds_nz = panel.groupby("industry_code")["industrial_ai_patents"].sum()
    if int((inds_nz > 0).sum()) < TIERED_MIN_INDUSTRIES_WITH_PATENTS:
        errors.append(
            f"need {TIERED_MIN_INDUSTRIES_WITH_PATENTS}+ industries with patents; "
            f"got {int((inds_nz > 0).sum())}"
        )

    return errors


def validate_tiered_robustness_geography(gate: dict[str, object]) -> tuple[bool, list[str]]:
    issues: list[str] = []
    fill = float(gate.get("geography_city_fill_rate") or 0.0)
    if fill < TIERED_MIN_CITY_FILL:
        issues.append(f"Geography city fill {fill:.1%} below {TIERED_MIN_CITY_FILL:.0%}")
    if not gate.get("tiered_robustness_ready"):
        issues.append("tiered_robustness_ready is false")
    if not gate.get("ready_for_tiered_robustness_patent_layer"):
        issues.append("ready_for_tiered_robustness_patent_layer is false")
    return len(issues) == 0, issues
