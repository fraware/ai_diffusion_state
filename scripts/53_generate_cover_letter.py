"""Generate paper/COVER_LETTER_DRAFT.md from PCS gate report."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.generate_cover_letter import write_cover_letter

if __name__ == "__main__":
    path = write_cover_letter()
    print(f"Wrote {path.relative_to(ROOT)}")
