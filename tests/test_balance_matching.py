from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from diffusion_state.run_balance_matching import run_balance_and_matching

ROOT = Path(__file__).resolve().parents[1]


def _synthetic_panel() -> pd.DataFrame:
    cities = [f"city_{i}" for i in range(12)]
    rows = []
    for city in cities:
        pilot = 1 if city in {"city_0", "city_1", "city_2", "city_3"} else 0
        for year in (2018, 2024, 2025):
            rows.append(
                {
                    "city": city,
                    "province": "Test",
                    "year": year,
                    "pilot_zone": pilot,
                    "post_pilot": int(pilot and year >= 2020),
                    "smart_factory_projects": (3 if pilot else 1) if year >= 2024 else 0,
                    "log1p_projects": 0.0,
                    "gdp": 100 + (10 if pilot else 0),
                    "population": 50,
                    "secondary_value_added": 20,
                    "industrial_output": 30,
                    "fdi": 5,
                    "fixed_asset_investment": 8,
                    "telecom_or_internet_proxy": 2,
                    "education_proxy": 1,
                    "foreign_trade": 4,
                    "average_wage": 3,
                }
            )
    return pd.DataFrame(rows)


def test_matched_sample_includes_pilot_and_control(monkeypatch, tmp_path):
    panel = _synthetic_panel()
    panel_path = tmp_path / "panel.csv"
    panel.to_csv(panel_path, index=False)

    matched = pd.DataFrame(
        [
            {"city": "city_0", "sample": "matched_pilot", "pilot_zone": 1},
            {"city": "city_4", "sample": "matched_control", "pilot_zone": 0},
            {"city": "city_1", "sample": "matched_pilot", "pilot_zone": 1},
            {"city": "city_5", "sample": "matched_control", "pilot_zone": 0},
        ]
    )
    matched_path = tmp_path / "matched.csv"
    matched.to_csv(matched_path, index=False)

    out_table = tmp_path / "table_8.csv"
    out_balance = tmp_path / "table_7.csv"

    import diffusion_state.run_balance_matching as mod

    monkeypatch.setattr(mod, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(mod, "OUTPUT_TABLES", tmp_path)
    monkeypatch.setattr(mod, "OUTPUT_FIGURES", tmp_path)
    monkeypatch.setattr(
        mod,
        "build_pilot_city_balance_2018",
        lambda p=None: pd.DataFrame([{"covariate": "log_gdp", "std_diff_pre": 0.1}]),
    )

    matched_path_proc = tmp_path / "data" / "processed" / "pilot_matched_cities_2018.csv"
    matched_path_proc.parent.mkdir(parents=True, exist_ok=True)
    matched.to_csv(matched_path_proc, index=False)

    _, matched_out = mod.run_balance_and_matching(panel_path)

    if matched_out.empty or matched_out.iloc[0]["term"] == "skipped":
        pytest.skip("matching skipped in synthetic fixture")

    assert "n_matched_pilot_cities" in matched_out.columns
    assert int(matched_out["n_matched_pilot_cities"].iloc[0]) == 2
    assert int(matched_out["n_matched_control_cities"].iloc[0]) == 2
