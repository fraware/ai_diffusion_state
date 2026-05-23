from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from diffusion_state.utils import PROJECT_ROOT, write_csv

OUTPUT_TABLES = PROJECT_ROOT / "outputs" / "tables"
FIGURES = PROJECT_ROOT / "outputs" / "figures"

EVENT_K = [-4, -3, -2, -1, 0, 1, 2, 3, 4]
OMIT_K = -1


def _atlas_model_row(
    fit,
    term: str,
    *,
    model: str,
    fixed_effects: str,
    sample_rule: str,
    claim_tier: str,
    interpretation: str,
    not_supported: str,
    data: pd.DataFrame,
) -> dict:
    return {
        "model": model,
        "term": term,
        "coef": float(fit.params[term]),
        "std_err": float(fit.bse[term]),
        "p_value": float(fit.pvalues[term]),
        "n_obs": int(fit.nobs),
        "n_cities": int(data["city"].nunique()),
        "n_industries": int(data["industry_code"].nunique()),
        "years": ",".join(str(int(y)) for y in sorted(data["year"].unique())),
        "fixed_effects": fixed_effects,
        "sample_rule": sample_rule,
        "claim_tier": claim_tier,
        "interpretation": interpretation,
        "not_supported_claims": not_supported,
    }


def _prep_patent_sample(panel: pd.DataFrame) -> pd.DataFrame:
    df = panel.copy()
    df = df[df["industrial_ai_patents"].notna()]
    df["city_industry"] = df["city"].astype(str) + "__" + df["industry_code"].astype(str)
    df["province_year"] = df["province"].astype(str) + "__" + df["year"].astype(str)
    df["industry_year"] = df["industry_code"].astype(str) + "__" + df["year"].astype(str)
    df["log1p_patents"] = np.log1p(df["industrial_ai_patents"].clip(lower=0))
    df["post_x_exposure"] = df["post_pilot"] * df["ai_exposure_ex_ante"]
    df["post_x_exposure_x_robot"] = (
        df["post_pilot"] * df["ai_exposure_ex_ante"] * df["robot_compatibility"]
    )
    return df.dropna(subset=["ai_exposure_ex_ante", "robot_compatibility"])


def _fit_interaction_specs(
    data: pd.DataFrame,
    *,
    dep: str,
    interaction: str,
    model_prefix: str,
    fixed_effects: str,
    fe_formula: str,
) -> pd.DataFrame:
    rows = []
    base_formula = f"{dep} ~ {interaction} + {fe_formula}"
    not_supported = (
        "causal productivity; export upgrading; procurement commercial output; "
        "economy-wide productivity shock"
    )
    for est, fitter in (
        ("ols_count", lambda f, d: smf.ols(f, data=d).fit(cov_type="cluster", cov_kwds={"groups": d["city"]})),
        ("ols_log1p", lambda f, d: smf.ols(f, data=d).fit(cov_type="cluster", cov_kwds={"groups": d["city"]})),
        ("poisson", lambda f, d: smf.poisson(f, data=d).fit(cov_type="cluster", cov_kwds={"groups": d["city"]}, disp=False)),
    ):
        dep_var = dep
        if est == "ols_log1p":
            dep_var = "log1p_patents" if dep == "industrial_ai_patents" else f"log1p_{dep}"
            if dep_var not in data.columns and dep == "smart_factory_count":
                data = data.assign(log1p_projects=np.log1p(data["smart_factory_count"].clip(lower=0)))
                dep_var = "log1p_projects"
        formula = base_formula.replace(dep, dep_var) if est == "ols_log1p" else base_formula
        try:
            fit = fitter(formula, data)
            rows.append(
                _atlas_model_row(
                    fit,
                    interaction,
                    model=f"{model_prefix}_{est}",
                    fixed_effects=fixed_effects,
                    sample_rule="atlas_city_industry_year_patent_years",
                    claim_tier="associational_exploratory",
                    interpretation="Pilot-zone × ex-ante AI exposure association with industrial AI outcomes.",
                    not_supported=not_supported,
                    data=data,
                )
            )
        except Exception as exc:
            rows.append(
                {
                    "model": f"{model_prefix}_{est}",
                    "term": interaction,
                    "coef": np.nan,
                    "std_err": np.nan,
                    "p_value": np.nan,
                    "n_obs": len(data),
                    "n_cities": data["city"].nunique(),
                    "n_industries": data["industry_code"].nunique(),
                    "years": "",
                    "fixed_effects": fixed_effects,
                    "sample_rule": "failed_fit",
                    "claim_tier": "associational_exploratory",
                    "interpretation": str(exc),
                    "not_supported_claims": not_supported,
                }
            )
    return pd.DataFrame(rows)


def run_patent_pilot_exposure_models(panel: pd.DataFrame) -> pd.DataFrame:
    data = _prep_patent_sample(panel)
    fe = "C(city_industry) + C(province_year) + C(industry_year)"
    return _fit_interaction_specs(
        data,
        dep="industrial_ai_patents",
        interaction="post_x_exposure",
        model_prefix="pilot_x_ai_exposure_patents",
        fixed_effects="city_industry, province_year, industry_year",
        fe_formula=fe,
    )


def run_robot_complementarity_models(panel: pd.DataFrame) -> pd.DataFrame:
    data = _prep_patent_sample(panel)
    fe = "C(city_industry) + C(province_year) + C(industry_year)"
    return _fit_interaction_specs(
        data,
        dep="industrial_ai_patents",
        interaction="post_x_exposure_x_robot",
        model_prefix="robot_complementarity_patents",
        fixed_effects="city_industry, province_year, industry_year",
        fe_formula=fe,
    )


