from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from diffusion_state.utils import PROJECT_ROOT

STUB_SOURCE_MARKERS = ("pipeline_ci_stub_not_for_paper", "city_controls_ci_stub", "STUB_NOTE")

ADOPTION_YEARS = (2024, 2025)
PRE_TREATMENT_YEAR = 2018

CONTROL_VARS = [
    "gdp",
    "population",
    "secondary_value_added",
    "industrial_output",
    "fdi",
    "fixed_asset_investment",
    "telecom_or_internet_proxy",
    "education_proxy",
    "foreign_trade",
    "average_wage",
]

DERIVED_CONTROL_COLS = [
    "log_gdp",
    "log_population",
    "log_fdi",
    "log_fixed_asset_investment",
    "secondary_industry_share",
]

MODEL_CONTROL_TERMS = [
    "log_gdp",
    "log_population",
    "secondary_industry_share",
    "log_fdi",
    "log_fixed_asset_investment",
    "telecom_or_internet_proxy",
]

MIN_NONMISSING_FOR_ADOPTION = [
    "log_gdp",
    "log_population",
    "secondary_industry_share",
    "log_fdi",
    "log_fixed_asset_investment",
    "telecom_or_internet_proxy",
]

TIMING_DIAGNOSTIC_NOTE = (
    "Pre-2024 coefficients are mechanical because excellence-level smart-factory outcomes "
    "are observed only from 2024 onward. This figure is a timing diagnostic, not a "
    "pre-trend validation."
)


def _safe_log(series: pd.Series) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    return np.log(np.where(s > 0, s, np.nan))


def add_derived_controls(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["log_gdp"] = _safe_log(out["gdp"]) if "gdp" in out.columns else np.nan
    out["log_population"] = _safe_log(out["population"]) if "population" in out.columns else np.nan
    out["log_fdi"] = _safe_log(out["fdi"]) if "fdi" in out.columns else np.nan
    out["log_fixed_asset_investment"] = (
        _safe_log(out["fixed_asset_investment"]) if "fixed_asset_investment" in out.columns else np.nan
    )
    if "gdp" in out.columns and "secondary_value_added" in out.columns:
        gdp = pd.to_numeric(out["gdp"], errors="coerce")
        sec = pd.to_numeric(out["secondary_value_added"], errors="coerce")
        out["secondary_industry_share"] = np.where(gdp > 0, sec / gdp, np.nan)
    else:
        out["secondary_industry_share"] = np.nan
    return out


def controls_available(
    panel: pd.DataFrame,
    years: tuple[int, ...] = ADOPTION_YEARS,
    min_vars: list[str] | None = None,
) -> bool:
    if city_controls_source() != "production":
        return False
    min_vars = min_vars or MIN_NONMISSING_FOR_ADOPTION
    sample = panel[panel["year"].isin(years)]
    if sample.empty:
        return False
    for col in min_vars:
        if col not in sample.columns or sample[col].notna().sum() == 0:
            return False
    return True


def adoption_sample_with_controls(panel: pd.DataFrame) -> pd.DataFrame:
    sample = panel[panel["year"].isin(ADOPTION_YEARS)].copy()
    sample = add_derived_controls(sample)
    req = MIN_NONMISSING_FOR_ADOPTION + ["city", "province", "smart_factory_projects", "pilot_zone"]
    return sample.dropna(subset=[c for c in req if c in sample.columns])


NON_PRODUCTION_RAW_MARKERS = ("ci_stub", "ingest_template")


def _is_production_raw_file(path: Path) -> bool:
    name = path.name.lower()
    return not any(m in name for m in NON_PRODUCTION_RAW_MARKERS)


def _controls_csv_paths() -> list[Path]:
    raw = PROJECT_ROOT / "data" / "raw" / "city_controls"
    if not raw.exists():
        return []
    files = list(raw.glob("*.csv")) + list(raw.glob("*.xlsx")) + list(raw.glob("*.xls"))
    return [p for p in files if _is_production_raw_file(p)]


def city_controls_source() -> str:
    """Return production, stub, or missing for merged city controls."""
    processed = PROJECT_ROOT / "data" / "processed" / "city_controls_year.csv"
    if processed.exists():
        df = pd.read_csv(processed)
        if "source_name" in df.columns:
            names = df["source_name"].astype(str)
            if names.str.contains(STUB_SOURCE_MARKERS[0], case=False, na=False).any():
                return "stub"
            if names.notna().any() and (names.str.strip() != "").any():
                return "production"
    raw = _controls_csv_paths()
    if not raw:
        return "missing"
    return "production"


def typology_control_source(panel: pd.DataFrame | None = None) -> str:
    """Controls backing ex ante typology: real_city_controls or no_controls (never stub)."""
    if city_controls_source() == "production" and panel is not None and controls_available(panel):
        return "real_city_controls"
    return "no_controls"


def purge_stub_city_controls() -> list[str]:
    """Remove CI stub files and processed controls built from them."""
    removed: list[str] = []
    raw = PROJECT_ROOT / "data" / "raw" / "city_controls"
    if raw.exists():
        for path in list(raw.glob("*")):
            if path.is_file() and (
                "ci_stub" in path.name.lower() or path.name.lower().startswith("city_controls_ci_stub")
            ):
                path.unlink()
                removed.append(str(path.relative_to(PROJECT_ROOT)))
    processed = PROJECT_ROOT / "data" / "processed" / "city_controls_year.csv"
    if processed.exists():
        names = pd.read_csv(processed, usecols=["source_name"])["source_name"].astype(str)
        if names.str.contains(STUB_SOURCE_MARKERS[0], case=False, na=False).any():
            processed.unlink()
            removed.append(str(processed.relative_to(PROJECT_ROOT)))
    miss = PROJECT_ROOT / "data" / "processed" / "city_controls_missingness.csv"
    if miss.exists() and not processed.exists():
        miss.unlink()
        removed.append(str(miss.relative_to(PROJECT_ROOT)))
    return removed
