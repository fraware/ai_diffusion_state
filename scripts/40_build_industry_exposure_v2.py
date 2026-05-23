"""Build Atlas Phase 1 ex ante AI exposure and robot compatibility layers."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.build_industry_exposure_v2 import build_industry_exposure_v2

if __name__ == "__main__":
    exposure, robot = build_industry_exposure_v2()
    print(f"Wrote {len(exposure)} industries to industry_ai_exposure_ex_ante_v2.csv")
    print(f"Wrote {len(robot)} industries to industry_robot_compatibility.csv")
