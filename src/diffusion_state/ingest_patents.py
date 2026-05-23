from __future__ import annotations

from pathlib import Path

import pandas as pd

from diffusion_state.fetch_patents_cset import fetch_cset_patent_database
from diffusion_state.patent_city_normalize import normalize_city, normalize_province
from diffusion_state.patent_industry_map import map_patent_industry
from diffusion_state.patent_taxonomy import CATEGORY_COLUMNS, classify_patent_text
from diffusion_state.utils import PROJECT_ROOT, read_yaml, write_csv

TAXONOMY_PATH = PROJECT_ROOT / "configs" / "patent_taxonomy.yml"

LONG_COLUMNS = [
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
    "city",
    "province",
    "geocode_evidence",
    "industry_code",
    "industry_label",
    "industry_mapping_confidence",
    "industry_mapping_reason",
    "is_industrial_ai",
    "is_excluded_non_industrial",
    "classification_source",
    *CATEGORY_COLUMNS,
]

CNIPA_COLUMN_MAP = {
    "patent_id": ["申请号", "申请号.", "application_id", "patent_id"],
    "application_year": ["申请年份", "application_year"],
    "publication_year": ["公开公告年份", "publication_year"],
    "grant_year": ["授权公告年份", "grant_year"],
    "applicant_name": ["申请人", "applicant_name"],
    "applicant_city": ["申请人城市", "applicant_city", "city"],
    "applicant_province": ["申请人省份", "applicant_province", "province"],
    "applicant_address": ["申请人地址", "applicant_address", "address"],
    "patent_title": ["专利名称", "patent_title", "title", "Title"],
    "abstract": ["摘要文本", "abstract", "Abstract"],
    "claims_or_description": ["主权项内容", "claims_or_description"],
    "ipc_or_cpc": ["IPC分类号", "IPC主分类号", "ipc_or_cpc", "IPC"],
    "patent_type": ["专利类型", "patent_type", "Patent_Type"],
}

NORMALIZED_COLUMN_MAP = {col: [col] for col in LONG_COLUMNS if col not in CATEGORY_COLUMNS}


def _pick_column(df: pd.DataFrame, aliases: list[str]) -> str | None:
    cols = {c.strip(): c for c in df.columns}
    for alias in aliases:
        if alias in cols:
            return cols[alias]
        for c in df.columns:
            if str(c).strip() == alias:
                return c
    return None


def _rename_to_standard(df: pd.DataFrame, column_map: dict[str, list[str]]) -> pd.DataFrame:
    rename: dict[str, str] = {}
    for target, aliases in column_map.items():
        found = _pick_column(df, aliases)
        if found and found != target:
            rename[found] = target
    out = df.rename(columns=rename)
    for col in LONG_COLUMNS:
        if col not in out.columns and col not in CATEGORY_COLUMNS:
            out[col] = pd.NA
    return out


def _parse_year(value) -> int | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.isdigit() and len(text) == 4:
        return int(text)
    if len(text) >= 4 and text[:4].isdigit():
        return int(text[:4])
    return None


def _enrich_row(row: pd.Series, source: str, source_file: str) -> dict:
    cls = classify_patent_text(
        title=row.get("patent_title"),
        abstract=row.get("abstract"),
        claims_or_description=row.get("claims_or_description"),
        ipc_or_cpc=row.get("ipc_or_cpc"),
        cset_row=row.to_dict() if source == "cset_1790" else None,
    )
    ind_code, ind_label, ind_conf, ind_reason = map_patent_industry(
        title=row.get("patent_title"),
        abstract=row.get("abstract"),
        applicant_name=row.get("applicant_name"),
        ipc_or_cpc=row.get("ipc_or_cpc"),
    )
    city, province, geo = normalize_city(
        row.get("applicant_city"),
        row.get("applicant_province"),
        row.get("applicant_address"),
    )
    if not province:
        province = normalize_province(row.get("applicant_province"))

    year = _parse_year(row.get("application_year"))
    if year is None:
        year = _parse_year(row.get("publication_year"))

    record = {c: row.get(c) for c in LONG_COLUMNS if c not in CATEGORY_COLUMNS}
    record.update(
        {
            "application_year": year,
            "city": city,
            "province": province,
            "geocode_evidence": geo,
            "industry_code": ind_code,
            "industry_label": ind_label,
            "industry_mapping_confidence": ind_conf,
            "industry_mapping_reason": ind_reason,
            "is_industrial_ai": int(cls.is_industrial_ai),
            "is_excluded_non_industrial": int(cls.is_excluded_non_industrial),
            "classification_source": cls.classification_source,
            "source": source,
            "source_url_or_file": source_file,
        }
    )
    for cat, flag in cls.categories.items():
        record[cat] = int(flag)
    return record


def _enrich_dataframe(std: pd.DataFrame, source: str, source_file: str) -> pd.DataFrame:
    records = [_enrich_row(std.iloc[i], source, source_file) for i in range(len(std))]
    return pd.DataFrame(records)


