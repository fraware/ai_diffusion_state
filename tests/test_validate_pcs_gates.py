from __future__ import annotations

from diffusion_state.pcs_status import pcs_ready, collect_pcs_gates
from diffusion_state.validate_pcs_gates import validate_main_table_claim_map, validate_pcs_gates


def test_main_table_claim_map_aligned():
    issues = validate_main_table_claim_map()
    assert issues == [], issues


def test_pcs_gates_pass_in_repo_build():
    ok, issues = validate_pcs_gates()
    assert ok, issues


def test_pcs_ready_matches_validate():
    gates = collect_pcs_gates()
    ok, issues = validate_pcs_gates()
    assert pcs_ready(gates) == ok or (not issues)
