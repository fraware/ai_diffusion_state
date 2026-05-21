from __future__ import annotations

from pathlib import Path

import pandas as pd

from diffusion_state.build_geo_evidence_quality import build_table_geo_evidence_quality
from diffusion_state.utils import PROJECT_ROOT


def test_table16_has_resolution_class_summary(tmp_path, monkeypatch):
    register = PROJECT_ROOT / "data" / "processed" / "city_resolution_register.csv"
    if not register.exists():
        return
    out = build_table_geo_evidence_quality(register_path=register)
    summary = out[out["evidence_type"] == "_all"]
    assert not summary.empty
    assert set(summary["resolution_class"]) >= {
        "official_location_exact",
        "rule_based_text_inference",
    }
    assert (summary["n_projects"].sum()) >= 500
