from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from diffusion_state.atlas_model_estimation import (
    NOT_SUPPORTED_CLAIMS,
    prep_patent_sample,
    run_patent_model_suite,
    run_robot_complementarity_models,
)
from diffusion_state.utils import PROJECT_ROOT, write_csv

OUTPUT_TABLES = PROJECT_ROOT / "outputs" / "tables"
FIGURES = PROJECT_ROOT / "outputs" / "figures"

EVENT_K = [-4, -3, -2, -1, 0, 1, 2, 3, 4]
OMIT_K = -1


def _event_col(k: int) -> str:
    return f"event_k_m{abs(k)}" if k < 0 else f"event_k_{k}"


def run_patent_event_study(panel: pd.DataFrame) -> pd.DataFrame:
    data = prep_patent_sample(panel)
    data = data[data["pilot_zone"] == 1].copy()
    data = data[data["years_since_pilot"].isin(EVENT_K)]
    rows: list[dict] = []
    for k in EVENT_K:
        if k == OMIT_K:
            continue
        col = _event_col(k)
        data[col] = ((data["years_since_pilot"] == k).astype(int) * data["ai_exposure_ex_ante"])
    event_terms = " + ".join(_event_col(k) for k in EVENT_K if k != OMIT_K)
    formula = (
        f"industrial_ai_patents ~ {event_terms} + "
        "C(city_industry) + C(province_year) + C(industry_year)"
    )
    try:
        fit = smf.ols(formula, data=data).fit(
            cov_type="cluster", cov_kwds={"groups": data["city"]}
        )
        outcome = data["industrial_ai_patents"]
        n_nonzero = int((outcome > 0).sum())
        for k in EVENT_K:
            if k == OMIT_K:
                continue
            term = _event_col(k)
            se = float(fit.bse[term]) if term in fit.bse else np.nan
            p = float(fit.pvalues[term]) if term in fit.pvalues else np.nan
            status = "ok" if np.isfinite(se) and np.isfinite(p) else "failed_covariance"
            rows.append(
                {
                    "model": "atlas_event_study_patents",
                    "term": term,
                    "coef": float(fit.params[term]),
                    "std_err": se,
                    "p_value": p,
                    "n_obs": int(fit.nobs),
                    "n_nonzero_outcome": n_nonzero,
                    "n_cities": int(data["city"].nunique()),
                    "n_industries": int(data["industry_code"].nunique()),
                    "years": ",".join(str(int(y)) for y in sorted(data["year"].unique())),
                    "fixed_effects": "city_industry, province_year, industry_year",
                    "sample_rule": "pilot_cities_event_window",
                    "estimator_status": status,
                    "claim_tier": "associational_exploratory" if status == "ok" else "not_supported",
                    "interpretation": f"Event-time coefficient k={k} (omitted k=-1) x AI exposure.",
                    "not_supported_claims": NOT_SUPPORTED_CLAIMS,
                }
            )
    except Exception as exc:
        rows.append(
            {
                "model": "atlas_event_study_patents",
                "term": "event_study",
                "coef": np.nan,
                "std_err": np.nan,
                "p_value": np.nan,
                "n_obs": len(data),
                "n_nonzero_outcome": int((data["industrial_ai_patents"] > 0).sum()),
                "n_cities": int(data["city"].nunique()),
                "n_industries": int(data["industry_code"].nunique()),
                "years": "",
                "fixed_effects": "city_industry, province_year, industry_year",
                "sample_rule": "failed_fit",
                "estimator_status": "failed_covariance",
                "claim_tier": "not_supported",
                "interpretation": str(exc),
                "not_supported_claims": NOT_SUPPORTED_CLAIMS,
            }
        )
    return pd.DataFrame(rows)


