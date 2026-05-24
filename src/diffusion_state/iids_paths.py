"""Resolve IIDS source/output paths for download and conversion."""
from __future__ import annotations

import os
import shutil
from pathlib import Path

from diffusion_state.utils import PROJECT_ROOT

DEFAULT_IIDS_SOURCES_DIR = PROJECT_ROOT / "data" / "raw" / "patents" / "opendatalab_iids_sources"
DEFAULT_IIDS_OUTPUT = PROJECT_ROOT / "data" / "raw" / "patents" / "opendatalab_iids_industrial_ai_patents_2015_2024_part1.csv"
DEFAULT_GEO_OUTPUT = PROJECT_ROOT / "data" / "raw" / "patents" / "cnipa_patent_geography_2015_2024.csv"
PATENT_KEYS_FOR_GEO_OUTPUT = PROJECT_ROOT / "outputs" / "tables" / "table_P9_iids_patent_keys_for_geography.csv"
SMOKE_IIDS_DIR = PROJECT_ROOT / "outputs" / "smoke" / "iids"

MIN_SQL_DOWNLOAD_GB = 150

# Do not use WSL home or the repo laptop C: partition for ~136 GB SQL.
FORBIDDEN_TARGET_MARKERS = (
    "/home/",
    "~/",
    "\\wsl$\\",
    "/mnt/c/users/",
)


def validate_production_target_dir(target: Path) -> list[str]:
    """Return human-readable blockers for unsafe IIDS download targets."""
    issues: list[str] = []
    normalized = target.as_posix().lower()
    if "\\" in str(target):
        win = str(target).lower()
        if "\\wsl$\\" in win or "\\wsl.localhost\\" in win:
            issues.append(
                "Do not download into WSL paths. Use an external drive such as D:\\iids_sources or E:\\iids_sources."
            )
    for marker in FORBIDDEN_TARGET_MARKERS:
        if marker in normalized or marker.replace("/", "\\") in str(target).lower():
            issues.append(
                "Do not download to WSL home (/home/mateo/iids_sources). "
                "Use D:\\iids_sources, E:\\iids_sources, or a cloud VM with >= 300 GB disk."
            )
            break
    try:
        free = shutil.disk_usage(target if target.exists() else target.parent).free / (1024**3)
    except OSError:
        free = 0.0
    if free < MIN_SQL_DOWNLOAD_GB:
        issues.append(
            f"Only {free:.1f} GB free at {target}; need >= {MIN_SQL_DOWNLOAD_GB} GB for base_patent_detail.sql. "
            "Attach external SSD (D: or E:) or use a cloud VM."
        )
    repo_drive = PROJECT_ROOT.drive.lower()
    target_drive = target.drive.lower()
    if repo_drive and target_drive == repo_drive and free < MIN_SQL_DOWNLOAD_GB:
        issues.append(
            "Do not run the SQL download on the repo laptop Windows partition (~38 GB). "
            "Set OPENXLAB_IIDS_SOURCES_DIR to external storage."
        )
    return issues

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
