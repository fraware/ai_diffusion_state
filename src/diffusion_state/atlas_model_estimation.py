from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

MODEL_ROW_COLUMNS = [
    "model",
    "term",
    "coef",
    "std_err",
    "p_value",
    "n_obs",
    "n_nonzero_outcome",
    "n_cities",
    "n_industries",
    "years",
    "fixed_effects",
    "sample_rule",
    "estimator_status",
    "claim_tier",
    "interpretation",
    "not_supported_claims",
]

NOT_SUPPORTED_CLAIMS = (
    "causal productivity; export upgrading; procurement commercial output; "
    "economy-wide productivity shock"
)


@dataclass(frozen=True)
class ModelSpec:
    model_name: str
    dep: str
    interaction: str
    fe_formula: str
    fixed_effects_label: str
    sample_rule: str
    estimator: str  # ols | poisson


def prep_patent_sample(panel: pd.DataFrame) -> pd.DataFrame:
    df = panel[panel["industrial_ai_patents"].notna()].copy()
    df["city_industry"] = df["city"].astype(str) + "__" + df["industry_code"].astype(str)
    df["province_year"] = df["province"].astype(str) + "__" + df["year"].astype(str)
    df["industry_year"] = df["industry_code"].astype(str) + "__" + df["year"].astype(str)
    df["log1p_patents"] = np.log1p(df["industrial_ai_patents"].clip(lower=0))
    df["post_x_exposure"] = df["post_pilot"] * df["ai_exposure_ex_ante"]
    df["post_x_exposure_x_robot"] = (
        df["post_pilot"] * df["ai_exposure_ex_ante"] * df["robot_compatibility"]
    )
    return df.dropna(subset=["ai_exposure_ex_ante", "robot_compatibility"])


def _n_singleton_fe_cells(data: pd.DataFrame, fe_formula: str) -> int:
    """Approximate singleton absorbed FE cells via one-way group counts of size 1."""
    singletons = 0
    for token in fe_formula.replace("C(", "").replace(")", "").split("+"):
        col = token.strip()
        if col and col in data.columns:
            singletons += int((data.groupby(col).size() == 1).sum())
    return singletons


def build_model_diagnostics(
    data: pd.DataFrame,
    *,
    model_name: str,
    outcome_col: str,
    interaction_col: str,
) -> dict:
    outcome = pd.to_numeric(data[outcome_col], errors="coerce").fillna(0)
    interaction = pd.to_numeric(data[interaction_col], errors="coerce")
    n_nonzero = int((outcome > 0).sum())
    n_obs = int(len(data))
    can_estimate = n_obs >= 30 and n_nonzero >= 5
    failure = ""
    if n_nonzero < 5:
        failure = "insufficient_nonzero_outcome"
    elif data["city"].nunique() < 3:
        failure = "insufficient_cities"
    return {
        "model_name": model_name,
        "n_obs": n_obs,
        "n_nonzero_outcome": n_nonzero,
        "n_cities": int(data["city"].nunique()),
        "n_industries": int(data["industry_code"].nunique()),
        "n_years": int(data["year"].nunique()),
        "n_city_industry_cells": int(data["city_industry"].nunique()),
        "n_singleton_fe_cells": _n_singleton_fe_cells(data, "city_industry + year"),
        "interaction_mean": float(interaction.mean()) if interaction.notna().any() else np.nan,
        "interaction_sd": float(interaction.std()) if interaction.notna().any() else np.nan,
        "interaction_nonzero_share": float((interaction.fillna(0) != 0).mean()),
        "outcome_mean": float(outcome.mean()),
        "outcome_nonzero_share": float((outcome > 0).mean()),
        "can_estimate": bool(can_estimate),
        "failure_reason": failure,
    }


def _model_row(
    *,
    spec: ModelSpec,
    term: str,
    coef: float,
    std_err: float,
    p_value: float,
    data: pd.DataFrame,
    outcome_col: str,
    interpretation: str,
) -> dict:
    outcome = pd.to_numeric(data[outcome_col], errors="coerce").fillna(0)
    n_nonzero = int((outcome > 0).sum())
    se_ok = np.isfinite(std_err) and std_err > 0
    p_ok = np.isfinite(p_value)
    status = "ok" if se_ok and p_ok and np.isfinite(coef) else "failed_covariance"
    claim_tier = "associational_exploratory" if status == "ok" else "not_supported"
    return {
        "model": spec.model_name,
        "term": term,
        "coef": coef,
        "std_err": std_err,
        "p_value": p_value,
        "n_obs": len(data),
        "n_nonzero_outcome": n_nonzero,
        "n_cities": int(data["city"].nunique()),
        "n_industries": int(data["industry_code"].nunique()),
        "years": ",".join(str(int(y)) for y in sorted(data["year"].unique())),
        "fixed_effects": spec.fixed_effects_label,
        "sample_rule": spec.sample_rule,
        "estimator_status": status,
        "claim_tier": claim_tier,
        "interpretation": interpretation,
        "not_supported_claims": NOT_SUPPORTED_CLAIMS,
    }