def run_smart_factory_models(panel: pd.DataFrame) -> pd.DataFrame:
    from diffusion_state.atlas_model_estimation import ModelSpec, fit_interaction_model

    data = panel[panel["smart_factory_count"].notna()].copy()
    data["city_industry"] = data["city"].astype(str) + "__" + data["industry_code"].astype(str)
    data["industry_year"] = data["industry_code"].astype(str) + "__" + data["year"].astype(str)
    data["post_x_exposure"] = data["post_pilot"] * data["ai_exposure_ex_ante"]
    data = data.dropna(subset=["ai_exposure_ex_ante"])
    data["log1p_projects"] = np.log1p(data["smart_factory_count"].clip(lower=0))

    specs = [
        ModelSpec(
            "pilot_x_ai_exposure_smart_factories_ols_count",
            "smart_factory_count",
            "post_x_exposure",
            "C(city_industry) + C(industry_year)",
            "city_industry, industry_year",
            "atlas_sf_years_present",
            "ols",
        ),
        ModelSpec(
            "pilot_x_ai_exposure_smart_factories_ols_log1p",
            "log1p_projects",
            "post_x_exposure",
            "C(city_industry) + C(industry_year)",
            "city_industry, industry_year",
            "atlas_sf_years_present",
            "ols",
        ),
        ModelSpec(
            "pilot_x_ai_exposure_smart_factories_poisson",
            "smart_factory_count",
            "post_x_exposure",
            "C(city_industry) + C(industry_year)",
            "city_industry, industry_year",
            "atlas_sf_years_present",
            "poisson",
        ),
    ]
    return pd.DataFrame(
        [
            fit_interaction_model(
                data,
                s,
            )
            for s in specs
        ]
    )


def _plot_event_study(event_df: pd.DataFrame, out_path: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return
    coef_rows = event_df[
        (event_df["term"].str.startswith("event_k_"))
        & (event_df["estimator_status"] == "ok")
    ].copy()
    if coef_rows.empty:
        return

    def _parse_k(term: str) -> int:
        if term.startswith("event_k_m"):
            return -int(term.replace("event_k_m", ""))
        return int(term.replace("event_k_", ""))

    ks = [_parse_k(t) for t in coef_rows["term"]]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.errorbar(ks, coef_rows["coef"], yerr=1.96 * coef_rows["std_err"], fmt="o-")
    ax.axhline(0, color="gray", linewidth=0.8)
    ax.set_xlabel("Years since pilot")
    ax.set_ylabel("Coefficient (x AI exposure)")
    ax.set_title("Industrial AI patents — event study (pilot cities)")
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def run_atlas_models_v02(
    atlas_path: Path | None = None,
) -> dict[str, pd.DataFrame]:
    atlas_path = atlas_path or (
        PROJECT_ROOT / "data" / "processed" / "china_ai_diffusion_atlas_city_industry_year.csv"
    )
    panel = pd.read_csv(atlas_path)
    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)

    patent_suite = run_patent_model_suite(panel)
    f0 = patent_suite["F0"]
    f1a = patent_suite["F1a"]
    f1b = patent_suite["F1b"]
    f1c = patent_suite["F1c"]
    f1_legacy = patent_suite["F1_legacy"]

    f2 = run_robot_complementarity_models(panel)
    f3 = run_smart_factory_models(panel)
    f4 = run_patent_event_study(panel)

    write_csv(f0, OUTPUT_TABLES / "table_F0_atlas_model_diagnostics.csv")
    write_csv(f1a, OUTPUT_TABLES / "table_F1a_pilot_x_ai_exposure_patents_baseline.csv")
    write_csv(f1b, OUTPUT_TABLES / "table_F1b_pilot_x_ai_exposure_patents_fe_ladder.csv")
    write_csv(f1c, OUTPUT_TABLES / "table_F1c_pilot_x_ai_exposure_patents_saturated.csv")
    write_csv(f1_legacy, OUTPUT_TABLES / "table_F1_pilot_x_ai_exposure_patents.csv")
    write_csv(f2, OUTPUT_TABLES / "table_F2_robot_complementarity_patents.csv")
    write_csv(f3, OUTPUT_TABLES / "table_F3_pilot_x_ai_exposure_smart_factories.csv")
    write_csv(f4, OUTPUT_TABLES / "table_F4_atlas_event_study_patents.csv")
    _plot_event_study(f4, FIGURES / "fig_F1_patent_event_study.png")

    return {
        "F0": f0,
        "F1a": f1a,
        "F1b": f1b,
        "F1c": f1c,
        "F1": f1_legacy,
        "F2": f2,
        "F3": f3,
        "F4": f4,
    }
