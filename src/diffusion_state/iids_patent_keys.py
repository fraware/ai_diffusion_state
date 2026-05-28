"""Export patent keys from IIDS CSV for targeted geography acquisition."""
from __future__ import annotations

import csv
import shutil
from dataclasses import dataclass
from pathlib import Path

from diffusion_state.iids_paths import (
    FILTERED_PATENT_IDS_FOR_GEO_OUTPUT,
    PATENT_KEYS_FOR_GEO_OUTPUT,
)

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


def _cell(row: dict[str, str], col: str) -> str:
    val = row.get(col, "")
    if val is None:
        return ""
    return str(val).strip()


def export_patent_keys_for_geography(
    iids_csv: Path,
    output_csv: Path = PATENT_KEYS_FOR_GEO_OUTPUT,
    *,
    alias_csv: Path | None = FILTERED_PATENT_IDS_FOR_GEO_OUTPUT,
) -> PatentKeyExportStats:
    if not iids_csv.exists():
        raise FileNotFoundError(f"IIDS CSV not found: {iids_csv}")

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    seen: set[str] = set()
    input_rows = 0
    unique_patent_ids = 0

    with iids_csv.open(
        "r", encoding="utf-8-sig", errors="replace", newline=""
    ) as f_in:
        reader = csv.DictReader(f_in)
        if not reader.fieldnames:
            raise ValueError(f"IIDS CSV has no header: {iids_csv}")

        with output_csv.open("w", encoding="utf-8-sig", newline="") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=list(KEY_COLUMNS))
            writer.writeheader()

            for row in reader:
                input_rows += 1
                patent_id = _cell(row, "patent_id")
                if not patent_id or patent_id in seen:
                    continue
                seen.add(patent_id)
                writer.writerow(
                    {
                        "patent_id": patent_id,
                        "publication_number": patent_id,
                        "applicant_name": _cell(row, "applicant_name"),
                        "patent_title": _cell(row, "patent_title"),
                        "application_year": _cell(row, "application_year"),
                        "publication_year": _cell(row, "publication_year"),
                        "search_keyword": _cell(row, "search_keyword"),
                    }
                )
                unique_patent_ids += 1

    if input_rows == 0:
        raise ValueError(f"IIDS CSV is empty: {iids_csv}")
    if unique_patent_ids == 0:
        raise ValueError(f"No patent_id values found in {iids_csv}")

    written_alias: Path | None = None
    if alias_csv is not None and alias_csv.resolve() != output_csv.resolve():
        alias_csv.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(output_csv, alias_csv)
        written_alias = alias_csv

    print(f"Input rows: {input_rows}")
    print(f"Unique patent IDs: {unique_patent_ids}")

    return PatentKeyExportStats(
        input_rows=input_rows,
        unique_patent_ids=unique_patent_ids,
        output_path=output_csv,
        alias_path=written_alias,
    )
