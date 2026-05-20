from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]

CLEAN_REQUIRED = {
    "project_id",
    "list_year",
    "batch",
    "firm_name_zh",
    "project_name_zh",
    "location_raw",
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
}

ALLOWED_CITY_CONFIDENCE = {"exact", "high", "medium", "low", "unknown"}
ALLOWED_INDUSTRY_CONFIDENCE = {"high", "medium", "low"}


@pytest.fixture(scope="session")
def smart_factory_tables():
    raw_2024 = ROOT / "data" / "raw" / "smart_factories" / "2024_mirror.html"
    raw_2025 = ROOT / "data" / "raw" / "smart_factories" / "2025_jlts.html"
    if not raw_2024.exists() or not raw_2025.exists():
        pytest.skip("Raw smart-factory HTML not present; fetch sources first")
    from diffusion_state.build_smart_factories import build_all_smart_factories

    build_all_smart_factories()
    return {
        "raw_2024": pd.read_csv(ROOT / "data" / "interim" / "smart_factories_2024_raw.csv"),
        "raw_2025": pd.read_csv(ROOT / "data" / "interim" / "smart_factories_2025_raw.csv"),
        "clean": pd.read_csv(ROOT / "data" / "processed" / "smart_factories_clean.csv"),
        "city_year": pd.read_csv(ROOT / "data" / "processed" / "smart_factory_city_year.csv"),
        "city_industry": pd.read_csv(
            ROOT / "data" / "processed" / "smart_factory_city_industry_year.csv"
        ),
    }


def test_2024_parser_splits_ai_projects_correctly():
    from diffusion_state.parse_smart_factories import parse_2024_list_line

    line = (
        "58 开能健康科技集团股份有限公司 AI 大模型驱动的净水装备智能工厂 上海市"
    )
    row = parse_2024_list_line(line)
    assert row is not None
    assert row["firm_name_zh"].endswith("有限公司") or row["firm_name_zh"].endswith("股份有限公司")
    assert "大模型" in row["project_name_zh"]
    assert row["location_raw"] == "上海市"

    line2 = "223 海信视像科技股份有限公司 基于 AI+大数据的新型显示数智链接智能工厂 青岛市"
    row2 = parse_2024_list_line(line2)
    assert row2["location_raw"] == "青岛市"
    assert "AI+大数据" in row2["project_name_zh"]


def test_smart_factory_sample_columns():
    df = pd.read_csv(ROOT / "data" / "seed" / "smart_factory_sample.csv")
    required = {"batch", "firm", "project", "province_or_city", "source_url"}
    assert required.issubset(df.columns)


def test_interim_row_counts(smart_factory_tables):
    assert len(smart_factory_tables["raw_2024"]) == 235
    assert len(smart_factory_tables["raw_2025"]) == 274


def test_clean_schema_and_uniqueness(smart_factory_tables):
    df = smart_factory_tables["clean"]
    assert len(df) == 509
    assert CLEAN_REQUIRED.issubset(df.columns)
    assert df["project_id"].is_unique
    for col in ["firm_name_zh", "project_name_zh", "province", "list_year", "source_url"]:
        assert df[col].notna().all()
    assert set(df["city_confidence"]).issubset(ALLOWED_CITY_CONFIDENCE)
    assert set(df["industry_confidence"]).issubset(ALLOWED_INDUSTRY_CONFIDENCE)


def test_seed_sample_projects_in_clean(smart_factory_tables):
    sample = pd.read_csv(ROOT / "data" / "seed" / "smart_factory_sample.csv")
    clean = smart_factory_tables["clean"]
    from diffusion_state.smart_factory_geo import normalize_firm_name_zh

    sample = sample.copy()
    sample["firm_norm"] = sample["firm"].map(normalize_firm_name_zh)
    clean = clean.copy()
    clean["firm_norm"] = clean["firm_name_zh"].map(normalize_firm_name_zh)
    merged = sample.merge(clean, on="firm_norm", how="left", suffixes=("_seed", "_clean"))
    missing = merged[merged["project_id"].isna()]
    assert len(missing) == 0, f"Seed sample firms missing from clean: {missing['firm'].tolist()}"


def test_aggregation_reconciliation(smart_factory_tables):
    clean = smart_factory_tables["clean"]
    cy = smart_factory_tables["city_year"]
    ci = smart_factory_tables["city_industry"]

    known = clean[clean["city"] != "unknown"]
    assert cy["smart_factory_projects"].sum() == len(known)
    assert cy["source_rows"].sum() == len(known)
    assert ci["smart_factory_projects"].sum() == len(known)

    unknown_n = (clean["city"] == "unknown").shape[0]
    for year in clean["list_year"].unique():
        cy_year = cy[cy["year"] == year]
        excluded = int(cy_year["unknown_city_rows_excluded"].max())
        unknown_year = (clean[(clean["list_year"] == year) & (clean["city"] == "unknown")]).shape[0]
        assert excluded == unknown_year
        assert (
            cy_year["smart_factory_projects"].sum()
            + excluded
            == (clean["list_year"] == year).sum()
        )

    assert unknown_n > 0


def test_scenario_tags_from_rules_not_empty_for_ai_projects(smart_factory_tables):
    clean = smart_factory_tables["clean"]
    ai_rows = clean[clean["technology_tags"].astype(str).str.len() > 0]
    assert len(ai_rows) > 100
    assert (ai_rows["ai_scenario_tags"].astype(str).str.len() > 0).mean() > 0.5
