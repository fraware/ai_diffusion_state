from __future__ import annotations

from diffusion_state.iids_workflow import PhaseId, collect_workflow_phases, collect_workflow_report


def test_workflow_includes_all_phases() -> None:
    phases = collect_workflow_phases()
    ids = {p.id for p in phases}
    assert PhaseId.REPO_READY in ids
    assert PhaseId.CLOUD_PRODUCTION in ids
    assert PhaseId.EVIDENCE_CHAIN in ids
    assert PhaseId.ATLAS_EMPIRICAL in ids


def test_workflow_report_has_next_command() -> None:
    report = collect_workflow_report()
    assert report["phases_total"] >= 6
    assert report["next_command"]
    assert "phases" in report
