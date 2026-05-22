"""Run appendix-only public-fallback control models.

This produces outputs/tables/table_5b_public_fallback_controls.csv from ChinaUTC
public city-yearbook controls. It is intentionally separate from strict Table 5.

Use only as appendix robustness. It is not EPS-equivalent because FDI and fixed-asset
investment remain unavailable in the current public fallback.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.run_public_fallback_controls import run_public_fallback_controls

if __name__ == "__main__":
    out = run_public_fallback_controls()
    print(out[out["term"].isin(["pilot_zone", "skipped", "error"])].to_string(index=False))
