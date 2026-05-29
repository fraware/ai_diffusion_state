"""Handoff verify reads atlas_tiered_extension_ready from report root, not geo gate."""
from __future__ import annotations

from diffusion_state.engineer_handoff_expectations import (
    ATLAS_TOP_FLAGS_EXPECTED,
    GEO_GATE_FLAGS_EXPECTED,
    evaluate_atlas_tiered_handoff,
)


def test_atlas_top_flag_not_in_geo_gate() -> None:
    atlas = {
        "atlas_tiered_extension_ready": True,
        "iids_geography_gate": {
            "ready_for_evidence_chain": False,
            "iids_geography_ready": False,
            "exact_geography_ready": False,
            "ready_for_tiered_evidence_chain": False,
            "ready_for_tiered_robustness_patent_layer": True,
        },
    }
    checks, gate_values = evaluate_atlas_tiered_handoff(atlas)
    assert checks["atlas_tiered_extension_ready"] is True
    assert gate_values["atlas_tiered_extension_ready"] is True
    assert gate_values["ready_for_evidence_chain"] is False
    assert "atlas_tiered_extension_ready" not in GEO_GATE_FLAGS_EXPECTED


def test_missing_top_flag_fails_check() -> None:
    atlas = {"iids_geography_gate": dict(GEO_GATE_FLAGS_EXPECTED)}
    checks, _ = evaluate_atlas_tiered_handoff(atlas)
    assert checks["atlas_tiered_extension_ready"] is False


def test_all_frozen_flags_pass() -> None:
    atlas = {
        "atlas_tiered_extension_ready": True,
        "iids_geography_gate": dict(GEO_GATE_FLAGS_EXPECTED),
    }
    checks, gate_values = evaluate_atlas_tiered_handoff(atlas)
    assert all(checks.values())
    assert ATLAS_TOP_FLAGS_EXPECTED["atlas_tiered_extension_ready"] is True
