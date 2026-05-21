from __future__ import annotations

import pandas as pd

from diffusion_state.utils import PROJECT_ROOT


def test_clean_table_has_zero_unknown_when_built():
    path = PROJECT_ROOT / "data" / "processed" / "smart_factories_clean.csv"
    if not path.exists():
        return
    clean = pd.read_csv(path)
    assert (clean["city"] == "unknown").sum() == 0
    assert "resolution_class" in pd.read_csv(
        PROJECT_ROOT / "data" / "seed" / "smart_factory_city_overrides.csv"
    ).columns
