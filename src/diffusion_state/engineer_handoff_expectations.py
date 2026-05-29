"""Frozen gate expectations for engineer/paper-owner handoff verification."""

from __future__ import annotations

GEO_GATE_FLAGS_EXPECTED: dict[str, bool] = {
    "ready_for_evidence_chain": False,
    "iids_geography_ready": False,
    "exact_geography_ready": False,
    "ready_for_tiered_evidence_chain": False,
    "ready_for_tiered_robustness_patent_layer": True,
}

ATLAS_TOP_FLAGS_EXPECTED: dict[str, bool] = {
    "atlas_tiered_extension_ready": True,
}


def evaluate_atlas_tiered_handoff(atlas_report: dict) -> tuple[dict[str, bool], dict[str, object]]:
    """Return (checks_passed, gate_values) for frozen tiered extension handoff."""
    geo = atlas_report.get("iids_geography_gate") or {}
    checks_passed = {k: geo.get(k) == v for k, v in GEO_GATE_FLAGS_EXPECTED.items()}
    checks_passed.update({k: atlas_report.get(k) == v for k, v in ATLAS_TOP_FLAGS_EXPECTED.items()})
    gate_values = {
        **{k: geo.get(k) for k in GEO_GATE_FLAGS_EXPECTED},
        **{k: atlas_report.get(k) for k in ATLAS_TOP_FLAGS_EXPECTED},
    }
    return checks_passed, gate_values
