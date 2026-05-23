from __future__ import annotations

import pandas as pd

from diffusion_state.patent_taxonomy import CATEGORY_COLUMNS
from diffusion_state.utils import PROJECT_ROOT

YEAR_MIN = 2015
YEAR_MAX = 2024


def validate_industrial_ai_patents_phase1() -> list[str]:
    errors: list[str] = []
    panel_path = PROJECT_ROOT / "data" / "processed" / "industrial_ai_patents_city_industry_year.csv"
    if not panel_path.exists():
        return ["missing industrial_ai_patents_city_industry_year.csv"]

    panel = pd.read_csv(panel_path)
    required = {"city", "province", "industry_code", "industry", "year"}
    missing_cols = required - set(panel.columns)
    if missing_cols:
        errors.append(f"panel missing columns: {sorted(missing_cols)}")

    if panel.duplicated(subset=["city", "industry_code", "year"]).any():
        errors.append("duplicate city-industry-year rows in patent panel")

    null_keys = panel[
        panel["city"].isna()
        | panel["province"].isna()
        | panel["industry_code"].isna()
        | panel["year"].isna()
    ]
    if len(null_keys):
        errors.append(f"{len(null_keys)} rows missing city/province/industry/year")

    years = panel["year"].dropna().astype(int)
    if years.min() > YEAR_MIN or years.max() < YEAR_MAX:
        errors.append(
            f"year coverage {int(years.min())}-{int(years.max())} "
            f"(expected span within {YEAR_MIN}-{YEAR_MAX})"
        )

    cities_nz = panel.groupby("city")["industrial_ai_patents"].sum()
    cities_with = int((cities_nz > 0).sum())
    if cities_with < 50:
        errors.append(f"need 50+ cities with patents; got {cities_with}")

    inds_nz = panel.groupby("industry_code")["industrial_ai_patents"].sum()
    if int((inds_nz > 0).sum()) < 10:
        errors.append(f"need 10+ industries with patents; got {int((inds_nz > 0).sum())}")

    cats_populated = 0
    for cat in CATEGORY_COLUMNS:
        col = f"{cat}_patents"
        if col in panel.columns and panel[col].sum() > 0:
            cats_populated += 1
    if cats_populated < 5:
        errors.append(f"need 5+ patent categories populated; got {cats_populated}")

    return errors
