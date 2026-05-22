from __future__ import annotations

from diffusion_state.validate_audit_sample import validate_audit_sample
from diffusion_state.utils import PROJECT_ROOT


def test_audit_sample_validation():
    path = PROJECT_ROOT / "data" / "audit" / "city_resolution_sample_audit.csv"
    if not path.exists():
        return
    ok, issues = validate_audit_sample(path)
    if ok:
        assert issues == []
        return
    assert any("pending" in i or "audited" in i for i in issues)
