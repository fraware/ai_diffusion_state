"""Hub attenuation figure builds from synced main table."""
from __future__ import annotations

from pathlib import Path

from diffusion_state.build_hub_attenuation_figure import build_hub_attenuation_figure
from diffusion_state.utils import PROJECT_ROOT


def test_build_hub_attenuation_figure() -> None:
    path = build_hub_attenuation_figure()
    assert path.exists()
    assert path.stat().st_size > 1000
    assert (PROJECT_ROOT / "paper/main_tables/table_D_hub_exclusion.csv").exists()
