from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from diffusion_state.utils import PROJECT_ROOT, write_csv

EXPOSURE_DIMS = [
    "machine_vision_exposure",
    "robotics_exposure",
    "predictive_maintenance_exposure",
    "digital_twin_exposure",
    "process_control_exposure",
    "quality_inspection_exposure",
    "smart_logistics_exposure",
    "industrial_software_exposure",
]

SEED_PATH = PROJECT_ROOT / "data" / "seed" / "industry_ai_exposure_ex_ante_v2_seed.csv"
ROBOT_SEED_PATH = PROJECT_ROOT / "data" / "seed" / "industry_robot_compatibility_seed.csv"


def build_industry_ai_exposure_ex_ante_v2(
    seed_path: Path | None = None,
    out_path: Path | None = None,
) -> pd.DataFrame:
    seed_path = seed_path or SEED_PATH
    out_path = out_path or PROJECT_ROOT / "data" / "processed" / "industry_ai_exposure_ex_ante_v2.csv"
    df = pd.read_csv(seed_path)
    for col in EXPOSURE_DIMS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["ai_exposure_ex_ante"] = df[EXPOSURE_DIMS].mean(axis=1, skipna=True)
    write_csv(df, out_path)
    return df


def build_industry_robot_compatibility(
    seed_path: Path | None = None,
    out_path: Path | None = None,
) -> pd.DataFrame:
    seed_path = seed_path or ROBOT_SEED_PATH
    out_path = out_path or PROJECT_ROOT / "data" / "processed" / "industry_robot_compatibility.csv"
    df = pd.read_csv(seed_path)
    df["robot_compatibility"] = pd.to_numeric(df["robot_compatibility"], errors="coerce")
    write_csv(df, out_path)
    return df


def build_table_c1_exposure_scores(
    exposure: pd.DataFrame,
    robot: pd.DataFrame,
    out_path: Path | None = None,
) -> pd.DataFrame:
    out_path = out_path or PROJECT_ROOT / "outputs" / "tables" / "table_C1_industry_exposure_scores.csv"
    merged = exposure.merge(
        robot[["industry_code", "robot_compatibility"]],
        on="industry_code",
        how="left",
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_csv(merged, out_path)
    return merged


def build_industry_exposure_v2() -> tuple[pd.DataFrame, pd.DataFrame]:
    exposure = build_industry_ai_exposure_ex_ante_v2()
    robot = build_industry_robot_compatibility()
    build_table_c1_exposure_scores(exposure, robot)
    return exposure, robot
