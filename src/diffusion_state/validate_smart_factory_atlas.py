from __future__ import annotations

import pandas as pd

from diffusion_state.utils import PROJECT_ROOT


def validate_smart_factory_city_industry_year() -> list[str]:
    errors: list[str] = []
    path = PROJECT_ROOT / "data" / "processed" / "smart_factory_city_industry_year.csv"
    if not path.exists():
        return ["missing smart_factory_city_industry_year.csv"]

    df = pd.read_csv(path)
    total = int(df["smart_factory_count"].sum())
    if total != 509:
        errors.append(f"smart_factory_count total must be 509; got {total}")

    by_year = df.groupby("year")["smart_factory_count"].sum()
    if int(by_year.get(2024, 0)) != 235:
        errors.append(f"2024 count must be 235; got {int(by_year.get(2024, 0))}")
    if int(by_year.get(2025, 0)) != 274:
        errors.append(f"2025 count must be 274; got {int(by_year.get(2025, 0))}")

    external = int(df["external_verified_count"].sum())
    if external != 50:
        errors.append(f"external_verified_count must be 50; got {external}")

    conf = df["industry_mapping_confidence"].astype(str).str.lower()
    weights = df["smart_factory_count"].astype(float)
    is_high_med = conf.isin({"high", "medium"})
    high_med_share = float((is_high_med * weights).sum() / weights.sum()) if weights.sum() else 0.0
    if high_med_share < 0.80:
        errors.append(
            f"need 80%+ high/medium industry mapping confidence (project-weighted); got {high_med_share:.1%}"
        )

    return errors
