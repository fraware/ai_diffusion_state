"""Validate Atlas Phase 1 industry exposure and robot compatibility layers."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.validate_industry_exposure_v2 import validate_industry_exposure_v2

if __name__ == "__main__":
    errors = validate_industry_exposure_v2()
    if errors:
        print("FAIL industry exposure v2 validation:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print("PASS industry exposure v2 validation")
