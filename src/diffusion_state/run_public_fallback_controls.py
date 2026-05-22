from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from diffusion_state.model_utils import fit_ols_table, fit_poisson_table
from diffusion_state.panel_controls import add_derived_controls
from diffusion_state.utils import PROJECT_ROOT, write_csv

OUTPUT_TABLES = PROJECT_ROOT / "outputs" / "tables"

PUBLIC_FALLBACK_TERMS = [
    "log_gdp",
    "log_population",
    "secondary_industry_share",
    "foreign_trade_log1p",
    "telecom_log1p",
    "industrial_output_log1p",
]


def _safe_log1p(series: pd.Series) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    return np.log1p(np.where(s >= 0, s, np.nan))


def _skipped(reason: str) -> pd.DataFrame:
    return pd.DataFrame([
        {
            "term": "skipped",
            "coef": reason,
            "std_err": np.nan,
            "t_stat": np.nan,
            "p_value": np.nan,
            "n_obs": 0,
            "r_squared": np.nan,
            "model": "public_fallback_controls_missing",
            "formula": "",
            "sample_rule": "none",
            "n_cities": 0,
            "years": "",
            "fixed_effects": "",
            "controls_included": "",
            "evidence_tier": "partial_public_controls_appendix_only",
            "paper_use": "appendix robustness only; not EPS-equivalent Table 5",
        }
    ])


def prepare_public_fallback_sample(panel: pd.DataFrame) -> pd.DataFrame:
    df = add_derived_controls(panel).copy()
    df["foreign_trade_log1p"] = _safe_log1p(df["foreign_trade"]) if "foreign_trade" in df else np.nan
    df["telecom_log1p"] = _safe_log1p(df["telecom_or_internet_proxy"]) if "telecom_or_internet_proxy" in df else np.nan
    df["industrial_output_log1p"] = _safe_log1p(df["industrial_output"]) if "industrial_output" in df else np.nan
    df["log1p_projects"] = np.log1p(pd.to_numeric(df["smart_factory_projects"], errors="coerce"))
    # ChinaUTC public fallback currently has meaningful adoption-year control coverage mainly in 2024.
    # 2025 is not used unless future public tables are added.
    df = df[df["year"].isin([2024])].copy()
    required_core = ["city", "smart_factory_projects", "pilot_zone", "log_gdp", "log_population", "secondary_industry_share"]
    df = df.dropna(subset=[c for c in required_core if c in df.columns])
    return df


def run_public_fallback_controls(panel_path: Path | None = None) -> pd.DataFrame:
    panel_path = panel_path or PROJECT_ROOT / "data" / "processed" / "analysis_city_year_panel.csv"
    panel = pd.read_csv(panel_path)
    sample = prepare_public_fallback_sample(panel)
    if sample.empty or sample["city"].nunique() < 20:
        out = _skipped("insufficient ChinaUTC public-fallback controls in 2024")
        OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
        write_csv(out, OUTPUT_TABLES / "table_5b_public_fallback_controls.csv")
        return out

    # Include only controls with non-trivial variation in the actual sample.
    usable_terms = []
    for term in PUBLIC_FALLBACK_TERMS:
        if term in sample.columns and sample[term].notna().sum() >= 20 and sample[term].nunique(dropna=True) > 1:
            usable_terms.append(term)
    base_terms = ["log_gdp", "log_population", "secondary_industry_share"]
    usable_terms = [t for t in usable_terms if t in base_terms] + [t for t in usable_terms if t not in base_terms]
    if not set(base_terms).issubset(set(usable_terms)):
        out = _skipped("core public fallback controls missing: log_gdp/log_population/secondary_industry_share")
        OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
        write_csv(out, OUTPUT_TABLES / "table_5b_public_fallback_controls.csv")
        return out

    ctrl = " + ".join(usable_terms)
    meta = {
        "evidence_tier": "partial_public_controls_appendix_only",
        "paper_use": "appendix robustness only; not EPS-equivalent Table 5",
        "control_source": "ChinaUTC public China City Statistical Yearbook fallback, units as reported",
        "missing_controls": "FDI and fixed-asset investment unavailable in current public fallback",
    }
    results = []
    specs = [
        (
            "model_5b_public_fallback_count_2024",
            f"smart_factory_projects ~ pilot_zone + {ctrl}",
            fit_ols_table,
        ),
        (
            "model_5c_public_fallback_log_count_2024",
            f"log1p_projects ~ pilot_zone + {ctrl}",
            fit_ols_table,
        ),
        (
            "model_5d_public_fallback_poisson_2024",
            f"smart_factory_projects ~ pilot_zone + {ctrl}",
            fit_poisson_table,
        ),
    ]
    for model, formula, fitter in specs:
        if fitter is fit_ols_table:
            results.append(fitter(
                formula,
                sample,
                model=model,
                sample_rule="chinautc_public_fallback_2024_only",
                fixed_effects="none; single year",
                controls_included=ctrl,
                extra_meta=meta,
            ))
        else:
            tbl = fitter(
                formula,
                sample,
                model=model,
                sample_rule="chinautc_public_fallback_2024_only",
                fixed_effects="none; single year",
                controls_included=ctrl,
            )
            for k, v in meta.items():
                tbl[k] = v
            results.append(tbl)
    out = pd.concat(results, ignore_index=True)
    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
    write_csv(out, OUTPUT_TABLES / "table_5b_public_fallback_controls.csv")
    return out


if __name__ == "__main__":
    run_public_fallback_controls()
