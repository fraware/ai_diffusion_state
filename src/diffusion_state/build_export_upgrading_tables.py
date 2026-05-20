from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from diffusion_state.utils import PROJECT_ROOT, write_csv

OUTPUT_TABLES = PROJECT_ROOT / "outputs" / "tables"


def _fit_export_model(data: pd.DataFrame, formula: str) -> pd.DataFrame:
    model = smf.ols(formula, data=data).fit(cov_type="HC1")
    rows = []
    for term, coef in model.params.items():
        rows.append(
            {
                "term": term,
                "coef": coef,
                "std_err": model.bse[term],
                "p_value": model.pvalues[term],
                "n_obs": int(model.nobs),
                "r_squared": model.rsquared,
            }
        )
    return pd.DataFrame(rows)


def build_table_export_upgrading() -> pd.DataFrame:
    """Sector-year export growth on smart-factory exposure (province-industry adoption shares)."""
    sector = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "export_outcomes_sector_year.csv")
    prov_ind = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "smart_factory_province_year.csv")
    clean = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "smart_factories_clean.csv")

    # Province-industry adoption counts by year
    prov_ind2 = (
        clean[clean["province"] != "unknown"]
        .groupby(["province", "industry_code", "list_year"], as_index=False)
        .agg(smart_factory_projects=("project_id", "count"))
        .rename(columns={"list_year": "year"})
    )
    prov_ind2["prov_year_total"] = prov_ind2.groupby(["province", "year"])[
        "smart_factory_projects"
    ].transform("sum")
    prov_ind2["sf_share"] = np.where(
        prov_ind2["prov_year_total"] > 0,
        prov_ind2["smart_factory_projects"] / prov_ind2["prov_year_total"],
        0.0,
    )

    # Merge sector exports with average province exposure in that sector (descriptive aggregation)
    sector_exp = sector[sector["mapping_confidence_summary"].isin({"high", "medium"})].copy()
    exposure = (
        prov_ind2.groupby(["industry_code", "year"], as_index=False)["sf_share"]
        .mean()
        .rename(columns={"sf_share": "mean_province_sf_share"})
    )
    sector_exp = sector_exp.merge(
        exposure,
        left_on=["sector_code", "year"],
        right_on=["industry_code", "year"],
        how="left",
    ).drop(columns=["industry_code"], errors="ignore")
    sector_exp = sector_exp.dropna(subset=["export_value_growth", "mean_province_sf_share"])

    formula = "export_value_growth ~ mean_province_sf_share + C(year)"
    est = _fit_export_model(sector_exp, formula)
    est["model"] = "sector_export_growth_on_sf_exposure"
    est["formula"] = formula
    est["note"] = (
        "Descriptive sector-year regression; exposure is mean province smart-factory share. "
        "Not causal."
    )

    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
    write_csv(est, OUTPUT_TABLES / "table_4_export_upgrading_models.csv")
    return est


if __name__ == "__main__":
    build_table_export_upgrading()
