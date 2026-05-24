from __future__ import annotations

import os
import shutil
from pathlib import Path

import pandas as pd

from diffusion_state.patent_raw_sources import (
    FIXTURES_DIR,
    RAW_PATENTS_DIR,
    list_evidence_patent_csv_files,
)
from diffusion_state.utils import PROJECT_ROOT, write_csv

FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "patents_cnipa_micro.csv"

PHASE1_COLUMNS = [
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

CNIPA_TO_PHASE1 = {
    "申请号": "patent_id",
    "申请年份": "application_year",
    "公开公告年份": "publication_year",
    "授权公告年份": "grant_year",
    "申请人": "applicant_name",
    "申请人城市": "applicant_city",
    "申请人省份": "applicant_province",
    "申请人地址": "applicant_address",
    "专利名称": "patent_title",
    "摘要文本": "abstract",
    "IPC分类号": "ipc_or_cpc",
    "专利类型": "patent_type",
}


def normalize_to_phase1_schema(df: pd.DataFrame) -> pd.DataFrame:
    if "patent_id" in df.columns:
        out = df.copy()
    else:
        out = pd.DataFrame()
        for src, dst in CNIPA_TO_PHASE1.items():
            if src in df.columns:
                out[dst] = df[src]
    out["claims_or_description"] = out.get("claims_or_description", out.get("abstract", ""))
    out["source"] = out.get("source", "cnipa_export")
    out["source_url_or_file"] = out.get("source_url_or_file", "")
    out["search_keyword"] = out.get("search_keyword", "")
    for col in PHASE1_COLUMNS:
        if col not in out.columns:
            out[col] = ""
    return out[PHASE1_COLUMNS]


def ensure_fixture_copies_for_tests(fixture_path: Path | None = None) -> None:
    """Stage quarantined fixture copies for unit tests only (not evidence ingest)."""
    if os.environ.get("ATLAS_USE_FIXTURE_PATENTS", "").lower() not in ("1", "true", "yes"):
        return
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    fixture_path = fixture_path or FIXTURE
    if not fixture_path.exists():
        return
    target = FIXTURES_DIR / "industrial_ai_patent_records.csv"
    df = pd.read_csv(fixture_path)
    write_csv(normalize_to_phase1_schema(df), target)
    shutil.copy2(fixture_path, FIXTURES_DIR / "cnipa_micro.csv")


def parse_industrial_ai_patents(
    raw_path: Path | None = None,
    cnipa_compat_path: Path | None = None,
) -> pd.DataFrame:
    """Validate evidence-path patent exports; fixtures stay under data/raw/patents/fixtures/."""
    ensure_fixture_copies_for_tests()
    evidence = list_evidence_patent_csv_files()
    if not evidence:
        return pd.DataFrame(columns=PHASE1_COLUMNS)

    frames = [normalize_to_phase1_schema(pd.read_csv(p, low_memory=False)) for p in evidence]
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=PHASE1_COLUMNS)
