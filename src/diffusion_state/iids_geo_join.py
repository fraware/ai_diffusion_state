"""Validate and join applicant geography onto IIDS-derived patent exports."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from diffusion_state.parse_industrial_ai_patents import PHASE1_COLUMNS, normalize_to_phase1_schema
from diffusion_state.patent_raw_sources import RAW_PATENTS_DIR

GEO_PATTERNS = (
    "cnipa_patent_geography_*.csv",
    "cnipa_industrial_ai_patent_geography_*.csv",
    "lens_patent_geography_*.csv",
)

GEO_TEMPLATE_MARKERS = ("template", "example_only", "schema_guide")

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

MIN_CITY_FILL = 0.80
STRONG_CITY_FILL = 0.90
MIN_PROVINCE_FILL = 0.80
MIN_ROWS = 500
STRONG_ROWS = 5000
MIN_CITIES = 50
STRONG_CITIES = 100
MIN_INDUSTRIES = 10
STRONG_INDUSTRIES = 20
IIDS_PRODUCTION_MIN_KEYS = 4_000_000
KEY_COVERAGE_MIN_RATE = 0.95


@dataclass(frozen=True)
class GeographyThresholds:
    city_fill: float
    rows: int
    cities: int
    industries: int | None = None


MINIMUM_ACCEPTANCE = GeographyThresholds(
    city_fill=MIN_CITY_FILL,
    rows=MIN_ROWS,
    cities=MIN_CITIES,
    industries=MIN_INDUSTRIES,
)
STRONG_ACCEPTANCE = GeographyThresholds(
    city_fill=STRONG_CITY_FILL,
    rows=STRONG_ROWS,
    cities=STRONG_CITIES,
    industries=STRONG_INDUSTRIES,
)


def _pick_column(df: pd.DataFrame, aliases: tuple[str, ...]) -> str | None:
    lower_map = {str(c).strip().lower(): c for c in df.columns}
    for alias in aliases:
        if alias.lower() in lower_map:
            return str(lower_map[alias.lower()])
    return None


def is_geography_template_path(path: Path) -> bool:
    name = path.name.lower()
    return any(marker in name for marker in GEO_TEMPLATE_MARKERS)


def _non_empty(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().replace({"nan": "", "None": "", "TEMPLATE_DO_NOT_USE": ""}).str.len().gt(0)


def _non_empty_str(value: object) -> str:
    text = str(value or "").strip()
    if text.lower() in {"", "nan", "none", "template_do_not_use"}:
        return ""
    return text


def _pick_row_column(row: dict[str, str], aliases: tuple[str, ...]) -> str | None:
    lower = {str(k).strip().lower(): k for k in row}
    for alias in aliases:
        key = lower.get(alias.lower())
        if key is not None:
            return str(key)
    return None


def _join_keys_from_row(row: dict[str, str]) -> str:
    pub_key = _pick_row_column(
        row,
        ("publication_number", "publication_no", "pn", "公开号", "公开(公告)号", "公开公告号"),
    )
    pid_key = _pick_row_column(row, ("patent_id", "申请号"))
    pub = _non_empty_str(row.get(pub_key, "")) if pub_key else ""
    pid = _non_empty_str(row.get(pid_key, "")) if pid_key else ""
    return pub or pid


def summarize_geography_from_counts(
    *,
    n_keys: int,
    n_matched: int,
    n_city: int,
    n_province: int,
    n_unique_cities: int,
) -> dict[str, float | int]:
    denom = n_keys or 1
    return {
        "rows": n_keys,
        "rows_with_city": n_city,
        "rows_with_province": n_province,
        "unique_cities": n_unique_cities,
        "city_fill_rate": round(n_city / denom, 4),
        "province_fill_rate": round(n_province / denom, 4),
        "key_match_rate": round(n_matched / denom, 4),
        "n_keys": n_keys,
        "n_matched": n_matched,
    }


def discover_geography_supplement(patents_dir: Path | None = None) -> Path | None:
    patents_dir = patents_dir or RAW_PATENTS_DIR
    for pattern in GEO_PATTERNS:
        matches = sorted(p for p in patents_dir.glob(pattern) if not is_geography_template_path(p))
        if matches:
            return matches[0]
    return None


def _join_keys(geo: pd.DataFrame) -> pd.Series:
    pub_col = _pick_column(
        geo,
        ("publication_number", "publication_no", "pn", "公开号", "公开(公告)号"),
    )
    pid_col = _pick_column(geo, ("patent_id", "申请号"))
    if pub_col and pid_col:
        pub = geo[pub_col].astype(str).str.strip()
        pid = geo[pid_col].astype(str).str.strip()
        return pub.where(_non_empty(pub), pid)
    if pub_col:
        return geo[pub_col].astype(str).str.strip()
    if pid_col:
        return geo[pid_col].astype(str).str.strip()
    raise ValueError("Geography supplement missing join key column")


def load_geography_lookup(path: Path) -> pd.DataFrame:
    geo = pd.read_csv(path, low_memory=False, encoding="utf-8-sig")
    for notes_col in ("geo_notes", "notes"):
        if notes_col in geo.columns:
            notes = geo[notes_col].astype(str).str.upper()
            geo = geo[
                ~notes.str.contains("TEMPLATE", na=False) & ~notes.str.contains("DO NOT USE", na=False)
            ]
    join_key = _join_keys(geo)
    city_col = _pick_column(geo, GEO_CITY_COLUMNS)
    province_col = _pick_column(geo, GEO_PROVINCE_COLUMNS)
    address_col = _pick_column(geo, GEO_ADDRESS_COLUMNS)
    out = pd.DataFrame(
        {
            "patent_id": join_key,
            "applicant_city": geo[city_col].astype(str) if city_col else "",
            "applicant_province": geo[province_col].astype(str) if province_col else "",
            "applicant_address": geo[address_col].astype(str) if address_col else "",
        }
    )
    out = out[out["patent_id"].astype(str).str.len().gt(0)]
    out = out.drop_duplicates(subset=["patent_id"], keep="first")
    return out


def summarize_geography(df: pd.DataFrame) -> dict[str, float | int]:
    n_total = len(df)
    city = df.get("applicant_city", pd.Series(dtype=str))
    province = df.get("applicant_province", pd.Series(dtype=str))
    n_city = int(_non_empty(city).sum()) if n_total else 0
    n_province = int(_non_empty(province).sum()) if n_total else 0
    n_cities = int(city.astype(str).str.strip().replace({"nan": "", "None": ""}).nunique()) if n_total else 0
    stats = summarize_geography_from_counts(
        n_keys=n_total,
        n_matched=n_total,
        n_city=n_city,
        n_province=n_province,
        n_unique_cities=n_cities,
    )
    return stats


def evaluate_geography_acceptance(
    stats: dict[str, float | int],
    *,
    thresholds: GeographyThresholds = MINIMUM_ACCEPTANCE,
    label: str = "minimum",
    min_province_fill: float | None = MIN_PROVINCE_FILL,
    min_key_match_rate: float | None = None,
) -> tuple[bool, list[str]]:
    issues: list[str] = []
    city_fill = float(stats.get("city_fill_rate", 0.0))
    province_fill = float(stats.get("province_fill_rate", 0.0))
    key_match = float(stats.get("key_match_rate", 1.0))
    rows = int(stats.get("rows", 0))
    cities = int(stats.get("unique_cities", 0))
    industries = stats.get("unique_industries")

    if city_fill < thresholds.city_fill:
        issues.append(f"{label}: city fill {city_fill:.1%} below {thresholds.city_fill:.0%}")
    if min_province_fill is not None and province_fill < min_province_fill:
        issues.append(
            f"{label}: province fill {province_fill:.1%} below {min_province_fill:.0%}"
        )
    if min_key_match_rate is not None and key_match < min_key_match_rate:
        issues.append(f"{label}: key match rate {key_match:.1%} below {min_key_match_rate:.0%}")
    if rows < thresholds.rows:
        issues.append(f"{label}: rows {rows} below {thresholds.rows}")
    if cities < thresholds.cities:
        issues.append(f"{label}: unique cities {cities} below {thresholds.cities}")
    if thresholds.industries is not None and industries is not None:
        if int(industries) < thresholds.industries:
            issues.append(f"{label}: unique industries {industries} below {thresholds.industries}")
    return len(issues) == 0, issues


def production_key_coverage_thresholds(expected_keys: int) -> GeographyThresholds:
    """Acceptance thresholds for full IIDS key-list joins."""
    min_rows = max(MIN_ROWS, int(expected_keys * KEY_COVERAGE_MIN_RATE))
    return GeographyThresholds(
        city_fill=MIN_CITY_FILL,
        rows=min_rows,
        cities=MIN_CITIES,
        industries=MIN_INDUSTRIES,
    )


def validate_geography_supplement(path: Path) -> tuple[dict[str, float | int], list[str]]:
    lookup = load_geography_lookup(path)
    stats = summarize_geography(lookup)
    ok_min, issues = evaluate_geography_acceptance(stats, thresholds=MINIMUM_ACCEPTANCE, label="minimum")
    ok_strong, strong_issues = evaluate_geography_acceptance(stats, thresholds=STRONG_ACCEPTANCE, label="strong")
    if ok_strong:
        issues.append("strong geography acceptance: passed")
    elif ok_min:
        issues.extend(strong_issues)
    return stats, issues


def join_patent_geography(
    iids_csv: Path,
    geo_csv: Path,
    output_csv: Path | None = None,
) -> tuple[pd.DataFrame | None, dict[str, float | int]]:
    from diffusion_state.iids_geo_stream import join_patent_geography_streaming, should_stream_patent_csv

    output_csv = output_csv or iids_csv
    if should_stream_patent_csv(iids_csv):
        stats = join_patent_geography_streaming(iids_csv, geo_csv, output_csv)
        return None, stats

    patents = normalize_to_phase1_schema(pd.read_csv(iids_csv, low_memory=False, encoding="utf-8-sig"))
    lookup = load_geography_lookup(geo_csv)
    merged = patents.merge(lookup, on="patent_id", how="left", suffixes=("", "_geo"))
    for col in ("applicant_city", "applicant_province", "applicant_address"):
        geo_col = f"{col}_geo"
        if geo_col in merged.columns:
            base = merged[col].astype(str).replace({"nan": "", "None": ""})
            add = merged[geo_col].astype(str).replace({"nan": "", "None": ""})
            merged[col] = base.where(_non_empty(base), add)
            merged = merged.drop(columns=[geo_col])
    merged = merged[PHASE1_COLUMNS]
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(output_csv, index=False, encoding="utf-8-sig")
    stats = summarize_geography(merged)
    return merged, stats


GEO_OUTPUT_COLUMNS = [
    "patent_id",
    "applicant_city",
    "applicant_province",
    "applicant_address",
    "geo_source",
    "geo_match_confidence",
    "geo_notes",
]

GEO_OUTPUT_COLUMNS_LEGACY = GEO_OUTPUT_COLUMNS + [
    "publication_number",
    "applicant_name",
    "geography_source",
    "geography_source_url",
    "city_mapping_confidence",
    "notes",
]

EXPORT_PATTERNS = (
    "cnipa_industrial_ai_patents_*.csv",
    "cnipa_*.csv",
    "lens_industrial_ai_patents_*.csv",
    "lens_patent_geography_*.csv",
    "google_patents_industrial_ai_patents_*.csv",
)

PUBLICATION_COLUMNS = ("publication_number", "publication_no", "pn", "公开号", "公开(公告)号", "公开公告号")
PATENT_ID_COLUMNS = ("patent_id", "申请号", "application_id")
APPLICANT_COLUMNS = ("applicant_name", "申请人", "assignee")


def discover_patent_export_file(path: Path | None = None, patents_dir: Path | None = None) -> Path | None:
    patents_dir = patents_dir or RAW_PATENTS_DIR
    if path and path.exists():
        return path
    for pattern in EXPORT_PATTERNS:
        matches = sorted(patents_dir.glob(pattern))
        matches = [
            p
            for p in matches
            if "template" not in p.name.lower()
            and "geography" not in p.name.lower()
            and p.parent == patents_dir
        ]
        if matches:
            return matches[0]
    return None


def build_geography_from_export(
    export_path: Path,
    *,
    iids_csv: Path | None = None,
    source_label: str = "",
    source_url: str = "",
) -> pd.DataFrame:
    raw = pd.read_csv(export_path, low_memory=False, encoding="utf-8-sig")
    pub_col = _pick_column(raw, PUBLICATION_COLUMNS)
    pid_col = _pick_column(raw, PATENT_ID_COLUMNS)
    if pub_col is None and pid_col is None:
        raise ValueError(f"No publication or patent id column in {export_path.name}")

    applicant_col = _pick_column(raw, APPLICANT_COLUMNS)
    city_col = _pick_column(raw, GEO_CITY_COLUMNS)
    province_col = _pick_column(raw, GEO_PROVINCE_COLUMNS)
    address_col = _pick_column(raw, GEO_ADDRESS_COLUMNS)

    pub = raw[pub_col].astype(str).str.strip() if pub_col else pd.Series([""] * len(raw))
    pid = raw[pid_col].astype(str).str.strip() if pid_col else pd.Series([""] * len(raw))
    publication_number = pub.where(_non_empty(pub), pid)
    patent_id = publication_number.where(_non_empty(publication_number), pid)

    geo_source_col = _pick_column(raw, ("geo_source", "geography_source", "source", "database"))
    conf_col = _pick_column(
        raw, ("geo_match_confidence", "city_mapping_confidence", "match_confidence")
    )
    notes_col = _pick_column(raw, ("geo_notes", "notes", "provenance"))
    out = pd.DataFrame(
        {
            "patent_id": patent_id,
            "applicant_city": raw[city_col].astype(str) if city_col else "",
            "applicant_province": raw[province_col].astype(str) if province_col else "",
            "applicant_address": raw[address_col].astype(str) if address_col else "",
            "geo_source": raw[geo_source_col].astype(str) if geo_source_col else (source_label or export_path.stem),
            "geo_match_confidence": (
                raw[conf_col].astype(str) if conf_col else "exact_publication_number"
            ),
            "geo_notes": (
                raw[notes_col].astype(str) if notes_col else f"Built from {export_path.name}"
            ),
        }
    )
    out = out[out["patent_id"].astype(str).str.len().gt(0)]
    out = out.drop_duplicates(subset=["patent_id"], keep="first")

    if iids_csv and iids_csv.exists():
        keys = pd.read_csv(iids_csv, usecols=["patent_id"], encoding="utf-8-sig")["patent_id"].astype(str)
        out = out[out["patent_id"].isin(set(keys.str.strip()))]

    return out[GEO_OUTPUT_COLUMNS]
