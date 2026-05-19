from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]

PILOT_ZONE_COLUMNS = {
    "pilot_unit_id",
    "city",
    "province",
    "admin_level",
    "pilot_zone",
    "pilot_year",
    "created_date",
    "announced_date",
    "specialization_zh",
    "specialization_en",
    "source_url",
    "source_name",
    "date_quality",
    "notes",
}

ALLOWED_DATE_QUALITY = {"exact_date", "exact_year", "inferred_year", "uncertain"}

PILOT_YEAR_2019 = {
    "Beijing",
    "Shanghai",
    "Hangzhou",
    "Hefei",
    "Shenzhen",
    "Tianjin",
    "Deqing",
}

PILOT_YEAR_2020 = {
    "Chengdu",
    "Chongqing",
    "Jinan",
    "Xi'an",
    "Guangzhou",
    "Wuhan",
}


def test_pilot_seed_has_17_rows():
    df = pd.read_csv(ROOT / "data" / "seed" / "pilot_zones_seed.csv")
    assert len(df) == 17


def test_pilot_seed_required_columns():
    df = pd.read_csv(ROOT / "data" / "seed" / "pilot_zones_seed.csv")
    required = {"location", "province_or_municipality", "pilot_year", "source_url"}
    assert required.issubset(df.columns)


def test_pilot_seed_years_plausible():
    df = pd.read_csv(ROOT / "data" / "seed" / "pilot_zones_seed.csv")
    assert df["pilot_year"].between(2019, 2021).all()


def test_processed_pilot_zones_contract(pilot_zones_processed):
    path = ROOT / "data" / "processed" / "pilot_zones.csv"
    df = pd.read_csv(path)
    assert len(df) == 17
    assert PILOT_ZONE_COLUMNS.issubset(df.columns)
    assert df["pilot_unit_id"].is_unique
    assert df["city"].is_unique
    assert (df["pilot_zone"] == 1).all()
    assert df["source_url"].notna().all()
    assert set(df["date_quality"]).issubset(ALLOWED_DATE_QUALITY)


def test_processed_pilot_years_known_cities(pilot_zones_processed):
    df = pd.read_csv(ROOT / "data" / "processed" / "pilot_zones.csv")
    by_city = df.set_index("city")["pilot_year"].to_dict()
    for city in PILOT_YEAR_2019:
        assert by_city[city] == 2019, f"{city} expected 2019, got {by_city[city]}"
    for city in PILOT_YEAR_2020:
        assert by_city[city] == 2020, f"{city} expected 2020, got {by_city[city]}"


def test_deqing_county_admin_level(pilot_zones_processed):
    df = pd.read_csv(ROOT / "data" / "processed" / "pilot_zones.csv")
    deqing = df.loc[df["city"] == "Deqing"].iloc[0]
    assert deqing["admin_level"] == "county"
    assert "county" in deqing["notes"].lower()


def test_cset_rows_have_exact_or_year_dates(pilot_zones_processed):
    df = pd.read_csv(ROOT / "data" / "processed" / "pilot_zones.csv")
    cset = df[df["source_name"] == "cset_most_initial_11"]
    assert len(cset) == 11
    assert cset["date_quality"].isin({"exact_date", "exact_year"}).all()
