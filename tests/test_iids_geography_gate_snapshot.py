from __future__ import annotations

import json
from pathlib import Path

from diffusion_state.iids_geography_gate_snapshot import (
    SNAPSHOT_PATH,
    load_cached_gate,
    snapshot_inputs_fingerprint,
    write_cached_gate,
)


def test_gate_snapshot_roundtrip(tmp_path: Path, monkeypatch) -> None:
    snap = tmp_path / "snap.json"
    monkeypatch.setattr(
        "diffusion_state.iids_geography_gate_snapshot.SNAPSHOT_PATH",
        snap,
    )
    fp = snapshot_inputs_fingerprint(
        iids_csv=tmp_path / "i.csv",
        keys_csv=tmp_path / "k.csv",
        geography_csv=tmp_path / "g.csv",
        min_city_fill=0.8,
        min_province_fill=0.8,
        min_key_match_rate=1.0,
    )
    gate = {"tiered_robustness_ready": True, "geography_city_fill_rate": 0.6536}
    write_cached_gate(fp, gate)
    loaded = load_cached_gate(fp)
    assert loaded == gate
    assert snap.exists()


def test_snapshot_path_default_under_outputs() -> None:
    assert "table_P11" in SNAPSHOT_PATH.name
