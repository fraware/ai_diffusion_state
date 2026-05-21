from __future__ import annotations

import pandas as pd

from diffusion_state.build_city_diffusion_typology_ex_ante import build_city_diffusion_typology_ex_ante
from diffusion_state.panel_controls import typology_control_source
from diffusion_state.utils import PROJECT_ROOT


def test_table_18_has_typology_control_source_column():
    panel = PROJECT_ROOT / "data" / "processed" / "analysis_city_year_panel.csv"
    if not panel.exists():
        return
    out = build_city_diffusion_typology_ex_ante(panel)
    assert "typology_control_source" in out.columns
    assert out["typology_control_source"].iloc[0] == typology_control_source(pd.read_csv(panel))
    if out["typology_control_source"].iloc[0] != "real_city_controls":
        assert (out["top_10_gdp_city"] == 0).all()
