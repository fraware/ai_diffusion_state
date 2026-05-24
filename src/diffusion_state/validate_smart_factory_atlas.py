from __future__ import annotations

import pandas as pd

from diffusion_state.utils import PROJECT_ROOT


def _count_column(df: pd.DataFrame) -> str:
    if "smart_factory_count" in df.columns:
        return "smart_factory_count"
    if "smart_factory_projects" in df.columns:
        return "smart_factory_projects"
    raise KeyError("smart-factory panel missing count column")


def validate_smart_factory_city_industry_year() -> list[str]:
    errors: list[str] = []
    path = PROJECT_ROOT / "data" / "processed" / "smart_factory_city_industry_year.csv"
    if not path.exists():
        return ["missing smart_factory_city_industry_year.csv — run make atlas-smartfactories"]

    df = pd.read_csv(path)
    count_col = _count_column(df)
    total = int(df[count_col].sum())
    if total != 509:
        errors.append(f"smart_factory_count total must be 509; got {total}")

    by_year = df.groupby("year")[count_col].sum()
    if int(by_year.get(2024, 0)) != 235:
        errors.append(f"2024 count must be 235; got {int(by_year.get(2024, 0))}")
    if int(by_year.get(2025, 0)) != 274:
        errors.append(f"2025 count must be 274; got {int(by_year.get(2025, 0))}")

    external = int(df["external_verified_count"].sum()) if "external_verified_count" in df.columns else 0
    if "external_verified_count" not in df.columns:
        errors.append("missing external_verified_count column — run make atlas-smartfactories")
    elif external != 50:
        errors.append(f"external_verified_count must be 50; got {external}")

    if "industry_mapping_confidence" in df.columns:
        conf = df["industry_mapping_confidence"].astype(str).str.lower()
        weights = df[count_col].astype(float)
        is_high_med = conf.isin({"high", "medium"})
        high_med_share = float((is_high_med * weights).sum() / weights.sum()) if weights.sum() else 0.0
        if high_med_share < 0.80:
            errors.append(
                f"need 80%+ high/medium industry mapping confidence (project-weighted); got {high_med_share:.1%}"
            )
    else:
        errors.append("missing industry_mapping_confidence — run make atlas-smartfactories")

    return errors
