from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from diffusion_state.utils import PROJECT_ROOT, write_csv

PILOT_PATH = PROJECT_ROOT / "data" / "seed" / "pilot_zones_seed.csv"
EXPOSURE_PATH = PROJECT_ROOT / "data" / "processed" / "industry_ai_exposure_ex_ante_v2.csv"
ROBOT_PATH = PROJECT_ROOT / "data" / "processed" / "industry_robot_compatibility.csv"
PATENTS_PATH = PROJECT_ROOT / "data" / "processed" / "industrial_ai_patents_city_industry_year.csv"
SF_PATH = PROJECT_ROOT / "data" / "processed" / "smart_factory_city_industry_year.csv"

PATENT_COUNT_COLS = [
    "industrial_ai_patents",
    "machine_vision_patents",
    "robotics_patents",
    "predictive_maintenance_patents",
    "digital_twin_patents",
    "quality_inspection_patents",
    "process_control_patents",
]

ATLAS_COLUMNS = [
    "city",
    "province",
    "industry_code",
    "industry",
    "year",
    "pilot_zone",
    "pilot_year",
    "post_pilot",
    "years_since_pilot",
    "ai_exposure_ex_ante",
    "robot_compatibility",
    "smart_factory_count",
    "smart_factory_excellence_count",
    "industrial_ai_patents",
    "machine_vision_patents",
    "robotics_patents",
    "predictive_maintenance_patents",
    "digital_twin_patents",
    "quality_inspection_patents",
    "process_control_patents",
    "industrial_ai_procurement_count",
    "industrial_ai_procurement_value",
    "aid_equal_index",
    "procurement_layer_status",
    "source_coverage_flags",
]


def _zscore(series: pd.Series) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce").fillna(0.0)
    std = s.std(ddof=0)
    if std == 0 or np.isnan(std):
        return pd.Series(0.0, index=series.index)
    return (s - s.mean()) / std


def _load_pilot_city_year() -> pd.DataFrame:
    pilots = pd.read_csv(PILOT_PATH)
    pilots = pilots.rename(columns={"location": "city", "province_or_municipality": "province"})
    pilots["pilot_year"] = pd.to_numeric(pilots["pilot_year"], errors="coerce")
    rows = []
    for year in range(2015, 2026):
        for _, row in pilots.iterrows():
            py = row["pilot_year"]
            if pd.isna(py):
                continue
            py = int(py)
            rows.append(
                {
                    "city": row["city"],
                    "province": row["province"],
                    "year": year,
                    "pilot_zone": 1,
                    "pilot_year": py,
                    "post_pilot": int(year >= py),
                    "years_since_pilot": year - py,
                }
            )
    return pd.DataFrame(rows)


def _harmonize_city_province(df: pd.DataFrame) -> pd.DataFrame:
    """One canonical province per city (mode) to avoid cross-province duplicate keys."""
    if df.empty:
        return df
    mode_prov = df.groupby("city")["province"].agg(
        lambda s: s.mode().iloc[0] if len(s.mode()) else s.iloc[0]
    )
    out = df.copy()
    out["province"] = out["city"].map(mode_prov)
    return out


