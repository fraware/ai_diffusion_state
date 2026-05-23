"""Validate PCS paper figure bundle."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.validate_paper_figures import validate_paper_figures

if __name__ == "__main__":
    errors = validate_paper_figures()
    if errors:
        print("FAIL paper figures:")
        for e in errors:
            print(f"  - {e}")
        raise SystemExit(1)
    print("PASS paper figures")
