from __future__ import annotations

from diffusion_state.validate_draft_numbers import validate_draft_numbers


def test_draft_v1_numbers_match_tables():
    ok, issues = validate_draft_numbers()
    assert ok, issues
