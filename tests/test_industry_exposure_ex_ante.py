from __future__ import annotations

from pathlib import Path

import pytest

from diffusion_state.build_industry_ai_exposure_ex_ante import build_industry_ai_exposure_ex_ante

ROOT = Path(__file__).resolve().parents[1]


def test_build_ex_ante_exposure_no_duplicates():
    df = build_industry_ai_exposure_ex_ante()
    assert not df["industry_code"].duplicated().any()
    assert set(df["ai_exposure_ex_ante"].unique()).issubset({0, 1, 2})
    assert (df["high_exposure_ex_ante"] == (df["ai_exposure_ex_ante"] >= 2)).all()


def test_ex_ante_seed_not_from_outcomes():
    seed = (ROOT / "data" / "seed" / "industry_ai_exposure_ex_ante.csv").read_text(encoding="utf-8")
    assert "smart_factories_clean" not in seed
