from __future__ import annotations

from pathlib import Path

import pandas as pd

from diffusion_state.atlas_industry_map import map_legacy_industry_code
from diffusion_state.build_geo_evidence_quality import build_city_resolution_register
from diffusion_state.utils import PROJECT_ROOT, write_csv

OUTPUT_COLUMNS = [
    "city",
    "province",
    "industry_code",
    "industry",
    "year",
    "smart_factory_count",
    "smart_factory_excellence_count",
    "official_location_exact_count",
    "rule_based_count",
    "external_verified_count",
    "industry_mapping_confidence",
]


def _mapping_confidence(row: pd.Series) -> str:
    conf = str(row.get("industry_confidence", "")).strip().lower()
    if conf in ("high", "medium", "low"):
        return conf
    return "medium"


def build_smart_factory_city_industry_year(
    clean_path: Path | None = None,
    register_path: Path | None = None,
    out_path: Path | None = None,
) -> pd.DataFrame:
    clean_path = clean_path or PROJECT_ROOT / "data" / "processed" / "smart_factories_clean.csv"
    register_path = register_path or PROJECT_ROOT / "data" / "processed" / "city_resolution_register.csv"
    out_path = out_path or PROJECT_ROOT / "data" / "processed" / "smart_factory_city_industry_year.csv"

    if not register_path.exists():
        build_city_resolution_register(clean_path=clean_path, out_path=register_path)

    clean = pd.read_csv(clean_path)
    reg = pd.read_csv(register_path)[["project_id", "resolution_class"]]
    clean = clean.merge(reg, on="project_id", how="left")

    clean = clean[clean["city"].astype(str) != "unknown"].copy()
    prov_mode = clean.groupby("city")["province"].agg(
        lambda s: s.mode().iloc[0] if len(s.mode()) else s.iloc[0]
    )
    clean["province"] = clean["city"].map(prov_mode)
    clean["year"] = clean["list_year"].astype(int)
    clean["atlas_industry_code"] = clean["industry_code"].map(map_legacy_industry_code)
    clean["_project_confidence"] = clean.apply(_mapping_confidence, axis=1)
    clean["is_excellence"] = clean["batch"].astype(str).str.contains("excellence", case=False).astype(int)
    clean["is_official"] = (clean["resolution_class"] == "official_location_exact").astype(int)
    clean["is_rule_based"] = (clean["resolution_class"] == "rule_based_text_inference").astype(int)
    clean["is_external"] = (clean["resolution_class"] == "external_evidence_verified").astype(int)

    crosswalk = pd.read_csv(PROJECT_ROOT / "data" / "seed" / "industry_crosswalk_atlas.csv")
    label_map = dict(zip(crosswalk["industry_code"], crosswalk["industry"]))
    cross_conf = dict(
        zip(
            crosswalk["industry_code"],
            crosswalk["mapping_confidence_default"].astype(str).str.lower(),
        )
    )

    rank = {"high": 3, "medium": 2, "low": 1}
    clean["_project_conf_rank"] = clean["_project_confidence"].map(rank).fillna(2)
    clean["_cross_conf_rank"] = clean["atlas_industry_code"].map(
        lambda c: rank.get(cross_conf.get(str(c), "medium"), 2)
    )
    clean["_conf_rank"] = clean[["_project_conf_rank", "_cross_conf_rank"]].max(axis=1)

    agg = (
        clean.groupby(["city", "province", "atlas_industry_code", "year"], as_index=False)
        .agg(
            smart_factory_count=("project_id", "count"),
            smart_factory_excellence_count=("is_excellence", "sum"),
            official_location_exact_count=("is_official", "sum"),
            rule_based_count=("is_rule_based", "sum"),
            external_verified_count=("is_external", "sum"),
            _conf_rank=("_conf_rank", "max"),
        )
        .rename(columns={"atlas_industry_code": "industry_code"})
    )
    inv_rank = {v: k for k, v in rank.items()}
    agg["industry_mapping_confidence"] = agg["_conf_rank"].map(inv_rank).fillna("medium")
    agg = agg.drop(columns=["_conf_rank"])
    agg["industry"] = agg["industry_code"].map(label_map).fillna(agg["industry_code"])
    write_csv(agg[OUTPUT_COLUMNS], out_path)
    return agg[OUTPUT_COLUMNS]