def ingest_cnipa_files(patents_dir: Path) -> pd.DataFrame:
    patterns = ["cnipa_*.csv", "cnipa_*.csv.gz", "patents_normalized*.csv"]
    paths: list[Path] = []
    for pat in patterns:
        paths.extend(patents_dir.glob(pat))
    paths = sorted({p for p in paths if p.is_file()})
    if not paths:
        return pd.DataFrame(columns=LONG_COLUMNS)

    frames: list[pd.DataFrame] = []
    for path in paths:
        compression = "gzip" if path.suffix == ".gz" else None
        raw = pd.read_csv(path, compression=compression, low_memory=False)
        std = _rename_to_standard(raw, CNIPA_COLUMN_MAP)
        frames.append(_enrich_dataframe(std, "cnipa", str(path)))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=LONG_COLUMNS)


def ingest_normalized_files(patents_dir: Path) -> pd.DataFrame:
    paths = sorted(patents_dir.glob("patents_normalized*.csv"))
    if not paths:
        return pd.DataFrame(columns=LONG_COLUMNS)
    frames = []
    for path in paths:
        raw = pd.read_csv(path, low_memory=False)
        std = _rename_to_standard(raw, NORMALIZED_COLUMN_MAP)
        frames.append(_enrich_dataframe(std, "normalized", str(path)))
    return pd.concat(frames, ignore_index=True)


def ingest_cset_china(patents_dir: Path) -> pd.DataFrame:
    """CSET rows are taxonomy validation only (no applicant city)."""
    csv_path = patents_dir / "patent_database.csv"
    if not csv_path.exists():
        try:
            fetch_cset_patent_database(patents_dir)
        except Exception:
            return pd.DataFrame(columns=LONG_COLUMNS)

    usecols = [
        "Publication_country",
        "Publication_number",
        "Patent_Type",
        "Priority_Year",
        "Industrial_and_Manufacturing",
        "Robotics",
        "Computer_Vision",
        "Control",
        "Planning_and_Scheduling",
        "Measuring_and_Testing",
        "Semiconductors",
    ]
    raw = pd.read_csv(csv_path, usecols=usecols, low_memory=False)
    cn = raw[raw["Publication_country"] == "CN"].copy()
    if cn.empty:
        return pd.DataFrame(columns=LONG_COLUMNS)

    cn["patent_id"] = cn["Publication_number"].astype(str)
    cn["application_year"] = cn["Priority_Year"]
    cn["patent_type"] = cn["Patent_Type"]
    cn["patent_title"] = ""
    cn["abstract"] = ""
    cn["ipc_or_cpc"] = ""
    cn["source"] = "cset_1790"
    cn["source_url_or_file"] = str(csv_path)

    cfg = read_yaml(TAXONOMY_PATH)
    cat_df = pd.DataFrame(0, index=cn.index, columns=CATEGORY_COLUMNS)
    for field, cat in cfg.get("cset_field_map", {}).items():
        if field in cn.columns and cat in cat_df.columns:
            cat_df[cat] = cn[field].fillna(False).astype(bool).astype(int)
    cn = pd.concat([cn, cat_df], axis=1)
    cn["is_industrial_ai"] = (cat_df.sum(axis=1) > 0).astype(int)
    cn["is_excluded_non_industrial"] = 0
    cn["classification_source"] = "cset_fields"
    cn["industry_code"] = "C34"
    cn["industry_label"] = "general_equipment"
    cn["industry_mapping_confidence"] = "low"
    cn["industry_mapping_reason"] = "cset_no_ipc_or_text"
    cn["city"] = ""
    cn["province"] = ""
    cn["geocode_evidence"] = "missing"

    keep = [c for c in LONG_COLUMNS if c in cn.columns]
    return cn[keep]


def ingest_all_patents(
    patents_dir: Path | None = None,
    include_cset_validation: bool = False,
) -> pd.DataFrame:
    patents_dir = patents_dir or PROJECT_ROOT / "data" / "raw" / "patents"
    parts = [
        ingest_cnipa_files(patents_dir),
        ingest_normalized_files(patents_dir),
    ]
    if include_cset_validation:
        parts.append(ingest_cset_china(patents_dir))

    frames = [p for p in parts if len(p)]
    if not frames:
        return pd.DataFrame(columns=LONG_COLUMNS)
    long_df = pd.concat(frames, ignore_index=True)
    long_df = long_df.drop_duplicates(subset=["patent_id", "source"], keep="first")
    return long_df


def write_patents_long(
    long_df: pd.DataFrame,
    out_path: Path | None = None,
) -> pd.DataFrame:
    out_path = out_path or PROJECT_ROOT / "data" / "interim" / "industrial_ai_patents_long.csv"
    write_csv(long_df, out_path)
    return long_df