def _failed_row(spec: ModelSpec, term: str, data: pd.DataFrame, outcome_col: str, reason: str) -> dict:
    outcome = pd.to_numeric(data[outcome_col], errors="coerce").fillna(0)
    return {
        "model": spec.model_name,
        "term": term,
        "coef": np.nan,
        "std_err": np.nan,
        "p_value": np.nan,
        "n_obs": len(data),
        "n_nonzero_outcome": int((outcome > 0).sum()),
        "n_cities": int(data["city"].nunique()),
        "n_industries": int(data["industry_code"].nunique()),
        "years": ",".join(str(int(y)) for y in sorted(data["year"].unique())),
        "fixed_effects": spec.fixed_effects_label,
        "sample_rule": spec.sample_rule,
        "estimator_status": "failed_covariance",
        "claim_tier": "not_supported",
        "interpretation": reason,
        "not_supported_claims": NOT_SUPPORTED_CLAIMS,
    }


def _outcome_count_column(spec: ModelSpec) -> str:
    if spec.dep == "log1p_patents":
        return "industrial_ai_patents"
    if spec.dep == "log1p_projects":
        return "smart_factory_count"
    return spec.dep


def fit_interaction_model(data: pd.DataFrame, spec: ModelSpec) -> dict:
    term = spec.interaction
    outcome_count_col = _outcome_count_column(spec)
    formula = f"{spec.dep} ~ {term} + {spec.fe_formula}"
    try:
        if spec.estimator == "poisson":
            fit = smf.poisson(formula, data=data).fit(
                cov_type="cluster",
                cov_kwds={"groups": data["city"]},
                disp=False,
                maxiter=200,
            )
        else:
            fit = smf.ols(formula, data=data).fit(
                cov_type="cluster",
                cov_kwds={"groups": data["city"]},
            )
        if term not in fit.params:
            return _failed_row(spec, term, data, outcome_count_col, f"term {term} not identified")
        interp = (
            "Pilot-zone x ex-ante AI exposure association with smart-factory recognition counts."
            if "smart_factories" in spec.model_name
            else "Pilot-zone x ex-ante AI exposure association with industrial AI patents."
        )
        return _model_row(
            spec=spec,
            term=term,
            coef=float(fit.params[term]),
            std_err=float(fit.bse[term]) if term in fit.bse else np.nan,
            p_value=float(fit.pvalues[term]) if term in fit.pvalues else np.nan,
            data=data,
            outcome_col=outcome_count_col,
            interpretation=interp,
        )
    except Exception as exc:
        return _failed_row(spec, term, data, outcome_count_col, str(exc))


def patent_fe_ladder_specs() -> list[ModelSpec]:
    return [
        ModelSpec(
            "pilot_x_ai_exposure_patents_baseline_ols_log1p",
            "log1p_patents",
            "post_x_exposure",
            "C(city) + C(industry_code) + C(year)",
            "city, industry, year",
            "atlas_patent_years_baseline_fe",
            "ols",
        ),
        ModelSpec(
            "pilot_x_ai_exposure_patents_city_industry_year_ols_log1p",
            "log1p_patents",
            "post_x_exposure",
            "C(city_industry) + C(year)",
            "city_industry, year",
            "atlas_patent_years_city_industry_fe",
            "ols",
        ),
        ModelSpec(
            "pilot_x_ai_exposure_patents_province_year_ols_log1p",
            "log1p_patents",
            "post_x_exposure",
            "C(city_industry) + C(province_year)",
            "city_industry, province_year",
            "atlas_patent_years_province_year_fe",
            "ols",
        ),
        ModelSpec(
            "pilot_x_ai_exposure_patents_saturated_ols_log1p",
            "log1p_patents",
            "post_x_exposure",
            "C(city_industry) + C(province_year) + C(industry_year)",
            "city_industry, province_year, industry_year",
            "atlas_patent_years_saturated_fe",
            "ols",
        ),
        ModelSpec(
            "pilot_x_ai_exposure_patents_saturated_poisson",
            "industrial_ai_patents",
            "post_x_exposure",
            "C(city_industry) + C(province_year) + C(industry_year)",
            "city_industry, province_year, industry_year",
            "atlas_patent_years_saturated_fe",
            "poisson",
        ),
    ]


