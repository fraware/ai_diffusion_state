"""Export patent keys from IIDS CSV for targeted geography acquisition."""
from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from diffusion_state.iids_paths import FILTERED_PATENT_IDS_FOR_GEO_OUTPUT, PATENT_KEYS_FOR_GEO_OUTPUT

KEY_COLUMNS = (
    "patent_id",
    "publication_number",
    "applicant_name",
    "patent_title",
    "application_year",
    "publication_year",
    "search_keyword",
)


@dataclass(frozen=True)
class PatentKeyExportStats:
    input_rows: int
    unique_patent_ids: int
    output_path: Path
    alias_path: Path | None


def export_patent_keys_for_geography(
    iids_csv: Path,
    output_csv: Path = PATENT_KEYS_FOR_GEO_OUTPUT,
    *,
    alias_csv: Path | None = FILTERED_PATENT_IDS_FOR_GEO_OUTPUT,
) -> PatentKeyExportStats:
    if not iids_csv.exists():
        raise FileNotFoundError(f"IIDS CSV not found: {iids_csv}")

    df = pd.read_csv(iids_csv, low_memory=False)
    if df.empty:
        raise ValueError(f"IIDS CSV is empty: {iids_csv}")

    out = pd.DataFrame()
    out["patent_id"] = df["patent_id"].astype(str).str.strip()
    out["publication_number"] = out["patent_id"]
    for col in ("applicant_name", "patent_title", "application_year", "publication_year", "search_keyword"):
        out[col] = df[col].astype(str).str.strip() if col in df.columns else ""

    out = out[list(KEY_COLUMNS)]
    out = out.drop_duplicates(subset=["patent_id"], keep="first")
    out = out[out["patent_id"].str.len().gt(0)].sort_values(["application_year", "patent_id"])

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_csv, index=False, encoding="utf-8-sig")

    written_alias: Path | None = None
    if alias_csv is not None and alias_csv.resolve() != output_csv.resolve():
        alias_csv.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(output_csv, alias_csv)
        written_alias = alias_csv

    return PatentKeyExportStats(
        input_rows=len(df),
        unique_patent_ids=len(out),
        output_path=output_csv,
        alias_path=written_alias,
    )
