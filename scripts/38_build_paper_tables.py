"""Build markdown renditions of paper/main_tables for submission export."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.build_paper_tables import build_paper_tables_md

if __name__ == "__main__":
    manifest = build_paper_tables_md()
    for row in manifest:
        print(f"{row['status']:8} {row['label']}: {row['markdown_path']}")
    missing = [r for r in manifest if r["status"] != "built"]
    raise SystemExit(1 if missing else 0)
