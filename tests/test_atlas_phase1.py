from __future__ import annotations

from pathlib import Path

from diffusion_state.atlas_status import collect_atlas_status
from diffusion_state.utils import PROJECT_ROOT

ATLAS_ARTIFACTS = [
    "data/seed/industry_crosswalk_atlas.csv",
    "data/processed/industry_ai_exposure_ex_ante_v2.csv",
    "data/processed/industry_robot_compatibility.csv",
    "data/processed/industrial_ai_patents_city_industry_year.csv",
    "data/processed/smart_factory_city_industry_year.csv",
    "data/processed/china_ai_diffusion_atlas_city_industry_year.csv",
    "outputs/tables/table_F1_pilot_x_ai_exposure_patents.csv",
    "paper/draft_atlas_v1.md",
]


def test_atlas_artifact_files_exist() -> None:
    missing = [p for p in ATLAS_ARTIFACTS if not (PROJECT_ROOT / p).exists()]
    assert not missing, f"run make atlas-phase1 first; missing: {missing}"


def test_atlas_phase1_ready_after_build() -> None:
    status = collect_atlas_status()
    assert status["exposure_layer_ready"]
    assert status["patent_layer_ready"]
    assert status["smart_factory_layer_ready"]
    assert status["atlas_panel_ready"]
    assert status["atlas_models_ready"]
    assert status["atlas_phase1_ready"]
    assert status["n_cities"] and status["n_cities"] >= 50
    assert status["n_industries"] and status["n_industries"] >= 20
