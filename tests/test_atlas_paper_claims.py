from __future__ import annotations

from pathlib import Path

from diffusion_state.validate_atlas_paper_claims import collect_premature_patent_claim_flags


def test_premature_flags_when_geography_missing(tmp_path: Path) -> None:
    draft = tmp_path / "draft.md"
    draft.write_text(
        "The publication-ready F1 estimate shows pilot-zone x ai-exposure results.\n",
        encoding="utf-8",
    )
    gate = {
        "ready_for_evidence_chain": False,
        "iids_geography_ready": False,
    }
    flags = collect_premature_patent_claim_flags(draft_path=draft, geography_gate=gate)
    assert "premature_f1_publication_claim" in flags
    assert "geography_not_ready" in flags


def test_no_premature_flags_when_evidence_chain_ready(tmp_path: Path) -> None:
    draft = tmp_path / "draft.md"
    draft.write_text("Publication-ready F1 estimate from grounded panel.\n", encoding="utf-8")
    gate = {"ready_for_evidence_chain": True, "iids_geography_ready": True}
    flags = collect_premature_patent_claim_flags(draft_path=draft, geography_gate=gate)
    assert flags == []


def test_exact_geocoding_flag_when_evidence_blocked(tmp_path: Path) -> None:
    draft = tmp_path / "draft.md"
    draft.write_text(
        "We use exact publication-number geocoding for all patents.\n",
        encoding="utf-8",
    )
    gate = {"ready_for_evidence_chain": False, "iids_geography_ready": False}
    flags = collect_premature_patent_claim_flags(draft_path=draft, geography_gate=gate)
    assert "premature_exact_geocoding_claim" in flags
    assert "geography_not_ready" in collect_premature_patent_claim_flags(
        draft_path=draft, geography_gate=gate
    )
