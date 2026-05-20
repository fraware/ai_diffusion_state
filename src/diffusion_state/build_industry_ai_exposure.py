from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from diffusion_state.utils import PROJECT_ROOT, write_csv

HIGH_EXPOSURE_LABELS = {
    "semiconductors",
    "electronics",
    "ai_servers",
    "batteries",
    "automotive",
    "general_equipment",
    "special_equipment",
    "electrical_machinery",
    "metals",
    "railway_shipbuilding_aerospace",
    "pharma",
    "chemicals",
}

AI_TAG_KEYWORDS = {
    "machine_vision",
    "ai_quality_inspection",
    "predictive_maintenance",
    "digital_twin",
    "intelligent_scheduling",
    "industrial_robotics",
    "smart_logistics",
    "industrial_internet",
    "ai_server",
}


def build_industry_ai_exposure(
    clean_path: Path | None = None,
    out_path: Path | None = None,
) -> pd.DataFrame:
    clean_path = clean_path or PROJECT_ROOT / "data" / "processed" / "smart_factories_clean.csv"
    out_path = out_path or PROJECT_ROOT / "data" / "processed" / "industry_ai_exposure.csv"

    clean = pd.read_csv(clean_path)

    def _tag_score(tags: str) -> int:
        if pd.isna(tags) or not str(tags).strip():
            return 0
        parts = {t.strip() for t in str(tags).split(";") if t.strip()}
        return sum(1 for k in AI_TAG_KEYWORDS if k in parts)

    ind = (
        clean.groupby(["industry_code", "industry_label"], as_index=False)
        .agg(
            n_projects=("project_id", "count"),
            mean_ai_tags=("ai_scenario_tags", lambda s: float(np.mean([_tag_score(x) for x in s]))),
        )
    )
    ind["high_exposure_sector"] = ind["industry_label"].isin(HIGH_EXPOSURE_LABELS).astype(int)
    ind["ai_exposure_score"] = (
        ind["high_exposure_sector"] * 2 + ind["mean_ai_tags"].clip(lower=0)
    ).round(3)
    ind["ai_exposure_tier"] = pd.cut(
        ind["ai_exposure_score"],
        bins=[-0.01, 1.5, 3.5, 100],
        labels=["low", "medium", "high"],
    ).astype(str)

    write_csv(ind, out_path)
    return ind
