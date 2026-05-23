from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from diffusion_state.ingest_patents import ingest_all_patents, write_patents_long
from diffusion_state.patent_taxonomy import CATEGORY_COLUMNS, category_count_columns
from diffusion_state.utils import PROJECT_ROOT, write_csv

PRIMARY_CONFIDENCE = {"high", "medium"}
YEAR_MIN = 2015
YEAR_MAX = 2024

PROCESSED_COLUMNS = [
    "city",
    "province",
    "industry",
    "industry_code",
    "year",
    "ai_patents",
    "industrial_ai_patents",
    *category_count_columns(),
    "invention_patents",
    "utility_model_patents",
    "granted_patents",
    "citation_weighted_patents",
    "pct_or_family_patents",
    "source",
    "coverage_note",
]


def _analysis_year(row: pd.Series) -> int | None:
    for col in ("application_year", "publication_year", "grant_year"):
        val = row.get(col)
        if val is None or (isinstance(val, float) and np.isnan(val)):
            continue
        try:
            y = int(val)
        except (TypeError, ValueError):
            continue
        if YEAR_MIN <= y <= YEAR_MAX:
            return y
    return None


def _patent_type_bucket(patent_type: str | None) -> tuple[int, int, int]:
    if not patent_type or (isinstance(patent_type, float) and np.isnan(patent_type)):
        return 0, 0, 0
    text = str(patent_type).lower()
    invention = int("invention" in text or "发明" in text)
    utility = int("utility" in text or "实用新型" in text)
    granted = int("granted" in text or "授权" in text)
    return invention, utility, granted


def build_industrial_ai_patents_long(
    patents_dir: Path | None = None,
    interim_path: Path | None = None,
    include_cset_validation: bool = False,
) -> pd.DataFrame:
    long_df = ingest_all_patents(patents_dir, include_cset_validation=include_cset_validation)
    return write_patents_long(long_df, interim_path)


def aggregate_city_industry_year(
    long_df: pd.DataFrame,
    main_sample_only: bool = True,
) -> pd.DataFrame:
    if long_df.empty:
        return pd.DataFrame(columns=PROCESSED_COLUMNS)

    df = long_df.copy()
    df = df[df["is_excluded_non_industrial"] == 0]
    df = df[df["is_industrial_ai"] == 1]
    df = df[df["source"] != "cset_1790"]

    if main_sample_only:
        df = df[df["industry_mapping_confidence"].isin(PRIMARY_CONFIDENCE)]
        df = df[df["city"].astype(str).str.len() > 0]

    df["year"] = df.apply(_analysis_year, axis=1)
    df = df[df["year"].notna()]

    if df.empty:
        return pd.DataFrame(columns=PROCESSED_COLUMNS)

    group_cols = ["city", "province", "industry_code", "industry_label", "year", "source"]
    named_agg: dict[str, tuple] = {
        "industrial_ai_patents": ("patent_id", "count"),
        "ai_patents": ("patent_id", "count"),
    }
    for cat in CATEGORY_COLUMNS:
        named_agg[f"{cat}_patents"] = (cat, "sum")

    panel = df.groupby(group_cols, as_index=False).agg(**named_agg)
    panel = panel.rename(columns={"industry_label": "industry"})

    inv_ut_gr = []
    for _, row in df.iterrows():
        inv, ut, gr = _patent_type_bucket(row.get("patent_type"))
        inv_ut_gr.append((row["city"], row["province"], row["industry_code"], row["year"], inv, ut, gr))
    type_df = pd.DataFrame(
        inv_ut_gr,
        columns=["city", "province", "industry_code", "year", "invention", "utility", "granted"],
    )
    type_agg = (
        type_df.groupby(["city", "province", "industry_code", "year"], as_index=False)
        .agg(
            invention_patents=("invention", "sum"),
            utility_model_patents=("utility", "sum"),
            granted_patents=("granted", "sum"),
        )
    )
    panel = panel.merge(type_agg, on=["city", "province", "industry_code", "year"], how="left")
    panel["citation_weighted_patents"] = np.nan
    panel["pct_or_family_patents"] = np.nan
    panel["coverage_note"] = "city_industry_year_from_microdata"
    return panel[PROCESSED_COLUMNS]


def build_taxonomy_counts(long_df: pd.DataFrame) -> pd.DataFrame:
    if long_df.empty:
        return pd.DataFrame(columns=["category", "patent_count", "source"])
    df = long_df[long_df["is_industrial_ai"] == 1]
    rows = []
    for cat in CATEGORY_COLUMNS:
        rows.append(
            {
                "category": cat,
                "patent_count": int(df[cat].sum()),
                "source": "combined_ingest",
            }
        )
    return pd.DataFrame(rows)


def build_coverage_table(panel: pd.DataFrame) -> pd.DataFrame:
    if panel.empty:
        return pd.DataFrame(
            columns=[
                "metric",
                "value",
            ]
        )
    cats_populated = sum(
        1 for c in CATEGORY_COLUMNS if f"{c}_patents" in panel.columns and panel[f"{c}_patents"].sum() > 0
    )
    rows = [
        {"metric": "n_city_industry_year_rows", "value": len(panel)},
        {"metric": "n_cities", "value": panel["city"].nunique()},
        {"metric": "n_industries", "value": panel["industry_code"].nunique()},
        {"metric": "year_min", "value": int(panel["year"].min())},
        {"metric": "year_max", "value": int(panel["year"].max())},
        {"metric": "n_taxonomy_categories_populated", "value": cats_populated},
        {"metric": "total_industrial_ai_patents", "value": int(panel["industrial_ai_patents"].sum())},
    ]
    return pd.DataFrame(rows)


def build_cset_validation_tables(
    long_df: pd.DataFrame,
    tables_dir: Path | None = None,
) -> None:
    tables_dir = tables_dir or PROJECT_ROOT / "outputs" / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)
    cset = long_df[long_df["source"] == "cset_1790"]
    if cset.empty:
        return
    tax = build_taxonomy_counts(cset)
    tax["source"] = "cset_1790_china"
    write_csv(tax, tables_dir / "table_A1_patent_taxonomy_counts_cset_validation.csv")


def build_industrial_ai_patents(
    patents_dir: Path | None = None,
    processed_path: Path | None = None,
    interim_path: Path | None = None,
    include_cset_validation: bool = False,
) -> pd.DataFrame:
    patents_dir = patents_dir or PROJECT_ROOT / "data" / "raw" / "patents"
    processed_path = processed_path or (
        PROJECT_ROOT / "data" / "processed" / "industrial_ai_patents_city_industry_year.csv"
    )
    interim_path = interim_path or PROJECT_ROOT / "data" / "interim" / "industrial_ai_patents_long.csv"

    long_df = build_industrial_ai_patents_long(
        patents_dir,
        interim_path,
        include_cset_validation=include_cset_validation,
    )

    panel = aggregate_city_industry_year(long_df, main_sample_only=True)
    write_csv(panel, processed_path)

    tables_dir = PROJECT_ROOT / "outputs" / "tables"
    main_long = long_df[long_df["source"] != "cset_1790"] if len(long_df) else long_df
    write_csv(build_taxonomy_counts(main_long), tables_dir / "table_A1_patent_taxonomy_counts.csv")
    write_csv(build_coverage_table(panel), tables_dir / "table_A2_city_industry_patent_coverage.csv")
    build_cset_validation_tables(long_df, tables_dir)
    return panel
