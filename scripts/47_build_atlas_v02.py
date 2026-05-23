"""Assemble China AI Diffusion Atlas city-industry-year v0.2."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.build_atlas_v02 import build_atlas_v02

if __name__ == "__main__":
    panel = build_atlas_v02()
    print(
        f"Wrote atlas v0.2: {len(panel)} rows, "
        f"{panel['city'].nunique()} cities, {panel['industry_code'].nunique()} industries"
    )
