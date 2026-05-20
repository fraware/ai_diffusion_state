from __future__ import annotations

from pathlib import Path

import pandas as pd

from diffusion_state.parse_smart_factories import parse_smart_factory_lists
from diffusion_state.smart_factory_geo import normalize_firm_name_zh, resolve_geo
from diffusion_state.smart_factory_overrides import apply_city_overrides
from diffusion_state.smart_factory_tags import tag_project
from diffusion_state.utils import PROJECT_ROOT, write_csv

CLEAN_COLUMNS = [
    "project_id",
    "list_year",
    "batch",
    "firm_name_zh",
    "firm_name_en",
    "project_name_zh",
    "project_name_en",
    "province",
    "city",
    "city_confidence",
    "industry_code",
    "industry_label",
    "industry_confidence",
    "ai_scenario_tags",
    "technology_tags",
    "source_url",
    "source_file",
    "row_number_original",
    "parse_method",
    "manual_override_flag",
    "notes",
]

INDUSTRIAL_AI_TAGS = {
    "machine_vision",
    "ai_quality_inspection",
    "predictive_maintenance",
    "digital_twin",
    "intelligent_scheduling",
    "industrial_robotics",
    "smart_logistics",
    "industrial_internet",
    "ai_server",
    "semiconductor",
    "battery",
    "new_energy_vehicle",
}


def _build_project_id(list_year: int, batch: str, rank: int) -> str:
    batch_slug = batch.replace(" ", "_").lower()
    return f"{list_year}_{batch_slug}_{rank:04d}"


def build_smart_factories_clean(
    interim_dir: Path | None = None,
    out_path: Path | None = None,
    raw_dir: Path | None = None,
) -> pd.DataFrame:
    interim_dir = interim_dir or PROJECT_ROOT / "data" / "interim"
    out_path = out_path or PROJECT_ROOT / "data" / "processed" / "smart_factories_clean.csv"

    path_2024 = interim_dir / "smart_factories_2024_raw.csv"
    path_2025 = interim_dir / "smart_factories_2025_raw.csv"
    if not path_2024.exists() or not path_2025.exists():
        parse_smart_factory_lists(raw_dir=raw_dir, interim_dir=interim_dir)

    raw_frames = [
        pd.read_csv(path_2024),
        pd.read_csv(path_2025),
    ]
    raw = pd.concat(raw_frames, ignore_index=True)

    records: list[dict] = []
    for _, row in raw.iterrows():
        firm_zh = normalize_firm_name_zh(str(row["firm_name_zh"]))
        project_zh = str(row["project_name_zh"])
        geo = resolve_geo(str(row["location_raw"]), firm_zh, project_zh)
        tags = tag_project(firm_zh, project_zh)
        rank = int(row["rank"])
        list_year = int(row["list_year"])
        batch = str(row["batch"])
        notes = geo.geo_notes
        records.append(
            {
                "project_id": _build_project_id(list_year, batch, rank),
                "list_year": list_year,
                "batch": batch,
                "firm_name_zh": firm_zh,
                "firm_name_en": "",
                "project_name_zh": row["project_name_zh"],
                "project_name_en": "",
                "province": geo.province,
                "city": geo.city,
                "city_confidence": geo.city_confidence,
                "industry_code": tags.industry_code,
                "industry_label": tags.industry_label,
                "industry_confidence": tags.industry_confidence,
                "ai_scenario_tags": tags.ai_scenario_tags,
                "technology_tags": tags.technology_tags,
                "source_url": row["source_url"],
                "source_file": row["source_file"],
                "row_number_original": rank,
                "parse_method": row["parse_method"],
                "manual_override_flag": 0,
                "notes": notes,
            }
        )

    df = pd.DataFrame(records)[CLEAN_COLUMNS]
    if df["project_id"].duplicated().any():
        raise ValueError("Duplicate project_id values in clean table")
    df = apply_city_overrides(df)
    write_csv(df, out_path)
    return df


def _is_ai_tagged(tags: str) -> bool:
    if not tags or pd.isna(tags):
        return False
    return any(t in tags.split("|") for t in INDUSTRIAL_AI_TAGS)


def aggregate_city_year(clean: pd.DataFrame) -> pd.DataFrame:
    known = clean[clean["city"] != "unknown"].copy()
    known["ai_tagged"] = known["ai_scenario_tags"].map(_is_ai_tagged)
    known["industrial_ai"] = known["technology_tags"].astype(str).str.len() > 0

    agg = (
        known.groupby(["city", "province", "list_year"], as_index=False)
        .agg(
            smart_factory_projects=("project_id", "count"),
            smart_factory_projects_ai_tagged=("ai_tagged", "sum"),
            smart_factory_projects_industrial_ai=("industrial_ai", "sum"),
            num_distinct_firms=("firm_name_zh", "nunique"),
            num_distinct_industries=("industry_code", "nunique"),
            source_rows=("project_id", "count"),
        )
        .rename(columns={"list_year": "year"})
    )
    excluded = (
        clean[clean["city"] == "unknown"]
        .groupby("list_year", as_index=False)
        .agg(unknown_city_rows_excluded=("project_id", "count"))
        .rename(columns={"list_year": "year"})
    )
    agg = agg.merge(excluded, on="year", how="left")
    # Year-level count: do not sum across city rows (same value would repeat per city).
    agg["unknown_city_rows_excluded"] = agg["unknown_city_rows_excluded"].fillna(0).astype(int)
    return agg.sort_values(["year", "city"]).reset_index(drop=True)


def aggregate_city_industry_year(clean: pd.DataFrame) -> pd.DataFrame:
    known = clean[clean["city"] != "unknown"].copy()
    known["ai_tagged"] = known["ai_scenario_tags"].map(_is_ai_tagged)
    agg = (
        known.groupby(
            ["city", "province", "industry_code", "industry_label", "list_year"],
            as_index=False,
        )
        .agg(
            smart_factory_projects=("project_id", "count"),
            smart_factory_projects_ai_tagged=("ai_tagged", "sum"),
            num_distinct_firms=("firm_name_zh", "nunique"),
            source_rows=("project_id", "count"),
        )
        .rename(columns={"list_year": "year"})
    )
    return agg.sort_values(["year", "city", "industry_code"]).reset_index(drop=True)


def build_smart_factory_aggregates(
    clean_path: Path | None = None,
    city_year_path: Path | None = None,
    city_industry_path: Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    clean_path = clean_path or PROJECT_ROOT / "data" / "processed" / "smart_factories_clean.csv"
    city_year_path = city_year_path or PROJECT_ROOT / "data" / "processed" / "smart_factory_city_year.csv"
    city_industry_path = (
        city_industry_path or PROJECT_ROOT / "data" / "processed" / "smart_factory_city_industry_year.csv"
    )

    clean = pd.read_csv(clean_path)
    cy = aggregate_city_year(clean)
    ci = aggregate_city_industry_year(clean)
    write_csv(cy, city_year_path)
    write_csv(ci, city_industry_path)
    return cy, ci


def build_all_smart_factories(raw_dir: Path | None = None) -> pd.DataFrame:
    parse_smart_factory_lists(raw_dir=raw_dir)
    clean = build_smart_factories_clean(raw_dir=raw_dir)
    build_smart_factory_aggregates()
    return clean


if __name__ == "__main__":
    out = build_all_smart_factories()
    print(f"smart_factories_clean.csv: {len(out)} projects")
