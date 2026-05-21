from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from diffusion_state.model_utils import control_terms
from diffusion_state.panel_controls import add_derived_controls, controls_available
from diffusion_state.utils import PROJECT_ROOT, write_csv

OUTPUT_TABLES = PROJECT_ROOT / "outputs" / "tables"
ADOPTION_YEARS = (2024, 2025)


def build_analysis_province_year_panel(
    clean_path: Path | None = None,
    pilot_path: Path | None = None,
    out_path: Path | None = None,
) -> pd.DataFrame:
    clean_path = clean_path or PROJECT_ROOT / "data" / "processed" / "smart_factories_clean.csv"
    pilot_path = pilot_path or PROJECT_ROOT / "data" / "processed" / "pilot_zones.csv"
    out_path = out_path or PROJECT_ROOT / "data" / "processed" / "analysis_province_year_panel.csv"

    clean = pd.read_csv(clean_path)
    pilots = pd.read_csv(pilot_path)
    pilot_provinces = set(pilots["province"].unique())

    py = (
        clean.groupby(["province", "list_year"], as_index=False)
        .agg(smart_factory_projects=("project_id", "count"))
        .rename(columns={"list_year": "year"})
    )
    py["pilot_province"] = py["province"].isin(pilot_provinces).astype(int)
    n_pilot_cities = pilots.groupby("province")["city"].nunique()
    py["number_of_pilot_cities_in_province"] = py["province"].map(n_pilot_cities).fillna(0).astype(int)
    py = py[py["year"].isin(ADOPTION_YEARS)].copy()
    write_csv(py, out_path)
    return py


def run_province_year_models(
    panel_path: Path | None = None,
    city_panel_path: Path | None = None,
) -> pd.DataFrame:
    panel_path = panel_path or PROJECT_ROOT / "data" / "processed" / "analysis_province_year_panel.csv"
    if not panel_path.exists():
        build_analysis_province_year_panel()

    py = pd.read_csv(panel_path)
    py["log1p_projects"] = np.log1p(py["smart_factory_projects"])

    city_panel_path = city_panel_path or PROJECT_ROOT / "data" / "processed" / "analysis_city_year_panel.csv"
    prov_controls = None
    if city_panel_path.exists():
        cp = add_derived_controls(pd.read_csv(city_panel_path))
        if controls_available(cp):
            prov_controls = (
                cp[cp["year"].isin(ADOPTION_YEARS)]
                .groupby(["province", "year"], as_index=False)
                .agg(
                    gdp=("gdp", "sum"),
                    population=("population", "sum"),
                    secondary_value_added=("secondary_value_added", "sum"),
                    industrial_output=("industrial_output", "sum"),
                    fdi=("fdi", "sum"),
                    fixed_asset_investment=("fixed_asset_investment", "sum"),
                    telecom_or_internet_proxy=("telecom_or_internet_proxy", "mean"),
                    education_proxy=("education_proxy", "mean"),
                    foreign_trade=("foreign_trade", "sum"),
                    average_wage=("average_wage", "mean"),
                )
            )
            py = py.merge(prov_controls, on=["province", "year"], how="left")
            py = add_derived_controls(py)

    specs = [
        ("count_pilot_province", "smart_factory_projects ~ pilot_province + C(year)"),
        ("log1p_pilot_province", "log1p_projects ~ pilot_province + C(year)"),
        ("count_pilot_cities_in_province", "smart_factory_projects ~ number_of_pilot_cities_in_province + C(year)"),
    ]
    if prov_controls is not None:
        ctrl = control_terms()
        specs.append(
            (
                "log1p_pilot_cities_controlled",
                f"log1p_projects ~ number_of_pilot_cities_in_province + {ctrl} + C(year)",
            )
        )

    rows = []
    for model_name, formula in specs:
        rhs = formula.split("~", 1)[1]
        dep = formula.split("~", 1)[0].strip()
        predictors = [t.strip() for t in rhs.split("+") if t.strip() and not t.strip().startswith("C(")]
        data = py.dropna(subset=[dep] + predictors)
        if len(data) < 8 or data["province"].nunique() < 4:
            rows.append(
                {
                    "term": "skipped",
                    "coef": "insufficient province-year variation",
                    "std_err": np.nan,
                    "p_value": np.nan,
                    "n_obs": len(data),
                    "r_squared": np.nan,
                    "model": model_name,
                    "formula": formula,
                    "note": "Robustness only; pilot provinces include non-pilot cities.",
                }
            )
            continue
        fit = smf.ols(formula, data=data).fit(cov_type="HC1")
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
                    "note": "Robustness only; pilot provinces include non-pilot cities.",
                }
            )

    out = pd.DataFrame(rows)
    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
    write_csv(out, OUTPUT_TABLES / "table_19_province_year_models.csv")
    return out
