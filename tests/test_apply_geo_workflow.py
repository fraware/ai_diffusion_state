from __future__ import annotations

from diffusion_state.apply_geo_workflow_updates import apply_external_verification_queue
from diffusion_state.utils import PROJECT_ROOT


def test_apply_external_verification_queue_runs():
    qpath = PROJECT_ROOT / "data" / "interim" / "external_verification_queue.csv"
    if not qpath.exists():
        return
    _, n = apply_external_verification_queue()
    assert n >= 0
