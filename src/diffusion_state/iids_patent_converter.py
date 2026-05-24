"""Convert IIDS SQL dumps to Atlas Phase-1 patent CSV exports."""
from __future__ import annotations

import csv
import json
import re
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from diffusion_state.iids_sql_parser import stream_table_inserts
from diffusion_state.parse_industrial_ai_patents import PHASE1_COLUMNS
from diffusion_state.iids_paths import (
    DEFAULT_IIDS_OUTPUT,
    DEFAULT_IIDS_SOURCES_DIR,
    resolve_iids_sources_dir,
)
from diffusion_state.utils import PROJECT_ROOT, read_yaml

IIDS_SOURCES_DIR = DEFAULT_IIDS_SOURCES_DIR
DEFAULT_OUTPUT = DEFAULT_IIDS_OUTPUT

DETAIL_TABLE = "base_patent_detail"
LAW_TABLE = "base_patent_law_status"

DOCUMENTED_DETAIL_COLUMNS = (
    "pn",
    "title",
    "abs",
    "pr",
    "ap_or",
    "in_or",
    "ipc",
    "cpc",
    "pn_date",
    "ad",
    "family_number",
    "year",
)

DOCUMENTED_LAW_COLUMNS = (
    "pn",
    "event_date",
    "authorize",
    "reject",
    "event_code",
    "code_expl",
    "transfer",
    "invalid",
)

INDUSTRIAL_AI_IPC_PREFIXES = (
    "G06N",
    "G06T",
    "G06V",
    "G06Q",
    "G05B",
    "G05D",
    "H04L",
    "B25J",
    "G01N",
    "G01R",
    "H01L",
    "H01M",
    "C08L",
)

CN_PUBLICATION_RE = re.compile(r"^CN\d+[A-Z]\d*$", re.I)


@dataclass
class IidsConvertConfig:
    detail_sql: Path
    law_status_sql: Path | None = None
    output_csv: Path = DEFAULT_OUTPUT
    year_min: int = 2015
    year_max: int = 2024
    jurisdiction_cn_only: bool = True
    require_industrial_ai: bool = True
    max_rows: int | None = None
    search_keyword: str = "industrial_ai_taxonomy"
    source: str = "opendatalab_iids"
    source_url_or_file: str = "Gracie/IIDS"


@dataclass
class IidsConvertStats:
    scanned_rows: int = 0
    year_filtered: int = 0
    jurisdiction_filtered: int = 0
    ai_filtered: int = 0
    written_rows: int = 0


def _load_taxonomy_keywords() -> list[str]:
    path = PROJECT_ROOT / "configs" / "patent_taxonomy.yml"
    if not path.exists():
        return []
    cfg = read_yaml(path)
    keywords: list[str] = []
    for entry in cfg.get("categories", {}).values():
        keywords.extend(entry.get("keywords", []))
    keywords.extend(cfg.get("non_industrial_exclusions", {}).get("keywords", []))
    return keywords


def _parse_json_field(value: object) -> object:
    if value is None:
        return None
    if isinstance(value, (list, dict)):
        return value
    text = str(value).strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def _json_list_to_text(value: object) -> str:
    parsed = _parse_json_field(value)
    if parsed is None:
        return ""
    if isinstance(parsed, list):
        return "; ".join(str(x).strip() for x in parsed if str(x).strip())
    return str(parsed).strip()


def _year_from_json_dates(value: object) -> int | None:
    parsed = _parse_json_field(value)
    candidates: list[str] = []
    if isinstance(parsed, list):
        candidates = [str(x) for x in parsed]
    elif parsed is not None:
        candidates = [str(parsed)]
    for item in candidates:
        m = re.search(r"(20\d{2})", item)
        if m:
            return int(m.group(1))
    return None


def _year_from_event_date(value: object) -> int | None:
    text = str(value or "").strip()
    if len(text) >= 4 and text[:4].isdigit():
        return int(text[:4])
    return None


def _combine_ipc_cpc(ipc: object, cpc: object) -> str:
    parts = [_json_list_to_text(ipc), _json_list_to_text(cpc)]
    return " | ".join(p for p in parts if p)


def _is_cn_publication(pn: str) -> bool:
    return bool(CN_PUBLICATION_RE.match(pn.strip()))


def _matches_industrial_ai(row: dict[str, object], keywords: list[str]) -> bool:
    ipc_cpc = _combine_ipc_cpc(row.get("ipc"), row.get("cpc")).upper()
    if any(prefix in ipc_cpc for prefix in INDUSTRIAL_AI_IPC_PREFIXES):
        return True
    text = " ".join(
        str(row.get(k) or "")
        for k in ("title", "abs", "ap_or", "in_or")
    )
    if not text.strip():
        return False
    return any(kw in text for kw in keywords)


