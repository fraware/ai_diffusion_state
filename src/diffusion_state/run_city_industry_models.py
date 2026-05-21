from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from diffusion_state.build_industry_ai_exposure import build_industry_ai_exposure
from diffusion_state.build_industry_ai_exposure_ex_ante import build_industry_ai_exposure_ex_ante
from diffusion_state.utils import PROJECT_ROOT, write_csv

OUTPUT_TABLES = PROJECT_ROOT / "outputs" / "tables"


def run_city_industry_adoption_models(
    panel_path: Path | None = None,
) -> pd.DataFrame:
    panel_path = panel_path or PROJECT_ROOT / "data" / "processed" / "analysis_city_industry_year_panel.csv"
    if not panel_path.exists():
        from diffusion_state.build_analysis_city_industry_panel import (
            build_analysis_city_industry_year_panel,
        )

        build_analysis_city_industry_year_panel()

    ex_ante_path = PROJECT_ROOT / "data" / "processed" / "industry_ai_exposure_ex_ante.csv"
    if not ex_ante_path.exists():
        build_industry_ai_exposure_ex_ante()

    tag_path = PROJECT_ROOT / "data" / "processed" / "industry_ai_exposure.csv"
    if not tag_path.exists():
        build_industry_ai_exposure()

    panel = pd.read_csv(panel_path)
    ex_ante = pd.read_csv(ex_ante_path)
    tag_exposure = pd.read_csv(tag_path)

    panel = panel.merge(
        ex_ante[
            [
                "industry_code",
                "ai_exposure_ex_ante",
                "high_exposure_ex_ante",
                "ai_exposure_ex_ante_tier",
            ]
        ],
        on="industry_code",
        how="left",
    )
    panel = panel.merge(
        tag_exposure[
            ["industry_code", "ai_exposure_score", "ai_exposure_tier", "high_exposure_sector"]
        ],
        on="industry_code",
        how="left",
        suffixes=("", "_tag"),
    )
    panel = panel[panel["year"].isin((2024, 2025))].copy()
    panel["log1p_projects"] = np.log1p(panel["smart_factory_projects"])

    rows = []
    specs = [
        (
            "city_industry_post_pilot",
            "log1p_projects ~ post_pilot + C(city) + C(industry_code) + C(year)",
            "city, industry, and year FE (exploratory)",
            "ex_ante",
        ),
        (
            "city_industry_pilot_x_exposure_ex_ante",
            "log1p_projects ~ pilot_zone * high_exposure_ex_ante + C(city) + C(industry_code) + C(year)",
            "pilot x high-exposure industry (ex ante classification)",
            "ex_ante",
        ),
        (
            "city_industry_pilot_x_score_ex_ante",
            "log1p_projects ~ pilot_zone * ai_exposure_ex_ante + C(city) + C(industry_code) + C(year)",
            "pilot x continuous ex ante AI exposure",
            "ex_ante",
        ),
        (
            "city_industry_pilot_x_exposure_tag_descriptive",
            "log1p_projects ~ pilot_zone * high_exposure_sector + C(city) + C(industry_code) + C(year)",
            "pilot x tag-derived high exposure (descriptive only; outcome-built)",
            "descriptive_tag_derived",
        ),
        (
            "city_industry_pilot_x_score_tag_descriptive",
            "log1p_projects ~ pilot_zone * ai_exposure_score + C(city) + C(industry_code) + C(year)",
            "pilot x tag-derived exposure score (descriptive only)",
            "descriptive_tag_derived",
        ),
    ]

    for model_name, formula, note, exposure_source in specs:
        sub = panel.dropna(subset=["city", "industry_code", "log1p_projects"])
        if len(sub) < 30 or sub["city"].nunique() < 5:
            rows.append(
                {
                    "term": "skipped",
                    "coef": f"insufficient observations (n={len(sub)})",
                    "std_err": np.nan,
                    "p_value": np.nan,
                    "n_obs": len(sub),
                    "r_squared": np.nan,
                    "model": model_name,
                    "formula": formula,
                    "note": note,
                    "exposure_source": exposure_source,
                }
            )
            continue
        try:
            fit = smf.ols(formula, data=sub).fit(
                cov_type="cluster",
                cov_kwds={"groups": sub["city"]},
            )
            for term in fit.params.index:
                rows.append(
                    {
                        "term": term,
                        "coef": fit.params[term],
                        "std_err": fit.bse[term],
                        "p_value": fit.pvalues[term],
                        "n_obs": int(fit.nobs),
                        "r_squared": fit.rsquared,
                        "model": model_name,
                        "formula": formula,
                        "note": note,
                        "exposure_source": exposure_source,
                    }
                )
        except Exception as exc:  # noqa: BLE001
            rows.append(
                {
                    "term": "error",
                    "coef": str(exc),
                    "std_err": np.nan,
                    "p_value": np.nan,
                    "n_obs": len(sub),
                    "r_squared": np.nan,
                    "model": model_name,
                    "formula": formula,
                    "note": note,
                    "exposure_source": exposure_source,
                }
            )

    out = pd.DataFrame(rows)
    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
    write_csv(out, OUTPUT_TABLES / "table_13_city_industry_adoption_models.csv")
    return out