def run_patent_model_suite(panel: pd.DataFrame) -> dict[str, pd.DataFrame]:
    data = prep_patent_sample(panel)
    diag_rows = []
    model_rows: list[dict] = []
    for spec in patent_fe_ladder_specs():
        diag_rows.append(
            build_model_diagnostics(
                data,
                model_name=spec.model_name,
                outcome_col="industrial_ai_patents",
                interaction_col=spec.interaction,
            )
        )
        row = fit_interaction_model(data, spec)
        model_rows.append(row)
        if spec.estimator == "ols" and row["estimator_status"] != "ok":
            continue

    all_models = pd.DataFrame(model_rows)
    f1a = all_models[all_models["model"].str.contains("baseline")].copy()
    f1b = all_models[
        all_models["model"].str.contains("city_industry_year|province_year")
        & ~all_models["model"].str.contains("saturated")
    ].copy()
    f1c = all_models[all_models["model"].str.contains("saturated")].copy()
    f0 = pd.DataFrame(diag_rows)
    legacy_f1 = f1b if not f1b.empty else f1a
    return {"F0": f0, "F1a": f1a, "F1b": f1b, "F1c": f1c, "F1_legacy": legacy_f1}


def run_robot_complementarity_models(panel: pd.DataFrame) -> pd.DataFrame:
    data = prep_patent_sample(panel)
    specs = [
        ModelSpec(
            "robot_complementarity_patents_baseline_ols_log1p",
            "log1p_patents",
            "post_x_exposure_x_robot",
            "C(city) + C(industry_code) + C(year)",
            "city, industry, year",
            "atlas_patent_years_baseline_fe",
            "ols",
        ),
        ModelSpec(
            "robot_complementarity_patents_saturated_ols_log1p",
            "log1p_patents",
            "post_x_exposure_x_robot",
            "C(city_industry) + C(province_year) + C(industry_year)",
            "city_industry, province_year, industry_year",
            "atlas_patent_years_saturated_fe",
            "ols",
        ),
        ModelSpec(
            "robot_complementarity_patents_saturated_poisson",
            "industrial_ai_patents",
            "post_x_exposure_x_robot",
            "C(city_industry) + C(province_year) + C(industry_year)",
            "city_industry, province_year, industry_year",
            "atlas_patent_years_saturated_fe",
            "poisson",
        ),
    ]
    return pd.DataFrame([fit_interaction_model(data, s) for s in specs])


def has_publication_ready_f1(tables: dict[str, pd.DataFrame] | None = None) -> tuple[bool, str]:
    """At least one F1 model with valid inference and minimum support."""
    candidates = []
    for key in ("F1a", "F1b", "F1c", "F1_legacy"):
        if tables and key in tables:
            candidates.append(tables[key])
    if not candidates:
        from diffusion_state.utils import PROJECT_ROOT

        for name in (
            "table_F1a_pilot_x_ai_exposure_patents_baseline.csv",
            "table_F1b_pilot_x_ai_exposure_patents_fe_ladder.csv",
            "table_F1c_pilot_x_ai_exposure_patents_saturated.csv",
            "table_F1_pilot_x_ai_exposure_patents.csv",
        ):
            path = PROJECT_ROOT / "outputs" / "tables" / name
            if path.exists():
                candidates.append(pd.read_csv(path))

    for df in candidates:
        if df.empty:
            continue
        term_col = "term" if "term" in df.columns else None
        if not term_col:
            continue
        sub = df[df[term_col].astype(str).str.contains("post_x_exposure", na=False)]
        ok = sub[
            (sub["estimator_status"] == "ok")
            & sub["std_err"].notna()
            & sub["p_value"].notna()
            & (sub["n_nonzero_outcome"] >= 100)
            & (sub["n_cities"] >= 50)
            & (sub["n_industries"] >= 10)
        ]
        if not ok.empty:
            row = ok.iloc[0]
            return True, f"{row['model']}: coef={row['coef']:.4f}, p={row['p_value']:.3f}"
    return False, "no F1 model with valid std_err/p_value and minimum sample support"
