"""Run Atlas Phase 1 pilot-zone × AI-exposure models."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.run_atlas_models_v02 import run_atlas_models_v02

if __name__ == "__main__":
    results = run_atlas_models_v02()
    for name, df in results.items():
        print(f"{name}: {len(df)} model rows written")
