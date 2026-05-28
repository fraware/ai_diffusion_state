"""Fail fast unless IIDS geography gate is ready for the evidence chain."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.iids_geography_gate import collect_iids_geography_gate  # noqa: E402


def main() -> int:
    gate = collect_iids_geography_gate()
    if gate.get("ready_for_evidence_chain"):
        print("IIDS geography gate: ready for evidence chain")
        return 0
    print("ERROR: IIDS geography not ready for evidence chain.", file=sys.stderr)
    print(f"  recommended_next: {gate.get('recommended_next')}", file=sys.stderr)
    for key in (
        "iids_patent_export_ready",
        "iids_geography_ready",
        "geography_city_fill_rate",
        "geography_province_fill_rate",
        "geography_key_match_rate",
    ):
        print(f"  {key}: {gate.get(key)}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
