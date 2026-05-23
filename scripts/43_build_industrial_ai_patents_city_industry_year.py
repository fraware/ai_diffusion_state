"""Build city-industry-year industrial AI patent panel (Atlas Phase 1)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.build_industrial_ai_patents import build_industrial_ai_patents

if __name__ == "__main__":
    panel = build_industrial_ai_patents()
    print(
        f"Wrote {len(panel)} rows; "
        f"{panel['city'].nunique()} cities; "
        f"{panel['industry_code'].nunique()} industries"
    )
