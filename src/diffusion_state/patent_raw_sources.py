from __future__ import annotations

import re
from pathlib import Path

from diffusion_state.utils import PROJECT_ROOT

RAW_PATENTS_DIR = PROJECT_ROOT / "data" / "raw" / "patents"
FIXTURES_DIR = RAW_PATENTS_DIR / "fixtures"
MANIFEST_PATH = RAW_PATENTS_DIR / "patent_source_manifest.csv"

FIXTURE_BASENAMES = frozenset(
    {
        "industrial_ai_patent_records.csv",
        "cnipa_micro.csv",
        "patent_database.csv",
    }
)

REAL_EXPORT_PATTERNS = (
    re.compile(r"^cnipa_industrial_ai_patents_.*\.csv$", re.I),
    re.compile(r"^lens_industrial_ai_patents_.*\.csv$", re.I),
    re.compile(r"^google_patents_industrial_ai_patents_.*\.csv$", re.I),
    re.compile(r"^cnki_industrial_ai_patents_.*\.csv$", re.I),
    re.compile(r"^cnrds_industrial_ai_patents_.*\.csv$", re.I),
    re.compile(r"^csmar_industrial_ai_patents_.*\.csv$", re.I),
    re.compile(r"^opendatalab_iids_industrial_ai_patents_.*\.csv$", re.I),
)

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


def is_fixture_basename(name: str) -> bool:
    base = Path(name).name.lower()
    if base in {b.lower() for b in FIXTURE_BASENAMES}:
        return True
    if "_fixture" in base.lower():
        return True
    return False


def is_excluded_evidence_path(path: Path) -> bool:
    rel = path.as_posix().lower()
    if "/fixtures/" in rel or rel.startswith("fixtures/"):
        return True
    if is_fixture_basename(path.name):
        return True
    if path.name.lower() == "patent_source_manifest.csv":
        return True
    return False


def is_real_export_filename(name: str) -> bool:
    return any(p.search(name) for p in REAL_EXPORT_PATTERNS)


def list_all_patent_csv_files(patents_dir: Path | None = None) -> list[Path]:
    patents_dir = patents_dir or RAW_PATENTS_DIR
    if not patents_dir.exists():
        return []
    paths: list[Path] = []
    for fp in sorted(patents_dir.rglob("*.csv")):
        if fp.name.startswith("."):
            continue
        paths.append(fp)
    return paths


def list_fixture_patent_csv_files(patents_dir: Path | None = None) -> list[Path]:
    return [p for p in list_all_patent_csv_files(patents_dir) if is_excluded_evidence_path(p)]


def list_evidence_patent_csv_files(patents_dir: Path | None = None) -> list[Path]:
    patents_dir = patents_dir or RAW_PATENTS_DIR
    evidence: list[Path] = []
    for p in list_all_patent_csv_files(patents_dir):
        if is_excluded_evidence_path(p):
            continue
        rel = p.relative_to(patents_dir)
        # Root-level real exports only (exclude ukn/, nested legacy dumps)
        if len(rel.parts) == 1 and is_real_export_filename(p.name):
            evidence.append(p)
    return evidence


def relative_source_file(path: Path, patents_dir: Path | None = None) -> str:
    patents_dir = patents_dir or RAW_PATENTS_DIR
    try:
        return path.relative_to(patents_dir).as_posix()
    except ValueError:
        return path.name
