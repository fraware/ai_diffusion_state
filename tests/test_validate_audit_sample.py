from __future__ import annotations

from diffusion_state.validate_audit_sample import validate_audit_sample
from diffusion_state.utils import PROJECT_ROOT


def test_audit_pending_when_empty_decisions():
    path = PROJECT_ROOT / "data" / "audit" / "city_resolution_sample_audit.csv"
    if not path.exists():
        return
    ok, issues = validate_audit_sample(path)
    assert not ok
    assert any("pending" in i for i in issues)
