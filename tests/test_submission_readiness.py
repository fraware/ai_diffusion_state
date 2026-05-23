from __future__ import annotations

from diffusion_state.validate_draft_claim_compliance import validate_draft_claim_compliance
from diffusion_state.validate_submission_bundle import validate_submission_bundle
from diffusion_state.validate_submission_readiness import (
    validate_draft_language,
    validate_submission_readiness,
)
from diffusion_state.validate_paper_figures import validate_paper_figures
from diffusion_state.validate_paper_tables import validate_paper_tables


def test_draft_language_allows_negated_causality() -> None:
    assert validate_draft_language() == []


def test_paper_figures_after_build() -> None:
    errors = validate_paper_figures()
    assert errors == [], f"run make paper-figures first: {errors}"


def test_paper_tables_embedded() -> None:
    errors = validate_paper_tables()
    assert errors == [], f"run make paper-tables first: {errors}"


def test_draft_claim_compliance() -> None:
    assert validate_draft_claim_compliance() == []


def test_submission_bundle() -> None:
    assert validate_submission_bundle() == []


def test_submission_readiness_smoke() -> None:
    ok, issues = validate_submission_readiness()
    assert ok, issues
