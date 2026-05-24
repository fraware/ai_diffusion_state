"""Resolve IIDS source/output paths for download and conversion."""
from __future__ import annotations

import os
from pathlib import Path

from diffusion_state.utils import PROJECT_ROOT

DEFAULT_IIDS_SOURCES_DIR = PROJECT_ROOT / "data" / "raw" / "patents" / "opendatalab_iids_sources"
DEFAULT_IIDS_OUTPUT = PROJECT_ROOT / "data" / "raw" / "patents" / "opendatalab_iids_industrial_ai_patents_2015_2024_part1.csv"
DEFAULT_GEO_OUTPUT = PROJECT_ROOT / "data" / "raw" / "patents" / "cnipa_patent_geography_2015_2024.csv"
PATENT_KEYS_FOR_GEO_OUTPUT = PROJECT_ROOT / "outputs" / "tables" / "table_P9_iids_patent_keys_for_geography.csv"
SMOKE_IIDS_DIR = PROJECT_ROOT / "outputs" / "smoke" / "iids"

MIN_SQL_DOWNLOAD_GB = 150

IIDS_DATASET_REPO = "Gracie/IIDS"

IIDS_DOC_FILES = (
    "/README.md",
    "/metafile.yaml",
    "/Intelligent Innovation Dataset Technical Document.docx",
    "/智创数据库技术文档.docx",
)

IIDS_SQL_FILES = (
    "/base_patent_detail.sql",
    "/base_patent_law_status.sql",
)

IIDS_DETAIL_SQL_FILES = ("/base_patent_detail.sql",)

# Not required for Atlas patent layer:
# entity_fund_info.sql, entity_funds_re.zip, entity_paper.sql, reference_citation_re.sql


def resolve_iids_sources_dir() -> Path:
    override = os.environ.get("OPENXLAB_IIDS_SOURCES_DIR", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return DEFAULT_IIDS_SOURCES_DIR


def resolve_iids_output_csv(*, production: bool = True, smoke: bool = False) -> Path:
    if smoke and not production:
        return SMOKE_IIDS_DIR / DEFAULT_IIDS_OUTPUT.name
    override = os.environ.get("OPENXLAB_IIDS_OUTPUT_CSV", "").strip()
    if override and production:
        return Path(override).expanduser().resolve()
    return DEFAULT_IIDS_OUTPUT


def resolve_iids_download_targets(
    *,
    include_sql: bool = False,
    sql_only: bool = False,
    detail_only: bool = False,
) -> list[str]:
    if detail_only:
        return list(IIDS_DETAIL_SQL_FILES)
    if sql_only:
        return list(IIDS_SQL_FILES)
    if include_sql:
        return list(IIDS_DOC_FILES) + list(IIDS_SQL_FILES)
    return list(IIDS_DOC_FILES)


def build_iids_download_argv(
    sources_dir: Path,
    *,
    python: str,
    docs_only: bool = False,
    include_law_status: bool = False,
) -> list[str]:
    cmd = [python, "scripts/59_download_iids_patent_sources.py", "--target-dir", str(sources_dir)]
    if docs_only:
        return cmd
    if include_law_status:
        cmd.append("--include-sql")
    else:
        cmd.append("--detail-only")
    return cmd
