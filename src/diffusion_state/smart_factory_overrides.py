from __future__ import annotations

from pathlib import Path

import pandas as pd

from diffusion_state.utils import PROJECT_ROOT

REQUIRED_OVERRIDE_COLUMNS = [
    "project_id",
    "city",
    "province",
    "city_confidence",
    "notes",
]

OPTIONAL_OVERRIDE_COLUMNS = [
    "override_source",
    "evidence_url",
    "evidence_type",
    "reviewer",
    "review_date",
]

OVERRIDE_COLUMNS = REQUIRED_OVERRIDE_COLUMNS + [
    c for c in OPTIONAL_OVERRIDE_COLUMNS if c not in REQUIRED_OVERRIDE_COLUMNS
]

ALLOWED_OVERRIDE_CONFIDENCE = {"exact", "high", "medium"}


def load_city_overrides(path: Path | None = None) -> pd.DataFrame:
    path = path or PROJECT_ROOT / "data" / "seed" / "smart_factory_city_overrides.csv"
    if not path.exists():
        return pd.DataFrame(columns=OVERRIDE_COLUMNS)
    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=REQUIRED_OVERRIDE_COLUMNS)
    if df.empty and not set(df.columns):
        return pd.DataFrame(columns=REQUIRED_OVERRIDE_COLUMNS)
    missing = set(REQUIRED_OVERRIDE_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Override file missing columns: {sorted(missing)}")
    if df.empty:
        return df
    if df["project_id"].duplicated().any():
        dupes = df.loc[df["project_id"].duplicated(), "project_id"].tolist()
        raise ValueError(f"Duplicate project_id in overrides: {dupes}")
    bad_conf = set(df["city_confidence"].dropna().unique()) - ALLOWED_OVERRIDE_CONFIDENCE
    if bad_conf:
        raise ValueError(f"Invalid city_confidence in overrides: {bad_conf}")
    if df["notes"].isna().any() or (df["notes"].astype(str).str.strip() == "").any():
        raise ValueError("Every override row must have non-empty notes documenting evidence")
    cols = [c for c in OVERRIDE_COLUMNS if c in df.columns]
    return df[cols].copy()


def apply_city_overrides(df: pd.DataFrame, overrides: pd.DataFrame | None = None) -> pd.DataFrame:
    """Apply audited manual city assignments; does not impute missing rows."""
    overrides = overrides if overrides is not None else load_city_overrides()
    if overrides is None or overrides.empty:
        return df

    out = df.copy()
    missing = set(overrides["project_id"]) - set(out["project_id"])
    if missing:
        raise ValueError(f"Override project_id not in clean table: {sorted(missing)}")

    for _, row in overrides.iterrows():
        pid = row["project_id"]
        mask = out["project_id"] == pid
        if int(out.loc[mask, "manual_override_flag"].iloc[0]) == 1:
            continue
        out.loc[mask, "city"] = row["city"]
        out.loc[mask, "province"] = row["province"]
        out.loc[mask, "city_confidence"] = row["city_confidence"]
        out.loc[mask, "manual_override_flag"] = 1
        out.loc[mask, "parse_method"] = "manual_override"
        prior = out.loc[mask, "notes"].iloc[0]
        source = row.get("override_source", row.get("evidence_type", "audited"))
        out.loc[mask, "notes"] = (
            f"{prior}; manual override ({source}): {row['notes']}"
            if pd.notna(prior) and str(prior).strip()
            else f"manual override ({source}): {row['notes']}"
        )
    return out
