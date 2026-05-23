"""Export submission-ready draft with figures and citation index."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.export_draft_submission import export_draft_submission

if __name__ == "__main__":
    md_path, tex_path = export_draft_submission()
    print(f"Wrote {md_path.relative_to(ROOT)}")
    if tex_path:
        print(f"Wrote {tex_path.relative_to(ROOT)}")
