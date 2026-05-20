from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def analysis_panel():
    raw_sf = ROOT / "data" / "raw" / "smart_factories" / "2024_mirror.html"
    if not raw_sf.exists():
        pytest.skip("Smart-factory raw HTML required")
    from diffusion_state.build_panel import build_city_year_panel

    build_city_year_panel()
    return pd.read_csv(ROOT / "data" / "processed" / "analysis_city_year_panel.csv")


def test_analysis_panel_schema(analysis_panel):
    required = {
        "city",
        "province",
        "year",
        "pilot_zone",
        "pilot_year",
        "post_pilot",
        "years_since_pilot",
        "smart_factory_projects",
    }
    assert required.issubset(analysis_panel.columns)
    assert not analysis_panel.duplicated(subset=["city", "year"]).any()


def test_post_pilot_logic(analysis_panel):
    treated = analysis_panel[analysis_panel["pilot_zone"] == 1]
    assert (treated["post_pilot"] == (treated["year"] >= treated["pilot_year"])).all()
    control = analysis_panel[analysis_panel["pilot_zone"] == 0]
    assert (control["post_pilot"] == 0).all()
    assert control["pilot_year"].isna().all()


def test_pre_2024_adoption_zero(analysis_panel):
    pre = analysis_panel[analysis_panel["year"] < 2024]
    assert (pre["smart_factory_projects"] == 0).all()


def test_descriptive_tables_exist(analysis_panel):
    from diffusion_state.build_descriptive_tables import build_all_descriptive_tables

    tables = build_all_descriptive_tables()
    for name in tables:
        assert (ROOT / "outputs" / "tables" / name).exists()
