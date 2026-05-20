from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
BACI_DIR = ROOT / "data" / "raw" / "baci"


@pytest.fixture(scope="session")
def baci_hs6():
    processed = ROOT / "data" / "processed" / "export_outcomes_hs6_year.csv"
    if processed.exists():
        return pd.read_csv(processed)
    if not list(BACI_DIR.glob("BACI_HS17_Y*_V*.csv")):
        pytest.skip("BACI HS17 raw files not present; run scripts/03_build_baci_outcomes.py")
    from diffusion_state.build_baci_outcomes import build_china_export_outcomes

    return build_china_export_outcomes(baci_dir=BACI_DIR)


def test_hs6_no_duplicate_rows(baci_hs6):
    assert not baci_hs6.duplicated(subset=["year", "hs6"]).any()


def test_hs6_non_negative_values(baci_hs6):
    assert (baci_hs6["export_value_usd"] >= 0).all()
    assert (baci_hs6["quantity"] >= 0).all()


def test_unit_value_missing_when_no_quantity(baci_hs6):
    zero_q = baci_hs6["quantity"] <= 0
    assert baci_hs6.loc[zero_q, "unit_value"].isna().all()
    pos = baci_hs6["quantity"] > 0
    assert baci_hs6.loc[pos, "unit_value"].notna().all()


def test_market_share_bounds(baci_hs6):
    defined = baci_hs6["china_world_market_share"].notna()
    share = baci_hs6.loc[defined, "china_world_market_share"]
    assert (share >= 0).all() and (share <= 1).all()


def test_bridge_and_sector_files(baci_hs6):
    bridge = pd.read_csv(ROOT / "data" / "processed" / "hs_to_smart_factory_sector_bridge.csv")
    sector = pd.read_csv(ROOT / "data" / "processed" / "export_outcomes_sector_year.csv")
    assert len(bridge) >= 10
    assert not sector.duplicated(subset=["year", "sector_code"]).any()
    labels = set(
        pd.read_csv(ROOT / "data" / "processed" / "smart_factories_clean.csv")["industry_label"]
    )
    covered = set(bridge["smart_factory_industry_label"])
    assert labels.intersection(covered), "Bridge should cover at least one observed industry label"
