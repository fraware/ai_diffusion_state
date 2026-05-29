"""Unit tests for Lens geography export helpers."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "lens_geo",
    ROOT / "scripts" / "79_lens_geography_export.py",
)
lens_geo = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(lens_geo)


def test_norm_id_strips_non_alnum() -> None:
    assert lens_geo.norm_id("CN-109556919-A") == "CN109556919A"


def test_parse_china_geo_zh_municipality() -> None:
    city, province = lens_geo.parse_china_geo("北京市海淀区中关村")
    assert province == "Beijing"
    assert city in {"Beijing", "北京"}


def test_parse_china_geo_zh_city_suffix() -> None:
    city, province = lens_geo.parse_china_geo("广东省深圳市南山区")
    assert province == "Guangdong"
    assert "深圳" in city


def test_extract_first_applicant_with_address() -> None:
    record = {
        "biblio": {
            "parties": {
                "applicants": [
                    {
                        "extracted_name": {"value": "ACME CO"},
                        "extracted_address": "广东省深圳市南山区",
                    }
                ]
            }
        }
    }
    name, address, suffix = lens_geo.extract_first_applicant(record)
    assert name == "ACME CO"
    assert "深圳" in address
    assert suffix == ""
