"""Resolve IIDS source/output paths for download and conversion."""
from __future__ import annotations

import os
from pathlib import Path

from diffusion_state.utils import PROJECT_ROOT

DEFAULT_IIDS_SOURCES_DIR = PROJECT_ROOT / "data" / "raw" / "patents" / "opendatalab_iids_sources"
DEFAULT_IIDS_OUTPUT = PROJECT_ROOT / "data" / "raw" / "patents" / "opendatalab_iids_industrial_ai_patents_2015_2024_part1.csv"
DEFAULT_GEO_OUTPUT = PROJECT_ROOT / "data" / "raw" / "patents" / "cnipa_patent_geography_2015_2024.csv"
SMOKE_IIDS_DIR = PROJECT_ROOT / "outputs" / "smoke" / "iids"

MIN_SQL_DOWNLOAD_GB = 150


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
