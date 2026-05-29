"""Tests for manual mapping incremental coverage (P13)."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "m90",
    ROOT / "scripts" / "90_measure_manual_mapping_incremental_coverage.py",
)
m90 = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(m90)


def test_incremental_counts(tmp_path: Path) -> None:
    iids = tmp_path / "iids.csv"
    inferred = tmp_path / "inferred.csv"
    top_map = tmp_path / "top_map.csv"

    pd.DataFrame(
        {
            "patent_id": ["P1", "P2", "P3"],
            "applicant_name": [
                "SHENZHEN ACME LTD",
                "BEIJING BETA UNIV",
                "GENERIC CORP",
            ],
        }
    ).to_csv(iids, index=False)

    pd.DataFrame(
        {
            "patent_id": ["P1"],
            "applicant_city": ["Shenzhen"],
            "applicant_province": ["Guangdong"],
            "geo_match_confidence": ["applicant_name_city_token"],
        }
    ).to_csv(inferred, index=False)

    pd.DataFrame(
        {
            "applicant_name": ["BEIJING BETA UNIV"],
            "applicant_city": ["Beijing"],
            "applicant_province": ["Beijing"],
            "source_url": ["http://example.edu"],
            "geo_match_confidence": ["university_location"],
            "notes": [""],
        }
    ).to_csv(top_map, index=False)

    stats = m90.measure(iids_csv=iids, name_inferred_csv=inferred, top_map_csv=top_map)
    assert stats["manual_applicants_with_city"] == 1
    assert stats["patents_with_manual_applicant"] == 1
    assert stats["manual_patents_already_name_token_covered"] == 0
    assert stats["manual_patents_incremental"] == 1
    assert stats["tiered_city_fill_after_manual"] == pytest.approx(2 / 3, rel=1e-3)
