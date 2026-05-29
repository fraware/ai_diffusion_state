"""Disk cache for collect_iids_geography_gate (4M-key scans are expensive)."""
from __future__ import annotations

import json
import os
from pathlib import Path

from diffusion_state.utils import PROJECT_ROOT

SNAPSHOT_PATH = (
    PROJECT_ROOT / "outputs" / "tables" / "table_P11_iids_geography_gate_snapshot.json"
)


def _mtime(path: Path) -> float | None:
    return path.stat().st_mtime if path.exists() else None


def snapshot_inputs_fingerprint(
    *,
    iids_csv: Path,
    keys_csv: Path,
    geography_csv: Path,
    min_city_fill: float,
    min_province_fill: float,
    min_key_match_rate: float,
) -> dict[str, object]:
    return {
        "iids_mtime": _mtime(iids_csv),
        "keys_mtime": _mtime(keys_csv),
        "geo_mtime": _mtime(geography_csv),
        "min_city_fill": min_city_fill,
        "min_province_fill": min_province_fill,
        "min_key_match_rate": min_key_match_rate,
    }


def load_cached_gate(fingerprint: dict[str, object]) -> dict | None:
    if os.environ.get("ATLAS_IIDS_GATE_NO_CACHE", "").strip().lower() in ("1", "true", "yes"):
        return None
    if not SNAPSHOT_PATH.exists():
        return None
    try:
        payload = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if payload.get("fingerprint") != fingerprint:
        return None
    gate = payload.get("gate")
    return dict(gate) if isinstance(gate, dict) else None


def write_cached_gate(fingerprint: dict[str, object], gate: dict) -> None:
    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_PATH.write_text(
        json.dumps({"fingerprint": fingerprint, "gate": gate}, indent=2),
        encoding="utf-8",
    )
