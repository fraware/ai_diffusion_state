from __future__ import annotations

from diffusion_state.panel_controls import city_controls_source, purge_stub_city_controls
from diffusion_state.utils import PROJECT_ROOT


def test_purge_removes_stub_processed_if_present():
    processed = PROJECT_ROOT / "data" / "processed" / "city_controls_year.csv"
    if processed.exists():
        import pandas as pd

        if pd.read_csv(processed)["source_name"].astype(str).str.contains(
            "pipeline_ci_stub", case=False, na=False
        ).any():
            purge_stub_city_controls()
    assert city_controls_source() in ("missing", "production")