def run_smart_factory_models(panel: pd.DataFrame) -> pd.DataFrame:
    data = panel[panel["smart_factory_count"].notna()].copy()
    data["city_industry"] = data["city"].astype(str) + "__" + data["industry_code"].astype(str)
    data["industry_year"] = data["industry_code"].astype(str) + "__" + data["year"].astype(str)
    data["post_x_exposure"] = data["post_pilot"] * data["ai_exposure_ex_ante"]
    data = data.dropna(subset=["ai_exposure_ex_ante"])
    fe = "C(city_industry) + C(industry_year)"
    rows = []
    not_supported = "causal productivity; economy-wide shock"
    for est, formula_dep in (
        ("ols_count", "smart_factory_count"),
        ("ols_log1p", "log1p_projects"),
        ("poisson", "smart_factory_count"),
    ):
        d = data.assign(log1p_projects=np.log1p(data["smart_factory_count"].clip(lower=0)))
        dep = formula_dep
        formula = f"{dep} ~ post_x_exposure + {fe}"
        try:
            if est == "poisson":
                fit = smf.poisson(formula, data=d).fit(
                    cov_type="cluster", cov_kwds={"groups": d["city"]}, disp=False
                )
            else:
                fit = smf.ols(formula, data=d).fit(
                    cov_type="cluster", cov_kwds={"groups": d["city"]}
                )
            rows.append(
                _atlas_model_row(
                    fit,
                    "post_x_exposure",
                    model=f"pilot_x_ai_exposure_smart_factories_{est}",
                    fixed_effects="city_industry, industry_year",
                    sample_rule="atlas_sf_years_present",
                    claim_tier="associational_exploratory",
                    interpretation="Pilot-zone × ex-ante exposure and smart-factory recognition counts.",
                    not_supported=not_supported,
                    data=d,
                )
            )
        except Exception as exc:
            rows.append(
                {
                    "model": f"pilot_x_ai_exposure_smart_factories_{est}",
                    "term": "post_x_exposure",
                    "coef": np.nan,
                    "std_err": np.nan,
                    "p_value": np.nan,
                    "n_obs": len(d),
                    "n_cities": d["city"].nunique(),
                    "n_industries": d["industry_code"].nunique(),
                    "years": ",".join(str(int(y)) for y in sorted(d["year"].unique())),
                    "fixed_effects": "city_industry, industry_year",
                    "sample_rule": "failed_fit",
                    "claim_tier": "associational_exploratory",
                    "interpretation": str(exc),
                    "not_supported_claims": not_supported,
                }
            )
    return pd.DataFrame(rows)


def run_patent_event_study(panel: pd.DataFrame) -> pd.DataFrame:
    data = _prep_patent_sample(panel)
    data = data[data["pilot_zone"] == 1].copy()
    data = data[data["years_since_pilot"].isin(EVENT_K)]
    rows = []
    not_supported = "causal productivity; export upgrading"
    def _event_col(k: int) -> str:
        return f"event_k_m{abs(k)}" if k < 0 else f"event_k_{k}"

    for k in EVENT_K:
        if k == OMIT_K:
            continue
        col = _event_col(k)
        data[col] = ((data["years_since_pilot"] == k).astype(int) * data["ai_exposure_ex_ante"])
    event_terms = " + ".join(_event_col(k) for k in EVENT_K if k != OMIT_K)
    formula = f"industrial_ai_patents ~ {event_terms} + C(city_industry) + C(province_year) + C(industry_year)"
    try:
        fit = smf.ols(formula, data=data).fit(
            cov_type="cluster", cov_kwds={"groups": data["city"]}
        )
        for k in EVENT_K:
            if k == OMIT_K:
                continue
            term = _event_col(k)
            rows.append(
                _atlas_model_row(
                    fit,
                    term,
                    model="atlas_event_study_patents",
                    fixed_effects="city_industry, province_year, industry_year",
                    sample_rule="pilot_cities_event_window",
                    claim_tier="associational_exploratory",
                    interpretation=f"Event-time coefficient k={k} (omitted k=-1) × AI exposure.",
                    not_supported=not_supported,
                    data=data,
                )
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
                "n_cities": data["city"].nunique(),
                "n_industries": data["industry_code"].nunique(),
                "years": "",
                "fixed_effects": "city_industry, province_year, industry_year",
                "sample_rule": "failed_fit",
                "claim_tier": "associational_exploratory",
                "interpretation": str(exc),
                "not_supported_claims": not_supported,
            }
        )
    return pd.DataFrame(rows)


def _plot_event_study(event_df: pd.DataFrame, out_path: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return
    coef_rows = event_df[event_df["term"].str.startswith("event_k_")].copy()
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
    ax.set_ylabel("Coefficient (× AI exposure)")
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

    f1 = run_patent_pilot_exposure_models(panel)
    f2 = run_robot_complementarity_models(panel)
    f3 = run_smart_factory_models(panel)
    f4 = run_patent_event_study(panel)

    write_csv(f1, OUTPUT_TABLES / "table_F1_pilot_x_ai_exposure_patents.csv")
    write_csv(f2, OUTPUT_TABLES / "table_F2_robot_complementarity_patents.csv")
    write_csv(f3, OUTPUT_TABLES / "table_F3_pilot_x_ai_exposure_smart_factories.csv")
    write_csv(f4, OUTPUT_TABLES / "table_F4_atlas_event_study_patents.csv")
    _plot_event_study(f4, FIGURES / "fig_F1_patent_event_study.png")

    return {"F1": f1, "F2": f2, "F3": f3, "F4": f4}
