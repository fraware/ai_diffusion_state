from __future__ import annotations

from pathlib import Path

import pandas as pd

from diffusion_state.panel_controls import add_derived_controls
from diffusion_state.run_hub_robustness import DIRECT_ADMIN, HUB_CITIES, _top_gdp_cities
from diffusion_state.utils import PROJECT_ROOT, write_csv

OUTPUT_TABLES = PROJECT_ROOT / "outputs" / "tables"
PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "city_diffusion_typology_ex_ante.csv"


def build_city_diffusion_typology_ex_ante(panel_path: Path | None = None) -> pd.DataFrame:
    panel_path = panel_path or PROJECT_ROOT / "data" / "processed" / "analysis_city_year_panel.csv"
    panel = add_derived_controls(pd.read_csv(panel_path))
    meta = (
        panel.groupby(["city", "province"], as_index=False)
        .agg(
            pilot_zone=("pilot_zone", "max"),
            gdp=("gdp", "mean"),
            telecom_or_internet_proxy=("telecom_or_internet_proxy", "mean"),
            secondary_value_added=("secondary_value_added", "mean"),
            industrial_output=("industrial_output", "mean"),
        )
    )
    top10_gdp = _top_gdp_cities(10, panel) if panel["gdp"].notna().any() else set()

    meta["direct_admin_municipality"] = meta["city"].isin(DIRECT_ADMIN).astype(int)
    meta["mega_hub"] = meta["city"].isin(HUB_CITIES).astype(int)
    meta["top_10_gdp_city"] = meta["city"].isin(top10_gdp).astype(int)
    meta["province_manufacturing_intensity"] = meta["secondary_value_added"] / meta["gdp"].replace(0, pd.NA)

    def _type(row: pd.Series) -> str:
        if row["direct_admin_municipality"] == 1:
            return "frontier_municipality_hub"
        if row["pilot_zone"] == 1 and (row["mega_hub"] == 1 or row["top_10_gdp_city"] == 1):
            return "ex_ante_pilot_hub"
        if row["pilot_zone"] == 1:
            return "ex_ante_pilot_non_hub"
        if row["mega_hub"] == 1 or row["top_10_gdp_city"] == 1:
            return "ex_ante_nonpilot_industrial_hub"
        return "ex_ante_nonpilot_low_capacity"

    meta["diffusion_type_ex_ante"] = meta.apply(_type, axis=1)
    write_csv(meta, PROCESSED_PATH)
    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
    write_csv(meta, OUTPUT_TABLES / "table_18_city_diffusion_typology_ex_ante.csv")
    return meta
