"""Tests for applicant-name city token gazetteer."""
from __future__ import annotations

from diffusion_state.china_city_gazetteer import (
    geography_from_applicant_name,
    match_city_from_applicant_name,
)


def test_shenzhen_english_company() -> None:
    entry = match_city_from_applicant_name("SHENZHEN NEW IND BIOMEDICAL ENGINEERING CO LTD")
    assert entry is not None
    assert entry.city_en == "Shenzhen"


def test_beijing_chinese() -> None:
    entry = match_city_from_applicant_name("北京某某科技有限公司")
    assert entry is not None
    assert entry.city_en == "Beijing"


def test_no_guess_generic() -> None:
    assert match_city_from_applicant_name("STATE GRID ELECTRIC POWER CO LTD") is None


def test_geography_contract_keys() -> None:
    geo = geography_from_applicant_name("杭州市某公司")
    assert geo["applicant_city"] == "Hangzhou"
    assert geo["geo_match_confidence"] == "applicant_name_city_token"
