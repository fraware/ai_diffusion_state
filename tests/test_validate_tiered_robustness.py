from diffusion_state.validate_tiered_robustness import (
    validate_industrial_ai_patents_phase1_tiered,
    validate_tiered_robustness_panel,
)


def test_tiered_panel_passes_on_built_iids_panel():
    ok, issues = validate_tiered_robustness_panel()
    assert ok, issues
    assert validate_industrial_ai_patents_phase1_tiered() == []
