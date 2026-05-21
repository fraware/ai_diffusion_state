from __future__ import annotations

from pathlib import Path

import pandas as pd

from diffusion_state.panel_controls import add_derived_controls
from diffusion_state.run_hub_robustness import DIRECT_ADMIN, HUB_CITIES, _top_gdp_cities, _top_smart_factory_cities
from diffusion_state.utils import PROJECT_ROOT, write_csv

OUTPUT_TABLES = PROJECT_ROOT / "outputs" / "tables"
OUTPUT_FIGURES = PROJECT_ROOT / "outputs" / "figures"

PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "city_diffusion_typology.csv"


def _city_project_totals() -> pd.DataFrame:
    cy = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "smart_factory_city_year.csv")
    totals = (
        cy.groupby("city", as_index=False)["smart_factory_projects"]
        .sum()
        .rename(columns={"smart_factory_projects": "resolved_smart_factory_projects"})
    )
    totals["smart_factory_rank"] = (
        totals["resolved_smart_factory_projects"].rank(method="dense", ascending=False).astype(int)
    )
    return totals


def build_city_diffusion_typology(panel_path: Path | None = None) -> pd.DataFrame:
    panel_path = panel_path or PROJECT_ROOT / "data" / "processed" / "analysis_city_year_panel.csv"
    panel = add_derived_controls(pd.read_csv(panel_path))
    meta = (
        panel.groupby(["city", "province"], as_index=False)
        .agg(
            pilot_zone=("pilot_zone", "max"),
            post_pilot=("post_pilot", "max"),
        )
    )
    totals = _city_project_totals()
    meta = meta.merge(totals, on="city", how="left")
    meta["resolved_smart_factory_projects"] = meta["resolved_smart_factory_projects"].fillna(0).astype(int)

    top5_sf = _top_smart_factory_cities(5)
    top10_gdp = _top_gdp_cities(10, panel) if panel["gdp"].notna().any() else set()

    meta["direct_admin_municipality"] = meta["city"].isin(DIRECT_ADMIN).astype(int)
    meta["mega_hub"] = meta["city"].isin(HUB_CITIES).astype(int)
    meta["top_5_smart_factory_city"] = meta["city"].isin(top5_sf).astype(int)
    meta["top_10_gdp_city"] = meta["city"].isin(top10_gdp).astype(int)

    def _diffusion_type(row: pd.Series) -> str:
        city = row["city"]
        if city == "unknown" or pd.isna(city):
            return "unknown_geo_limited"
        if row["direct_admin_municipality"] == 1:
            return "frontier_municipality_hub"
        if row["pilot_zone"] == 1 and (row["mega_hub"] == 1 or row["top_5_smart_factory_city"] == 1):
            return "pilot_industrial_hub"
        if row["pilot_zone"] == 1:
            return "pilot_non_hub"
        if row["top_5_smart_factory_city"] == 1 or row["top_10_gdp_city"] == 1:
            return "nonpilot_industrial_hub"
        if row["resolved_smart_factory_projects"] <= 0:
            return "nonpilot_low_adoption"
        return "nonpilot_low_adoption"

    meta["diffusion_type"] = meta.apply(_diffusion_type, axis=1)
    write_csv(meta, PROCESSED_PATH)

    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
    write_csv(meta, OUTPUT_TABLES / "table_14_city_diffusion_typology.csv")
    _plot_typology_counts(meta)
    return meta


def _plot_typology_counts(typology: pd.DataFrame) -> Path | None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    agg = (
        typology.groupby("diffusion_type", as_index=False)["resolved_smart_factory_projects"]
        .sum()
        .sort_values("resolved_smart_factory_projects", ascending=True)
    )
    fig, ax = plt.subplots(figsize=(9, max(4, len(agg) * 0.4)))
    ax.barh(agg["diffusion_type"], agg["resolved_smart_factory_projects"], color="steelblue")
    ax.set_xlabel("Listed smart-factory projects (2024–2025, resolved cities)")
    ax.set_title("Smart-factory projects by diffusion-state city type")
    fig.tight_layout()
    OUTPUT_FIGURES.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_FIGURES / "fig_city_typology_smart_factory_counts.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path
