"""Export patent keys from IIDS CSV for targeted geography acquisition."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

KEY_COLUMNS = (
    "patent_id",
    "publication_number",
    "applicant_name",
    "application_year",
    "publication_year",
    "search_keyword",
)


@dataclass(frozen=True)
class PatentKeyExportStats:
    input_rows: int
    unique_patent_ids: int
    output_path: Path


def export_patent_keys_for_geography(
    iids_csv: Path,
    output_csv: Path,
) -> PatentKeyExportStats:
    if not iids_csv.exists():
        raise FileNotFoundError(f"IIDS CSV not found: {iids_csv}")

    df = pd.read_csv(iids_csv, low_memory=False)
    if df.empty:
        raise ValueError(f"IIDS CSV is empty: {iids_csv}")

    out = pd.DataFrame()
    out["patent_id"] = df["patent_id"].astype(str).str.strip()
    out["publication_number"] = out["patent_id"]
    for col in KEY_COLUMNS[2:]:
        out[col] = df[col].astype(str).str.strip() if col in df.columns else ""

    out = out.drop_duplicates(subset=["patent_id"], keep="first")
    out = out[out["patent_id"].str.len().gt(0)].sort_values(["application_year", "patent_id"])

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_csv, index=False, encoding="utf-8-sig")

    return PatentKeyExportStats(
        input_rows=len(df),
        unique_patent_ids=len(out),
        output_path=output_csv,
    )
