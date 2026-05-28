from __future__ import annotations

import json

from diffusion_state.atlas_status import collect_atlas_status
from diffusion_state.utils import PROJECT_ROOT
from diffusion_state.validate_no_fixture_patents import collect_evidence_gate_report


def test_evidence_gate_not_passed_until_geography_ready() -> None:
    report = collect_evidence_gate_report()
    assert report["evidence_gate_passed"] is False
    if report["real_patent_source_present"] and not report["fixture_patents_detected"]:
        assert report["iids_geography_ready"] is False
        assert report["ready_for_evidence_chain"] is False
        assert "iids_geography_gate" in report
    else:
        assert report["fixture_patents_detected"] is True
        assert report["real_patent_source_present"] is False
        assert report["patent_source_status"] in (
            "missing_real_exports",
            "fixture_micro_in_evidence_path",
        )


def test_atlas_software_ready_but_not_evidence_ready() -> None:
    status = collect_atlas_status()
    assert status["atlas_software_ready"] is True
    assert status["atlas_evidence_ready"] is False
    if status["fixture_patents_detected"]:
        assert status["atlas_phase1_ready"] is False
    else:
        assert status["iids_patent_export_ready"] is True
        assert status["iids_geography_ready"] is False
        assert status["ready_for_evidence_chain"] is False


def test_quarantined_fixtures_not_in_evidence_path() -> None:
    report = collect_evidence_gate_report()
    for name in report.get("source_files", []):
        assert "fixtures/" not in name
        assert name not in {
            "industrial_ai_patent_records.csv",
            "cnipa_micro.csv",
            "patent_database.csv",
        }


def test_evidence_gate_report_fields() -> None:
    path = PROJECT_ROOT / "paper" / "atlas_evidence_gate_report.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "fixture_patents_detected" in data
        assert "quarantined_fixture_files" in data
        assert "manifest_path" in data
