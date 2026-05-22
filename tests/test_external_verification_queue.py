from __future__ import annotations

from diffusion_state.build_external_verification_queue import build_external_verification_queue
from diffusion_state.utils import PROJECT_ROOT


def test_external_verification_queue_builds():
    reg = PROJECT_ROOT / "data" / "processed" / "city_resolution_register.csv"
    if not reg.exists():
        return
    q = build_external_verification_queue()
    assert len(q) <= 50
    assert "priority_rank" in q.columns
    assert q["resolution_class"].isin(
        {"rule_based_text_inference", "external_evidence_verified"}
    ).all()
