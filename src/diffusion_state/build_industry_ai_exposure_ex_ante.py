from __future__ import annotations

from pathlib import Path

import pandas as pd

from diffusion_state.utils import PROJECT_ROOT, write_csv

SEED_PATH = PROJECT_ROOT / "data" / "seed" / "industry_ai_exposure_ex_ante.csv"
PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "industry_ai_exposure_ex_ante.csv"

REQUIRED_COLUMNS = [
    "industry_code",
    "industry_label",
    "ai_exposure_ex_ante",
    "robot_complementarity_ex_ante",
    "process_control_exposure",
    "machine_vision_exposure",
    "digital_twin_exposure",
    "classification_reason",
    "classification_source",
]


def build_industry_ai_exposure_ex_ante(
    seed_path: Path | None = None,
    out_path: Path | None = None,
) -> pd.DataFrame:
    seed_path = seed_path or SEED_PATH
    out_path = out_path or PROCESSED_PATH
    if not seed_path.exists():
        raise FileNotFoundError(f"Ex ante industry exposure seed missing: {seed_path}")

    df = pd.read_csv(seed_path)
    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Ex ante exposure seed missing columns: {sorted(missing)}")
    if df["industry_code"].duplicated().any():
        dupes = df.loc[df["industry_code"].duplicated(), "industry_code"].tolist()
        raise ValueError(f"Duplicate industry_code in ex ante seed: {dupes}")

    for col in [
        "ai_exposure_ex_ante",
        "robot_complementarity_ex_ante",
        "process_control_exposure",
        "machine_vision_exposure",
        "digital_twin_exposure",
    ]:
        if not df[col].isin([0, 1, 2]).all():
            raise ValueError(f"{col} must use 0=low, 1=medium, 2=high")

    df["high_exposure_ex_ante"] = (df["ai_exposure_ex_ante"] >= 2).astype(int)
    df["ai_exposure_ex_ante_tier"] = df["ai_exposure_ex_ante"].map(
        {0: "low", 1: "medium", 2: "high"}
    )
    write_csv(df, out_path)
    return df
