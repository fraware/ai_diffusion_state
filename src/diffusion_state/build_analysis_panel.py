from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from diffusion_state.panel_controls import add_derived_controls
from diffusion_state.utils import PROJECT_ROOT, write_csv

LIST_YEARS = (2024, 2025)
PANEL_YEARS = list(range(2019, 2026))

CONTROL_COLUMNS = [
    "gdp",
    "gdp_per_capita",
    "industrial_output",
    "secondary_value_added",
    "population",
    "employment",
    "average_wage",
    "fdi",
    "fixed_asset_investment",
    "education_proxy",
    "telecom_or_internet_proxy",
    "foreign_trade",
]


def _load_pilots(path: Path) -> pd.DataFrame:
    pilots = pd.read_csv(path)
    return pilots[["city", "province", "pilot_year"]].rename(
        columns={"pilot_year": "pilot_year_treatment"}
    )


def _city_universe(pilots: pd.DataFrame, city_year: pd.DataFrame) -> pd.DataFrame:
    pilot_cities = pilots[["city", "province"]].drop_duplicates()
    sf_cities = city_year[["city", "province"]].drop_duplicates()
    universe = pd.concat([pilot_cities, sf_cities], ignore_index=True).drop_duplicates(
        subset=["city"], keep="first"
    )
    return universe


def build_analysis_city_year_panel(
    pilot_path: Path | None = None,
    city_year_path: Path | None = None,
    city_controls_path: Path | None = None,
    out_path: Path | None = None,
    panel_years: list[int] | None = None,
) -> pd.DataFrame:
    """City-year panel for adoption analysis.

    Smart-factory counts are observed for 2024-2025 only; earlier years are zero-filled
    for cities in the analysis universe (documented assumption: no pre-2024 list).
    """
    pilot_path = pilot_path or PROJECT_ROOT / "data" / "processed" / "pilot_zones.csv"
    city_year_path = city_year_path or PROJECT_ROOT / "data" / "processed" / "smart_factory_city_year.csv"
    city_controls_path = city_controls_path or PROJECT_ROOT / "data" / "processed" / "city_controls_year.csv"
    out_path = out_path or PROJECT_ROOT / "data" / "processed" / "analysis_city_year_panel.csv"
    panel_years = panel_years or PANEL_YEARS

    pilots = _load_pilots(pilot_path)
    city_year = pd.read_csv(city_year_path)
    universe = _city_universe(pilots, city_year)

    grid = universe.assign(key=1).merge(
        pd.DataFrame({"year": panel_years, "key": 1}), on="key"
    ).drop(columns="key")

    sf = city_year[
        [
            "city",
            "year",
            "smart_factory_projects",
            "smart_factory_projects_ai_tagged",
            "smart_factory_projects_industrial_ai",
        ]
    ]
    df = grid.merge(sf, on=["city", "year"], how="left")
    for col in [
        "smart_factory_projects",
        "smart_factory_projects_ai_tagged",
        "smart_factory_projects_industrial_ai",
    ]:
        df[col] = df[col].fillna(0).astype(int)

    df = df.merge(pilots, on="city", how="left", suffixes=("", "_pilot"))
    if "province_pilot" in df.columns:
        df["province"] = df["province"].fillna(df["province_pilot"])
        df = df.drop(columns=["province_pilot"])

    df["pilot_zone"] = df["pilot_year_treatment"].notna().astype(int)
    df["pilot_year"] = df["pilot_year_treatment"]
    df["post_pilot"] = (
        (df["pilot_zone"] == 1) & (df["year"] >= df["pilot_year"])
    ).astype(int)
    df["years_since_pilot"] = np.where(
        df["pilot_zone"] == 1, df["year"] - df["pilot_year"], np.nan
    )

    never_treated = df["pilot_zone"] == 0
    df.loc[never_treated, "pilot_year"] = np.nan
    df.loc[never_treated, "post_pilot"] = 0
    df.loc[never_treated, "years_since_pilot"] = np.nan

    if city_controls_path.exists():
        controls = pd.read_csv(city_controls_path)
        keep = ["city", "year"] + [c for c in CONTROL_COLUMNS if c in controls.columns]
        df = df.merge(controls[keep], on=["city", "year"], how="left")
    else:
        for col in CONTROL_COLUMNS:
            df[col] = np.nan

    df = df.drop(columns=["pilot_year_treatment"])
    df = add_derived_controls(df)
    df = df.sort_values(["city", "year"]).reset_index(drop=True)
    write_csv(df, out_path)
    return df


def build_smart_factory_province_year(
    clean_path: Path | None = None,
    out_path: Path | None = None,
) -> pd.DataFrame:
    """Province-year adoption including projects without resolved city."""
    clean_path = clean_path or PROJECT_ROOT / "data" / "processed" / "smart_factories_clean.csv"
    out_path = out_path or PROJECT_ROOT / "data" / "processed" / "smart_factory_province_year.csv"

    clean = pd.read_csv(clean_path)
    clean = clean[clean["province"] != "unknown"]
    tagged = clean["ai_scenario_tags"].astype(str).str.len() > 0
    industrial = clean["technology_tags"].astype(str).str.len() > 0

    agg = (
        clean.assign(ai_tagged=tagged, industrial_ai=industrial)
        .groupby(["province", "list_year"], as_index=False)
        .agg(
            smart_factory_projects=("project_id", "count"),
            smart_factory_projects_ai_tagged=("ai_tagged", "sum"),
            smart_factory_projects_industrial_ai=("industrial_ai", "sum"),
            num_distinct_firms=("firm_name_zh", "nunique"),
            projects_city_unknown=("city", lambda s: (s == "unknown").sum()),
        )
        .rename(columns={"list_year": "year"})
    )
    write_csv(agg, out_path)
    return agg
