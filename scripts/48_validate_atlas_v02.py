"""Validate Atlas v0.2 assembly."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.validate_atlas_v02 import validate_atlas_v02

if __name__ == "__main__":
    errors = validate_atlas_v02()
    if errors:
        print("FAIL atlas v0.2 validation:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print("PASS atlas v0.2 validation")
