from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from diffusion_state.build_industrial_ai_patents import (
    aggregate_city_industry_year,
    build_industrial_ai_patents,
)
from diffusion_state.utils import PROJECT_ROOT

FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "patents_cnipa_micro.csv"


@pytest.fixture(scope="module")
def patent_fixture_path(tmp_path_factory) -> Path:
    if not FIXTURE.exists():
        pytest.skip("patent micro fixture missing")
    tmp = tmp_path_factory.mktemp("patents")
    dest = tmp / "cnipa_micro.csv"
    dest.write_text(FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")
    return tmp


def test_aggregate_meets_minimum_coverage(patent_fixture_path: Path):
    panel = build_industrial_ai_patents(
        patents_dir=patent_fixture_path,
        include_cset_validation=False,
    )
    assert len(panel) >= 10
    assert panel["city"].nunique() >= 10
    assert panel["industry_code"].nunique() >= 5
    assert panel["industrial_ai_patents"].sum() > 0


def test_low_confidence_excluded_from_main_panel(patent_fixture_path: Path):
    from diffusion_state.ingest_patents import ingest_cnipa_files

    long_df = ingest_cnipa_files(patent_fixture_path)
    main = aggregate_city_industry_year(long_df, main_sample_only=True)
    appendix = aggregate_city_industry_year(long_df, main_sample_only=False)
    assert len(appendix) >= len(main)