def build_grant_year_index(law_status_sql: Path) -> dict[str, int]:
    """Map publication number -> grant year from authorize=1 law-status events."""
    table_columns = {LAW_TABLE: list(DOCUMENTED_LAW_COLUMNS)}
    grant_years: dict[str, int] = {}
    for row in stream_table_inserts(law_status_sql, LAW_TABLE, table_columns=table_columns):
        pn = str(row.get("pn") or "").strip()
        if not pn:
            continue
        try:
            authorized = int(row.get("authorize") or 0)
        except (TypeError, ValueError):
            authorized = 0
        if authorized != 1:
            continue
        year = _year_from_event_date(row.get("event_date"))
        if year is None:
            continue
        prev = grant_years.get(pn)
        if prev is None or year > prev:
            grant_years[pn] = year
    return grant_years


def iids_row_to_phase1(
    row: dict[str, object],
    *,
    grant_years: dict[str, int],
    config: IidsConvertConfig,
) -> dict[str, str]:
    pn = str(row.get("pn") or "").strip()
    application_year = row.get("year")
    try:
        app_year = int(application_year) if application_year not in (None, "") else None
    except (TypeError, ValueError):
        app_year = None
    pub_year = _year_from_json_dates(row.get("pn_date"))
    grant_year = grant_years.get(pn)
    return {
        "patent_id": pn,
        "application_year": str(app_year or ""),
        "publication_year": str(pub_year or ""),
        "grant_year": str(grant_year or ""),
        "applicant_name": _json_list_to_text(row.get("ap_or")),
        "applicant_city": "",
        "applicant_province": "",
        "applicant_address": "",
        "patent_title": str(row.get("title") or "").strip(),
        "abstract": str(row.get("abs") or "").strip(),
        "claims_or_description": str(row.get("abs") or "").strip(),
        "ipc_or_cpc": _combine_ipc_cpc(row.get("ipc"), row.get("cpc")),
        "patent_type": "",
        "source": config.source,
        "source_url_or_file": config.source_url_or_file,
        "search_keyword": config.search_keyword,
    }


def iter_iids_phase1_rows(
    config: IidsConvertConfig,
    *,
    grant_years: dict[str, int] | None = None,
    keywords: list[str] | None = None,
) -> Iterator[tuple[dict[str, str], IidsConvertStats]]:
    keywords = keywords if keywords is not None else _load_taxonomy_keywords()
    stats = IidsConvertStats()
    table_columns = {DETAIL_TABLE: list(DOCUMENTED_DETAIL_COLUMNS)}
    for row in stream_table_inserts(config.detail_sql, DETAIL_TABLE, table_columns=table_columns):
        stats.scanned_rows += 1
        pn = str(row.get("pn") or "").strip()
        if not pn:
            continue
        if config.jurisdiction_cn_only and not _is_cn_publication(pn):
            stats.jurisdiction_filtered += 1
            continue
        try:
            year = int(row.get("year"))
        except (TypeError, ValueError):
            stats.year_filtered += 1
            continue
        if year < config.year_min or year > config.year_max:
            stats.year_filtered += 1
            continue
        if config.require_industrial_ai and not _matches_industrial_ai(row, keywords):
            stats.ai_filtered += 1
            continue
        phase1 = iids_row_to_phase1(row, grant_years=grant_years or {}, config=config)
        stats.written_rows += 1
        yield phase1, stats
        if config.max_rows is not None and stats.written_rows >= config.max_rows:
            break


def convert_iids_sql_to_csv(config: IidsConvertConfig) -> IidsConvertStats:
    grant_years: dict[str, int] = {}
    if config.law_status_sql and config.law_status_sql.exists():
        grant_years = build_grant_year_index(config.law_status_sql)

    config.output_csv.parent.mkdir(parents=True, exist_ok=True)
    final_stats = IidsConvertStats()
    with config.output_csv.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=PHASE1_COLUMNS)
        writer.writeheader()
        for row, stats in iter_iids_phase1_rows(config, grant_years=grant_years):
            writer.writerow(row)
            final_stats = stats
    return final_stats


def find_iids_sql_paths(sources_dir: Path | None = None) -> tuple[Path | None, Path | None]:
    sources_dir = sources_dir or resolve_iids_sources_dir()
    if not sources_dir.exists():
        return None, None
    detail = next(iter(sources_dir.rglob("base_patent_detail.sql")), None)
    law = next(iter(sources_dir.rglob("base_patent_law_status.sql")), None)
    return detail, law
