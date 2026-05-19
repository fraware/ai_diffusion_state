from __future__ import annotations

from pathlib import Path

import pandas as pd

from diffusion_state.utils import PROJECT_ROOT, write_csv


def build_city_year_panel(
    pilot_path: Path | None = None,
    smart_factory_path: Path | None = None,
    city_controls_path: Path | None = None,
    out_path: Path | None = None,
) -> pd.DataFrame:
    pilot_path = pilot_path or PROJECT_ROOT / "data" / "processed" / "pilot_zones.csv"
    smart_factory_path = smart_factory_path or PROJECT_ROOT / "data" / "processed" / "smart_factories_clean.csv"
    city_controls_path = city_controls_path or PROJECT_ROOT / "data" / "processed" / "city_controls.csv"
    out_path = out_path or PROJECT_ROOT / "data" / "processed" / "panel_city_year.csv"

    pilots = pd.read_csv(pilot_path)
    controls = pd.read_csv(city_controls_path)
    if smart_factory_path.exists():
        sf = pd.read_csv(smart_factory_path)
        sf_counts = sf.groupby(["city_std", "year"], as_index=False).agg(
            smart_factory_count=("firm_std", "count"),
            industrial_ai_keyword_count=("has_industrial_ai_keyword", "sum") if "has_industrial_ai_keyword" in sf.columns else ("firm_std", "count"),
        )
    else:
        sf_counts = pd.DataFrame(columns=["city_std", "year", "smart_factory_count", "industrial_ai_keyword_count"])

    df = controls.merge(sf_counts, on=["city_std", "year"], how="left")
    df[["smart_factory_count", "industrial_ai_keyword_count"]] = df[["smart_factory_count", "industrial_ai_keyword_count"]].fillna(0)

    pilot_min = pilots[["location_std", "pilot_year"]].rename(columns={"location_std": "city_std"})
    df = df.merge(pilot_min, on="city_std", how="left")
    df["pilot_zone"] = df["pilot_year"].notna().astype(int)
    df["post_pilot"] = ((df["pilot_zone"] == 1) & (df["year"] >= df["pilot_year"])).astype(int)
    df["years_since_pilot"] = df["year"] - df["pilot_year"]
    write_csv(df, out_path)
    return df
