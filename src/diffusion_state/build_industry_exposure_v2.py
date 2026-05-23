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
EXPOSURE_VERSION = "v2_ex_ante_manual"


def _attach_exposure_metadata(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["source_url_or_citation"] = df.get("classification_source", "").astype(str).str.strip()
    df.loc[df["source_url_or_citation"] == "", "source_url_or_citation"] = (
        "Expert-coded ex-ante industry exposure (see data/seed/industry_ai_exposure_ex_ante_v2_seed.csv)"
    )
    df["not_outcome_derived"] = True
    df["exposure_version"] = EXPOSURE_VERSION
    for col in EXPOSURE_DIMS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["ai_exposure_ex_ante"] = df[EXPOSURE_DIMS].mean(axis=1, skipna=True)
    df["ai_exposure_binary_high"] = (df["ai_exposure_ex_ante"] >= 1.5).astype(int)
    df["ai_exposure_rank"] = df["ai_exposure_ex_ante"].rank(method="average")
    leave_mv = [c for c in EXPOSURE_DIMS if c != "machine_vision_exposure"]
    leave_robot = [c for c in EXPOSURE_DIMS if c != "robotics_exposure"]
    df["ai_exposure_leave_out_machine_vision"] = df[leave_mv].mean(axis=1, skipna=True)
    df["ai_exposure_leave_out_robotics"] = df[leave_robot].mean(axis=1, skipna=True)
    return df


def build_industry_ai_exposure_ex_ante_v2(
    seed_path: Path | None = None,
    out_path: Path | None = None,
) -> pd.DataFrame:
    seed_path = seed_path or SEED_PATH
    out_path = out_path or PROJECT_ROOT / "data" / "processed" / "industry_ai_exposure_ex_ante_v2.csv"
    df = _attach_exposure_metadata(pd.read_csv(seed_path))
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


def build_table_c2_exposure_sensitivity(exposure: pd.DataFrame) -> pd.DataFrame:
    out_path = PROJECT_ROOT / "outputs" / "tables" / "table_C2_exposure_sensitivity_versions.csv"
    rows = []
    version_cols = {
        "ai_exposure_ex_ante": "baseline_mean_dims",
        "ai_exposure_binary_high": "binary_high_ge_1p5",
        "ai_exposure_rank": "rank_average",
        "ai_exposure_leave_out_machine_vision": "leave_out_machine_vision",
        "ai_exposure_leave_out_robotics": "leave_out_robotics",
    }
    for _, row in exposure.iterrows():
        for col, version in version_cols.items():
            rows.append(
                {
                    "industry_code": row["industry_code"],
                    "industry": row.get("industry", ""),
                    "exposure_version": row.get("exposure_version", EXPOSURE_VERSION),
                    "sensitivity_version": version,
                    "exposure_value": row[col],
                    "source_url_or_citation": row.get("source_url_or_citation", ""),
                    "not_outcome_derived": row.get("not_outcome_derived", True),
                }
            )
    out = pd.DataFrame(rows)
    write_csv(out, out_path)
    return out


def build_industry_exposure_v2() -> tuple[pd.DataFrame, pd.DataFrame]:
    exposure = build_industry_ai_exposure_ex_ante_v2()
    robot = build_industry_robot_compatibility()
    build_table_c1_exposure_scores(exposure, robot)
    build_table_c2_exposure_sensitivity(exposure)
    return exposure, robot
