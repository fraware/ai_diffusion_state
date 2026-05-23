"""Parse / stage Atlas Phase 1 industrial AI patent raw records."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.parse_industrial_ai_patents import parse_industrial_ai_patents

if __name__ == "__main__":
    df = parse_industrial_ai_patents()
    print(f"Staged {len(df)} patent records for Phase 1 ingest")
