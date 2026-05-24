"""Prepare draft manifest rows for real Atlas patent exports.

This helper does not make fixture data evidentiary. It scans only allowed real-export
filenames at data/raw/patents/ repo root and writes a draft manifest with row counts
and schema diagnostics. The operator must still fill query metadata, license/access
notes, and export provenance before running the evidence gate.

Usage:
    python scripts/58_prepare_patent_source_manifest.py

Outputs:
    data/raw/patents/patent_source_manifest_draft.csv
    outputs/tables/table_P0_patent_export_schema_diagnostics.csv
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "patents"
OUT_DRAFT = RAW / "patent_source_manifest_draft.csv"
OUT_DIAG = ROOT / "outputs" / "tables" / "table_P0_patent_export_schema_diagnostics.csv"

ALLOWED_PATTERNS = [
    re.compile(r"^cnipa_industrial_ai_patents_.*\.csv$", re.I),
    re.compile(r"^lens_industrial_ai_patents_.*\.csv$", re.I),
    re.compile(r"^google_patents_industrial_ai_patents_.*\.csv$", re.I),
    re.compile(r"^cnki_industrial_ai_patents_.*\.csv$", re.I),
    re.compile(r"^cnrds_industrial_ai_patents_.*\.csv$", re.I),
    re.compile(r"^csmar_industrial_ai_patents_.*\.csv$", re.I),
    re.compile(r"^opendatalab_iids_industrial_ai_patents_.*\.csv$", re.I),
]

REQUIRED_COLUMNS = [
    "patent_id",
    "application_year",
    "publication_year",
    "grant_year",
    "applicant_name",
    "applicant_city",
    "applicant_province",
    "applicant_address",
    "patent_title",
    "abstract",
    "claims_or_description",
    "ipc_or_cpc",
    "patent_type",
    "source",
    "source_url_or_file",
    "search_keyword",
]

MANIFEST_COLUMNS = [
    "source_file",
    "source_platform",
    "export_date",
    "export_owner",
    "query_group",
    "query_string",
    "year_min",
    "year_max",
    "jurisdiction_filter",
    "record_count",
    "contains_applicant_address",
    "contains_city",
    "contains_abstract",
    "contains_claims",
    "license_or_access_note",
    "proprietary_or_public",
    "notes",
]


def is_allowed_real_export(path: Path) -> bool:
    if path.parent != RAW:
        return False
    return any(p.match(path.name) for p in ALLOWED_PATTERNS)


def infer_platform(filename: str) -> str:
    lower = filename.lower()
    if lower.startswith("cnipa_"):
        return "cnipa"
    if lower.startswith("lens_"):
        return "lens"
    if lower.startswith("google_patents_"):
        return "google_patents"
    if lower.startswith("cnki_"):
        return "cnki"
    if lower.startswith("cnrds_"):
        return "cnrds"
    if lower.startswith("csmar_"):
        return "csmar"
    if lower.startswith("opendatalab_iids_"):
        return "opendatalab_iids"
    return "unknown"


def count_rows_and_columns(path: Path) -> tuple[int, list[str]]:
    # Read header first, then count rows cheaply.
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
        reader = csv.reader(f)
        try:
            columns = next(reader)
        except StopIteration:
            return 0, []
        n = sum(1 for _ in reader)
    return n, [c.strip() for c in columns]


def iids_manifest_defaults(path: Path, colset: set[str], n: int) -> dict[str, object]:
    city_fill = False
    if n > 0 and "applicant_city" in colset:
        try:
            city = pd.read_csv(path, usecols=["applicant_city"], encoding="utf-8-sig")
            city_fill = float(city["applicant_city"].astype(str).str.strip().str.len().gt(0).mean()) >= 0.8
        except Exception:
            pass
    return {
        "export_date": "FILL_ME",
        "export_owner": "FILL_ME",
        "query_group": "industrial_ai_taxonomy",
        "query_string": "IIDS base_patent_detail.sql filtered CN 2015-2024 industrial-AI IPC/taxonomy",
        "license_or_access_note": "FILL_ME OpenXLab Gracie/IIDS access terms",
        "proprietary_or_public": "FILL_ME_PUBLIC_OR_PROPRIETARY",
        "contains_claims": False,
        "contains_city": city_fill,
        "contains_applicant_address": city_fill,
        "notes": (
            "OpenXLab IIDS converter output; claims_or_description falls back to abstract. "
            "Join cnipa_patent_geography_2015_2024.csv before evidence chain if city fill < 80%."
        ),
    }


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    OUT_DIAG.parent.mkdir(parents=True, exist_ok=True)
    files = sorted([p for p in RAW.glob("*.csv") if is_allowed_real_export(p)])
    manifest_rows = []
    diag_rows = []
    for path in files:
        n, cols = count_rows_and_columns(path)
        colset = set(cols)
        missing = [c for c in REQUIRED_COLUMNS if c not in colset]
        year_min = ""
        year_max = ""
        if "application_year" in colset and n > 0:
            try:
                years = pd.read_csv(path, usecols=["application_year"], encoding="utf-8-sig")
                yy = pd.to_numeric(years["application_year"], errors="coerce").dropna()
                if not yy.empty:
                    year_min = int(yy.min())
                    year_max = int(yy.max())
            except Exception:
                pass
        row = {
            "source_file": path.name,
            "source_platform": infer_platform(path.name),
            "export_date": "FILL_ME",
            "export_owner": "FILL_ME",
            "query_group": "FILL_ME",
            "query_string": "FILL_ME",
            "year_min": year_min,
            "year_max": year_max,
            "jurisdiction_filter": "CN",
            "record_count": n,
            "contains_applicant_address": "applicant_address" in colset,
            "contains_city": ("applicant_city" in colset and "applicant_province" in colset),
            "contains_abstract": "abstract" in colset,
            "contains_claims": "claims_or_description" in colset,
            "license_or_access_note": "FILL_ME",
            "proprietary_or_public": "FILL_ME_PUBLIC_OR_PROPRIETARY",
            "notes": "Draft row generated by scripts/58_prepare_patent_source_manifest.py; review before evidence gate.",
        }
        if infer_platform(path.name) == "opendatalab_iids":
            row.update(iids_manifest_defaults(path, colset, n))
        manifest_rows.append(row)
        diag_rows.append({
            "source_file": path.name,
            "record_count": n,
            "n_columns": len(cols),
            "missing_required_columns": ";".join(missing),
            "schema_ready": len(missing) == 0,
            "year_min": year_min,
            "year_max": year_max,
        })
    pd.DataFrame(manifest_rows, columns=MANIFEST_COLUMNS).to_csv(OUT_DRAFT, index=False, encoding="utf-8-sig")
    pd.DataFrame(diag_rows).to_csv(OUT_DIAG, index=False, encoding="utf-8-sig")
    print(f"Found {len(files)} allowed real patent export file(s).")
    print(f"Wrote draft manifest: {OUT_DRAFT}")
    print(f"Wrote schema diagnostics: {OUT_DIAG}")
    if not files:
        print("No real exports found. Place allowed files at data/raw/patents/ repo root.")
        return 1
    bad = [r for r in diag_rows if not r["schema_ready"]]
    if bad:
        print("Some files are missing required columns; inspect table_P0 diagnostics before running atlas-patents.")
        return 2
    print("All detected real export files have the required schema. Fill manifest metadata before evidence gate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
