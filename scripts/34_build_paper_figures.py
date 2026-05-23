"""Sync PCS paper figures into paper/figures/ with manifest."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.build_paper_figures import build_paper_figures

if __name__ == "__main__":
    manifest = build_paper_figures()
    for row in manifest:
        print(f"{row['status']:16} {row['paper_path']}")
    missing = [r for r in manifest if r["required"] and r["status"] == "missing"]
    raise SystemExit(1 if missing else 0)