def build_atlas_v02(
    out_path: Path | None = None,
) -> pd.DataFrame:
    out_path = out_path or PROJECT_ROOT / "data" / "processed" / "china_ai_diffusion_atlas_city_industry_year.csv"

    patents = _harmonize_city_province(pd.read_csv(PATENTS_PATH))
    sf = _harmonize_city_province(pd.read_csv(SF_PATH))
    exposure = pd.read_csv(EXPOSURE_PATH)[["industry_code", "ai_exposure_ex_ante"]]
    robot = pd.read_csv(ROBOT_PATH)[["industry_code", "robot_compatibility"]]

    patents = patents.rename(columns={"industry": "industry_patent", "province": "province_p"})
    sf = sf.rename(columns={"industry": "industry_sf", "province": "province_s"})

    keys = ["city", "industry_code", "year"]
    panel = patents.merge(sf, on=keys, how="outer", suffixes=("", "_sf"))
    panel["province"] = panel["province_p"].fillna(panel["province_s"])
    panel["industry"] = panel["industry_patent"].fillna(panel["industry_sf"])
    drop_cols = [c for c in panel.columns if c.endswith("_p") or c.endswith("_s") or c in ("industry_patent", "industry_sf")]
    panel = panel.drop(columns=[c for c in drop_cols if c in panel.columns])

    for col in (
        "smart_factory_count",
        "smart_factory_excellence_count",
        "official_location_exact_count",
        "rule_based_count",
        "external_verified_count",
    ):
        if col not in panel.columns:
            panel[col] = 0
        panel[col] = panel[col].fillna(0)

    for col in PATENT_COUNT_COLS:
        if col not in panel.columns:
            panel[col] = 0
        panel[col] = panel[col].fillna(0)

    pilot = _load_pilot_city_year()
    panel = panel.merge(pilot, on=["city", "province", "year"], how="left")
    panel["pilot_zone"] = panel["pilot_zone"].fillna(0).astype(int)
    panel["post_pilot"] = panel["post_pilot"].fillna(0).astype(int)
    panel["years_since_pilot"] = panel["years_since_pilot"].fillna(np.nan)

    panel = panel.merge(exposure, on="industry_code", how="left")
    panel = panel.merge(robot, on="industry_code", how="left")

    panel["industrial_ai_procurement_count"] = 0
    panel["industrial_ai_procurement_value"] = np.nan
    panel["procurement_layer_status"] = "pending"

    panel["post_x_exposure"] = panel["post_pilot"] * panel["ai_exposure_ex_ante"]
    panel["robot_x_exposure"] = panel["robot_compatibility"] * panel["ai_exposure_ex_ante"]
    panel["aid_equal_index"] = (
        _zscore(panel["smart_factory_count"])
        + _zscore(panel["industrial_ai_patents"])
        + _zscore(panel["post_x_exposure"])
        + _zscore(panel["robot_x_exposure"])
    ) / 4.0

    panel["source_coverage_flags"] = (
        "patents="
        + (panel["industrial_ai_patents"] > 0).astype(int).astype(str)
        + ";smart_factories="
        + (panel["smart_factory_count"] > 0).astype(int).astype(str)
        + ";procurement=pending"
    )

    out = panel[ATLAS_COLUMNS].copy()
    write_csv(out, out_path)

    tables = PROJECT_ROOT / "outputs" / "tables"
    tables.mkdir(parents=True, exist_ok=True)
    coverage = pd.DataFrame(
        [
            {"metric": "n_rows", "value": len(out)},
            {"metric": "n_cities", "value": out["city"].nunique()},
            {"metric": "n_industries", "value": out["industry_code"].nunique()},
            {"metric": "year_min", "value": int(out["year"].min())},
            {"metric": "year_max", "value": int(out["year"].max())},
            {"metric": "total_smart_factories", "value": int(out["smart_factory_count"].sum())},
            {"metric": "total_industrial_ai_patents", "value": int(out["industrial_ai_patents"].sum())},
        ]
    )
    write_csv(coverage, tables / "table_E1_atlas_coverage.csv")

    miss = out.isna().mean().reset_index()
    miss.columns = ["column", "missing_share"]
    write_csv(miss, tables / "table_E2_atlas_missingness.csv")

    components = pd.DataFrame(
        {
            "component": [
                "z_smart_factory_count",
                "z_industrial_ai_patents",
                "z_post_pilot_x_ai_exposure",
                "z_robot_compatibility_x_ai_exposure",
            ],
            "weight": [0.25, 0.25, 0.25, 0.25],
        }
    )
    write_csv(components, tables / "table_E3_diffusion_index_components.csv")

    return out
