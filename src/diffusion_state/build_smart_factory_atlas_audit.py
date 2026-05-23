from __future__ import annotations

from pathlib import Path

import pandas as pd

from diffusion_state.atlas_industry_map import map_legacy_industry_code
from diffusion_state.utils import PROJECT_ROOT, write_csv

CLEAN_PATH = PROJECT_ROOT / "data" / "processed" / "smart_factories_clean.csv"
SF_PANEL_PATH = PROJECT_ROOT / "data" / "processed" / "smart_factory_city_industry_year.csv"
SF1_PATH = PROJECT_ROOT / "outputs" / "tables" / "table_SF1_smart_factory_industry_mapping_audit.csv"
SF2_PATH = PROJECT_ROOT / "outputs" / "tables" / "table_SF2_smart_factory_city_industry_top_cells.csv"


def _sf_count_column(panel: pd.DataFrame) -> str:
    if "smart_factory_count" in panel.columns:
        return "smart_factory_count"
    if "smart_factory_projects" in panel.columns:
        return "smart_factory_projects"
    raise KeyError("smart-factory panel missing count column")


def build_sf1_industry_mapping_audit(clean_path: Path | None = None) -> pd.DataFrame:
    clean_path = clean_path or CLEAN_PATH
    clean = pd.read_csv(clean_path)
    clean = clean[clean["city"].astype(str) != "unknown"].copy()
    clean["atlas_industry_code"] = clean["industry_code"].map(map_legacy_industry_code)
    conf = clean.get("industry_confidence", pd.Series("medium", index=clean.index)).astype(str).str.lower()
    clean["_conf"] = conf.where(conf.isin(["high", "medium", "low"]), "medium")

    audit = (
        clean.groupby(["industry_code", "atlas_industry_code", "_conf"], as_index=False)
        .agg(
            n_projects=("project_id", "nunique"),
            n_cities=("city", "nunique"),
        )
        .rename(columns={"_conf": "industry_mapping_confidence"})
        .sort_values("n_projects", ascending=False)
    )
    audit["share_of_509"] = audit["n_projects"] / 509.0
    SF1_PATH.parent.mkdir(parents=True, exist_ok=True)
    write_csv(audit, SF1_PATH)
    return audit


def build_sf2_top_cells(panel_path: Path | None = None) -> pd.DataFrame:
    panel_path = panel_path or SF_PANEL_PATH
    panel = pd.read_csv(panel_path)
    count_col = _sf_count_column(panel)
    cols = ["city", "province", "industry_code", "year", count_col]
    if "industry" in panel.columns:
        cols.insert(3, "industry")
    elif "industry_label" in panel.columns:
        cols.insert(3, "industry_label")
    for optional in ("external_verified_count", "industry_mapping_confidence"):
        if optional in panel.columns:
            cols.append(optional)
    top = panel.sort_values(count_col, ascending=False).head(30)[cols].copy()
    write_csv(top, SF2_PATH)
    return top


def validate_smart_factory_audit() -> list[str]:
    errors: list[str] = []
    if not CLEAN_PATH.exists():
        return ["missing smart_factories_clean.csv"]
    clean = pd.read_csv(CLEAN_PATH)
    clean = clean[clean["city"].astype(str) != "unknown"]
    n_projects = int(clean["project_id"].nunique())
    if n_projects != 509:
        errors.append(f"expected 509 unique project_id before aggregation; got {n_projects}")

    if not SF_PANEL_PATH.exists():
        errors.append("missing smart_factory_city_industry_year.csv")
        return errors

    panel = pd.read_csv(SF_PANEL_PATH)
    count_col = _sf_count_column(panel)
    total_sf = int(panel[count_col].sum())
    if total_sf != 509:
        errors.append(f"sum({count_col})={total_sf}, expected 509")

    if "external_verified_count" not in panel.columns:
        errors.append("missing external_verified_count on smart-factory panel")
        return errors
    ext = int(panel["external_verified_count"].sum())
    if ext != 50:
        errors.append(f"external_verified_count sum={ext}, expected 50")

    if "industry_mapping_confidence" in panel.columns:
        conf = panel["industry_mapping_confidence"].astype(str).str.lower()
        weights = panel[count_col].astype(float)
        hm_share = float((conf.isin(["high", "medium"]) * weights).sum() / weights.sum())
        if hm_share < 0.8:
            errors.append(
                f"high/medium industry mapping confidence below 80% (weighted); got {hm_share:.1%}"
            )

    clean["atlas_industry_code"] = clean["industry_code"].map(map_legacy_industry_code)
    dup = clean.groupby("project_id")["atlas_industry_code"].nunique()
    if (dup > 1).any():
        errors.append("project double-counted across industries detected")

    return errors


def build_smart_factory_atlas_audit() -> tuple[pd.DataFrame, pd.DataFrame]:
    sf1 = build_sf1_industry_mapping_audit()
    sf2 = build_sf2_top_cells()
    return sf1, sf2
