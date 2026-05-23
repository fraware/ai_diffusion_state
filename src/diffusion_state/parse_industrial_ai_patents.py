from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd

from diffusion_state.utils import PROJECT_ROOT, write_csv

RAW_RECORDS = PROJECT_ROOT / "data" / "raw" / "patents" / "industrial_ai_patent_records.csv"
CNIPA_MICRO = PROJECT_ROOT / "data" / "raw" / "patents" / "cnipa_micro.csv"
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
    out["source"] = out.get("source", "cnipa_micro_export")
    out["source_url_or_file"] = out.get(
        "source_url_or_file", "data/raw/patents/industrial_ai_patent_records.csv"
    )
    out["search_keyword"] = out.get("search_keyword", "industrial_ai_phase1")
    for col in PHASE1_COLUMNS:
        if col not in out.columns:
            out[col] = ""
    return out[PHASE1_COLUMNS]


def ensure_industrial_ai_patent_records(
    raw_path: Path | None = None,
    fixture_path: Path | None = None,
) -> Path:
    raw_path = raw_path or RAW_RECORDS
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    if raw_path.exists():
        return raw_path

    fixture_path = fixture_path or FIXTURE
    if not fixture_path.exists():
        raise FileNotFoundError(
            f"No patent microdata at {raw_path}. Place CNIPA export or provide {fixture_path}."
        )
    df = pd.read_csv(fixture_path)
    write_csv(normalize_to_phase1_schema(df), raw_path)
    return raw_path


def parse_industrial_ai_patents(
    raw_path: Path | None = None,
    cnipa_compat_path: Path | None = None,
) -> pd.DataFrame:
    """Ensure canonical Phase 1 raw file and CNIPA ingest copy exist."""
    raw_path = ensure_industrial_ai_patent_records(raw_path)
    df = pd.read_csv(raw_path)
    if "patent_title" not in df.columns:
        df = normalize_to_phase1_schema(df)
        write_csv(df, raw_path)

    cnipa_compat_path = cnipa_compat_path or CNIPA_MICRO
    cnipa_compat_path.parent.mkdir(parents=True, exist_ok=True)
    fixture_path = FIXTURE
    if fixture_path.exists():
        shutil.copy2(fixture_path, cnipa_compat_path)
    elif not cnipa_compat_path.exists():
        shutil.copy2(raw_path, cnipa_compat_path)

    return df
