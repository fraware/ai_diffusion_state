from __future__ import annotations

from diffusion_state.pcs_status import collect_pcs_gates, pcs_ready


def test_pcs_gates_collect():
    gates = collect_pcs_gates()
    assert gates
    names = {g.name for g in gates}
    assert "city_resolution" in names
    assert "appendix_table_i" in names


def test_pcs_ready_when_build_complete():
    gates = collect_pcs_gates()
    if not pcs_ready(gates):
        blocking = [g for g in gates if not g.passed and g.severity == "error"]
        assert blocking, "expected detail on blocking gates"
