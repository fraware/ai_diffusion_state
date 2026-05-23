"""Validate PCS submission package (gates + figures + draft + bibliography)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.validate_submission_readiness import validate_submission_readiness

if __name__ == "__main__":
    ok, issues = validate_submission_readiness()
    if issues:
        print("FAIL submission readiness:")
        for issue in issues:
            print(f"  - {issue}")
        raise SystemExit(1)
    print("PASS submission readiness (PCS engineering package)")
