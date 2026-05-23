"""Optional Pandoc export to Word/PDF (skips if pandoc not installed)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.export_submission_pandoc import export_submission_pandoc

if __name__ == "__main__":
    result = export_submission_pandoc()
    print(f"Pandoc export status: {result['status']}")
    if result.get("docx"):
        print(f"  docx: {result['docx']}")
    if result.get("pdf"):
        print(f"  pdf: {result['pdf']}")
