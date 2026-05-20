from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from diffusion_state.panel_controls import MODEL_CONTROL_TERMS


def control_terms() -> str:
    return " + ".join(MODEL_CONTROL_TERMS)


def fit_ols_table(
    formula: str,
    data: pd.DataFrame,
    *,
    model: str,
    cluster: str | None = "city",
    sample_rule: str = "full",
    fixed_effects: str = "",
    controls_included: str = "",
    extra_meta: dict | None = None,
) -> pd.DataFrame:
    fit = smf.ols(formula, data=data).fit(
        cov_type="cluster" if cluster else "nonrobust",
        cov_kwds={"groups": data[cluster]} if cluster else None,
    )
    rows = []
    for term, coef in fit.params.items():
        row = {
            "term": term,
            "coef": coef,
            "std_err": fit.bse[term],
            "t_stat": fit.tvalues[term],
            "p_value": fit.pvalues[term],
            "n_obs": int(fit.nobs),
            "r_squared": fit.rsquared,
            "model": model,
            "formula": formula,
            "sample_rule": sample_rule,
            "n_cities": int(data["city"].nunique()) if "city" in data.columns else np.nan,
            "years": ",".join(str(int(y)) for y in sorted(data["year"].unique())) if "year" in data.columns else "",
            "fixed_effects": fixed_effects,
            "controls_included": controls_included,
        }
        if extra_meta:
            row.update(extra_meta)
        rows.append(row)
    return pd.DataFrame(rows)


def fit_poisson_table(
    formula: str,
    data: pd.DataFrame,
    *,
    model: str,
    cluster: str | None = "city",
    sample_rule: str = "full",
    fixed_effects: str = "",
    controls_included: str = "",
) -> pd.DataFrame:
    fit = smf.poisson(formula, data=data).fit(
        cov_type="cluster" if cluster else "nonrobust",
        cov_kwds={"groups": data[cluster]} if cluster else None,
        disp=False,
        maxiter=200,
    )
    rows = []
    for term, coef in fit.params.items():
        rows.append(
            {
                "term": term,
                "coef": coef,
                "std_err": fit.bse[term],
                "t_stat": fit.tvalues[term],
                "p_value": fit.pvalues[term],
                "n_obs": int(fit.nobs),
                "r_squared": np.nan,
                "model": model,
                "formula": formula,
                "sample_rule": sample_rule,
                "n_cities": int(data["city"].nunique()),
                "years": ",".join(str(int(y)) for y in sorted(data["year"].unique())),
                "fixed_effects": fixed_effects,
                "controls_included": controls_included,
            }
        )
    return pd.DataFrame(rows)


def fit_negative_binomial_table(
    formula: str,
    data: pd.DataFrame,
    *,
    model: str,
    cluster: str | None = "city",
    sample_rule: str = "full",
    fixed_effects: str = "",
    controls_included: str = "",
) -> pd.DataFrame:
    try:
        fit = smf.negativebinomial(formula, data=data).fit(
            cov_type="cluster" if cluster else "nonrobust",
            cov_kwds={"groups": data[cluster]} if cluster else None,
            disp=False,
            maxiter=200,
        )
    except Exception as exc:  # noqa: BLE001
        return pd.DataFrame(
            [
                {
                    "term": "error",
                    "coef": str(exc),
                    "std_err": np.nan,
                    "t_stat": np.nan,
                    "p_value": np.nan,
                    "n_obs": len(data),
                    "r_squared": np.nan,
                    "model": model,
                    "formula": formula,
                    "sample_rule": sample_rule,
                    "n_cities": int(data["city"].nunique()),
                    "years": ",".join(str(int(y)) for y in sorted(data["year"].unique())),
                    "fixed_effects": fixed_effects,
                    "controls_included": controls_included,
                }
            ]
        )
    rows = []
    for term, coef in fit.params.items():
        rows.append(
            {
                "term": term,
                "coef": coef,
                "std_err": fit.bse[term],
                "t_stat": fit.tvalues[term],
                "p_value": fit.pvalues[term],
                "n_obs": int(fit.nobs),
                "r_squared": np.nan,
                "model": model,
                "formula": formula,
                "sample_rule": sample_rule,
                "n_cities": int(data["city"].nunique()),
                "years": ",".join(str(int(y)) for y in sorted(data["year"].unique())),
                "fixed_effects": fixed_effects,
                "controls_included": controls_included,
            }
        )
    return pd.DataFrame(rows)


def pilot_coef_summary(table: pd.DataFrame, term: str = "pilot_zone") -> dict | None:
    sub = table[table["term"] == term]
    if sub.empty:
        return None
    row = sub.iloc[0]
    return {
        "term": term,
        "coef": float(row["coef"]),
        "std_err": float(row["std_err"]),
        "p_value": float(row["p_value"]),
    }
