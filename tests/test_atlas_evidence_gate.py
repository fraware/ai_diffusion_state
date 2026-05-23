from __future__ import annotations

import json

from diffusion_state.atlas_status import collect_atlas_status
from diffusion_state.utils import PROJECT_ROOT
from diffusion_state.validate_no_fixture_patents import collect_evidence_gate_report


def test_fixture_patents_detected_on_current_repo() -> None:
    report = collect_evidence_gate_report()
    assert report["fixture_patents_detected"] is True
    assert report["patent_source_status"] in ("fixture_micro", "mixed_fixture_and_real")
    assert report["n_raw_patent_records"] >= 100


def test_atlas_software_ready_but_not_evidence_ready() -> None:
    status = collect_atlas_status()
    assert status["atlas_software_ready"] is True
    assert status["atlas_evidence_ready"] is False
    assert status["atlas_phase1_ready"] is False
    assert status["fixture_patents_detected"] is True


def test_evidence_gate_report_written_by_make_target() -> None:
    path = PROJECT_ROOT / "paper" / "atlas_evidence_gate_report.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "fixture_patents_detected" in data
        assert "source_files" in data
