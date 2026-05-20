from __future__ import annotations

from pathlib import Path

import pandas as pd

from diffusion_state.build_analysis_city_industry_panel import (
    build_analysis_city_industry_year_panel,
)
from diffusion_state.build_analysis_panel import (
    build_analysis_city_year_panel,
    build_smart_factory_province_year,
)
from diffusion_state.utils import PROJECT_ROOT, write_csv


def build_city_year_panel(
    pilot_path: Path | None = None,
    smart_factory_path: Path | None = None,
    city_controls_path: Path | None = None,
    out_path: Path | None = None,
) -> pd.DataFrame:
    """Build analysis panel and province-year adoption (legacy entry point)."""
    build_smart_factory_province_year()
    df = build_analysis_city_year_panel(
        pilot_path=pilot_path,
        city_controls_path=city_controls_path,
    )
    if out_path:
        write_csv(df, out_path)
    else:
        write_csv(df, PROJECT_ROOT / "data" / "processed" / "analysis_city_year_panel.csv")

    sector_path = PROJECT_ROOT / "data" / "processed" / "export_outcomes_sector_year.csv"
    if sector_path.exists():
        build_analysis_city_industry_year_panel()
    return df
