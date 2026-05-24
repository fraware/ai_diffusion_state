"""Join applicant geography onto IIDS-derived patent exports."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from diffusion_state.parse_industrial_ai_patents import PHASE1_COLUMNS, normalize_to_phase1_schema
from diffusion_state.patent_raw_sources import RAW_PATENTS_DIR
from diffusion_state.utils import PROJECT_ROOT

GEO_PATTERNS = (
    "cnipa_patent_geography_*.csv",
    "cnipa_industrial_ai_patent_geography_*.csv",
    "lens_patent_geography_*.csv",
)

GEO_KEY_COLUMNS = (
    "patent_id",
    "publication_number",
    "publication_no",
    "pn",
    "公开号",
    "公开(公告)号",
)

GEO_CITY_COLUMNS = ("applicant_city", "city", "申请人城市")
GEO_PROVINCE_COLUMNS = ("applicant_province", "province", "申请人省份")
GEO_ADDRESS_COLUMNS = ("applicant_address", "address", "申请人地址")


def _pick_column(df: pd.DataFrame, aliases: tuple[str, ...]) -> str | None:
    lower_map = {str(c).strip().lower(): c for c in df.columns}
    for alias in aliases:
        if alias.lower() in lower_map:
            return str(lower_map[alias.lower()])
    return None


def discover_geography_supplement(patents_dir: Path | None = None) -> Path | None:
    patents_dir = patents_dir or RAW_PATENTS_DIR
    for pattern in GEO_PATTERNS:
        matches = sorted(patents_dir.glob(pattern))
        if matches:
            return matches[0]
    return None


def load_geography_lookup(path: Path) -> pd.DataFrame:
    geo = pd.read_csv(path, low_memory=False, encoding="utf-8-sig")
    key_col = _pick_column(geo, GEO_KEY_COLUMNS)
    if key_col is None:
        raise ValueError(f"Geography supplement missing join key column: {path.name}")
    city_col = _pick_column(geo, GEO_CITY_COLUMNS)
    province_col = _pick_column(geo, GEO_PROVINCE_COLUMNS)
    address_col = _pick_column(geo, GEO_ADDRESS_COLUMNS)
    out = pd.DataFrame(
        {
            "patent_id": geo[key_col].astype(str).str.strip(),
            "applicant_city": geo[city_col].astype(str) if city_col else "",
            "applicant_province": geo[province_col].astype(str) if province_col else "",
            "applicant_address": geo[address_col].astype(str) if address_col else "",
        }
    )
    out = out.drop_duplicates(subset=["patent_id"], keep="first")
    return out


def join_patent_geography(
    iids_csv: Path,
    geo_csv: Path,
    output_csv: Path | None = None,
) -> tuple[pd.DataFrame, dict[str, int]]:
    output_csv = output_csv or iids_csv
    patents = normalize_to_phase1_schema(pd.read_csv(iids_csv, low_memory=False, encoding="utf-8-sig"))
    lookup = load_geography_lookup(geo_csv)
    merged = patents.merge(lookup, on="patent_id", how="left", suffixes=("", "_geo"))
    for col in ("applicant_city", "applicant_province", "applicant_address"):
        geo_col = f"{col}_geo"
        if geo_col in merged.columns:
            base = merged[col].astype(str).replace({"nan": "", "None": ""})
            add = merged[geo_col].astype(str).replace({"nan": "", "None": ""})
            merged[col] = base.where(base.str.len() > 0, add)
            merged = merged.drop(columns=[geo_col])
    merged = merged[PHASE1_COLUMNS]
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(output_csv, index=False, encoding="utf-8-sig")
    n_total = len(merged)
    n_city = int(merged["applicant_city"].astype(str).str.len().gt(0).sum())
    n_province = int(merged["applicant_province"].astype(str).str.len().gt(0).sum())
    return merged, {
        "rows": n_total,
        "rows_with_city": n_city,
        "rows_with_province": n_province,
        "city_fill_rate": round(n_city / n_total, 4) if n_total else 0.0,
    }
