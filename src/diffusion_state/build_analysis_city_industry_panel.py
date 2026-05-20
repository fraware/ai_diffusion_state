from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from diffusion_state.build_analysis_panel import build_analysis_city_year_panel
from diffusion_state.utils import PROJECT_ROOT, write_csv

PRIMARY_MAPPING_CONFIDENCE = {"high", "medium"}


def build_analysis_city_industry_year_panel(
    city_industry_path: Path | None = None,
    pilots_path: Path | None = None,
    sector_export_path: Path | None = None,
    bridge_path: Path | None = None,
    city_panel_path: Path | None = None,
    out_path: Path | None = None,
) -> pd.DataFrame:
    city_industry_path = (
        city_industry_path or PROJECT_ROOT / "data" / "processed" / "smart_factory_city_industry_year.csv"
    )
    pilots_path = pilots_path or PROJECT_ROOT / "data" / "processed" / "pilot_zones.csv"
    sector_export_path = (
        sector_export_path or PROJECT_ROOT / "data" / "processed" / "export_outcomes_sector_year.csv"
    )
    bridge_path = bridge_path or PROJECT_ROOT / "data" / "processed" / "hs_to_smart_factory_sector_bridge.csv"
    city_panel_path = city_panel_path or PROJECT_ROOT / "data" / "processed" / "analysis_city_year_panel.csv"
    out_path = out_path or PROJECT_ROOT / "data" / "processed" / "analysis_city_industry_year_panel.csv"

    if not city_panel_path.exists():
        build_analysis_city_year_panel()

    ci = pd.read_csv(city_industry_path)
    pilots = pd.read_csv(pilots_path)[["city", "province", "pilot_year"]]
    panel = pd.read_csv(city_panel_path)[
        ["city", "year", "pilot_zone", "pilot_year", "post_pilot", "years_since_pilot"]
    ]

    df = ci.merge(panel, on=["city", "year"], how="left")
    df = df.merge(
        pilots.rename(columns={"pilot_year": "pilot_year_from_pilot_table"}),
        on=["city", "province"],
        how="left",
    )
    df["pilot_year"] = df["pilot_year"].fillna(df["pilot_year_from_pilot_table"])
    df["pilot_zone"] = df["pilot_zone"].fillna(df["pilot_year"].notna().astype(int))
    df["post_pilot"] = df["post_pilot"].fillna(
        ((df["pilot_zone"] == 1) & (df["year"] >= df["pilot_year"])).astype(int)
    )
    df = df.drop(columns=["pilot_year_from_pilot_table"])

    sector = pd.read_csv(sector_export_path)
    sector_primary = sector[sector["mapping_confidence_summary"].isin(PRIMARY_MAPPING_CONFIDENCE)]
    export_cols = sector_primary[
        ["year", "sector_code", "export_value_growth", "unit_value_growth", "mapping_confidence_summary"]
    ].rename(
        columns={
            "sector_code": "industry_code",
            "mapping_confidence_summary": "mapping_confidence",
        }
    )

    df = df.merge(export_cols, on=["year", "industry_code"], how="left")
    df["ai_exposure_industry"] = 1
    df["controls_available"] = 0

    df = df.sort_values(["city", "industry_code", "year"]).reset_index(drop=True)
    write_csv(df, out_path)
    return df
