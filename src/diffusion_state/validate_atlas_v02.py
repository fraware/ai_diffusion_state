from __future__ import annotations

import pandas as pd

from diffusion_state.utils import PROJECT_ROOT
from diffusion_state.validate_smart_factory_atlas import _count_column


def validate_atlas_v02() -> list[str]:
    errors: list[str] = []
    atlas_path = PROJECT_ROOT / "data" / "processed" / "china_ai_diffusion_atlas_city_industry_year.csv"
    sf_path = PROJECT_ROOT / "data" / "processed" / "smart_factory_city_industry_year.csv"
    pat_path = PROJECT_ROOT / "data" / "processed" / "industrial_ai_patents_city_industry_year.csv"

    if not atlas_path.exists():
        return ["missing china_ai_diffusion_atlas_city_industry_year.csv"]

    atlas = pd.read_csv(atlas_path)
    if atlas.duplicated(subset=["city", "industry_code", "year"]).any():
        errors.append("duplicate city-industry-year rows in atlas")

    if atlas["city"].nunique() < 50:
        errors.append(f"need 50+ cities in atlas; got {atlas['city'].nunique()}")
    if atlas["industry_code"].nunique() < 20:
        errors.append(f"need 20+ industries in atlas; got {atlas['industry_code'].nunique()}")

    years = atlas["year"].astype(int)
    if years.min() > 2017 or years.max() < 2024:
        errors.append(f"year coverage {years.min()}-{years.max()} outside 2015-2025 expectation")

    if int(atlas["smart_factory_count"].sum()) != 509:
        errors.append(
            f"atlas smart_factory_count total must be 509; got {int(atlas['smart_factory_count'].sum())}"
        )

    if sf_path.exists() and pat_path.exists():
        sf = pd.read_csv(sf_path)
        pat = pd.read_csv(pat_path)
        sf_count_col = _count_column(sf)
        if int(sf[sf_count_col].sum()) != int(atlas["smart_factory_count"].sum()):
            errors.append("smart-factory totals mismatch between atlas and SF layer")
        if int(pat["industrial_ai_patents"].sum()) != int(atlas["industrial_ai_patents"].sum()):
            errors.append("patent totals mismatch between atlas and patent layer")

    if "procurement_layer_status" not in atlas.columns:
        errors.append("missing procurement_layer_status column")

    return errors
