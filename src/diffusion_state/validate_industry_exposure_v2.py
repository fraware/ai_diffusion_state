from __future__ import annotations

import re

import pandas as pd

from diffusion_state.build_industry_exposure_v2 import EXPOSURE_DIMS
from diffusion_state.utils import PROJECT_ROOT

FORBIDDEN_REASON = re.compile(
    r"smart[\s_-]?factory|outcome|observed\s+count|many\s+projects",
    re.IGNORECASE,
)


def validate_industry_exposure_v2() -> list[str]:
    errors: list[str] = []
    exposure_path = PROJECT_ROOT / "data" / "processed" / "industry_ai_exposure_ex_ante_v2.csv"
    robot_path = PROJECT_ROOT / "data" / "processed" / "industry_robot_compatibility.csv"

    if not exposure_path.exists():
        return ["missing industry_ai_exposure_ex_ante_v2.csv — run scripts/40_build_industry_exposure_v2.py"]
    if not robot_path.exists():
        return ["missing industry_robot_compatibility.csv — run scripts/40_build_industry_exposure_v2.py"]

    exposure = pd.read_csv(exposure_path)
    robot = pd.read_csv(robot_path)

    if len(exposure) < 25:
        errors.append(f"need 25+ industries; got {len(exposure)}")

    high_med = exposure[exposure["ai_exposure_ex_ante"] >= 1.0]
    if len(high_med) < 15:
        errors.append(f"need 15+ high/medium AI-exposure industries; got {len(high_med)}")

    robot_pos = robot[robot["robot_compatibility"] >= 1]
    if len(robot_pos) < 15:
        errors.append(f"need 15+ robot-compatible industries; got {len(robot_pos)}")

    for col in (
        "source_url_or_citation",
        "not_outcome_derived",
        "exposure_version",
        "ai_exposure_binary_high",
        "ai_exposure_rank",
        "ai_exposure_leave_out_machine_vision",
        "ai_exposure_leave_out_robotics",
    ):
        if col not in exposure.columns:
            errors.append(f"missing exposure column: {col} — rebuild industry exposure v2")

    for _, row in exposure.iterrows():
        if pd.isna(row.get("ai_exposure_ex_ante")):
            errors.append(f"missing ai_exposure_ex_ante: {row.get('industry_code')}")
        if not str(row.get("source_url_or_citation", "")).strip():
            errors.append(f"missing source_url_or_citation: {row.get('industry_code')}")
        if row.get("not_outcome_derived") is not True and str(row.get("not_outcome_derived")).lower() not in (
            "true",
            "1",
        ):
            errors.append(f"not_outcome_derived must be true: {row.get('industry_code')}")
        reason = str(row.get("classification_reason", "")).strip()
        if not reason:
            errors.append(f"blank classification_reason: {row.get('industry_code')}")
        if FORBIDDEN_REASON.search(reason):
            errors.append(f"outcome-derived reason for {row.get('industry_code')}: {reason}")
        source = str(row.get("classification_source", "")).lower()
        if "smart factory" in source or "smart-factory" in source:
            errors.append(f"outcome-derived source for {row.get('industry_code')}")
        conf = str(row.get("confidence", "")).strip()
        if not conf:
            errors.append(f"missing confidence: {row.get('industry_code')}")

    for col in EXPOSURE_DIMS:
        if col not in exposure.columns:
            errors.append(f"missing exposure column: {col}")

    codes_exp = set(exposure["industry_code"].astype(str))
    codes_rob = set(robot["industry_code"].astype(str))
    if codes_exp != codes_rob:
        errors.append(
            f"industry_code mismatch exposure vs robot: "
            f"only exposure {sorted(codes_exp - codes_rob)[:5]} "
            f"only robot {sorted(codes_rob - codes_exp)[:5]}"
        )

    return errors
