"""Fail fast unless tiered geography meets robustness threshold (default 60%)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.iids_geography_gate import collect_iids_geography_gate  # noqa: E402


def main() -> int:
    gate = collect_iids_geography_gate()
    if gate.get("ready_for_tiered_robustness_patent_layer"):
        print(
            "Tiered robustness gate: ready for patent-layer build "
            f"(city fill {gate.get('geography_city_fill_rate')})"
        )
        return 0

    print("=" * 72, file=sys.stderr)
    print("BLOCKED: tiered robustness patent layer cannot run yet.", file=sys.stderr)
    print("=" * 72, file=sys.stderr)
    print(file=sys.stderr)
    for key in (
        "geography_city_fill_rate",
        "tiered_robustness_fill_threshold",
        "tiered_robustness_ready",
        "recommended_next",
    ):
        print(f"  {key}: {gate.get(key)}", file=sys.stderr)
    print(file=sys.stderr)
    print("Run: make atlas-iids-tiered-geography-phase-g", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
