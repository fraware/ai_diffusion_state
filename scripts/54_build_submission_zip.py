"""Create paper/submission_bundle.zip for journal portal upload."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.build_submission_zip import build_submission_zip

if __name__ == "__main__":
    path = build_submission_zip()
    print(f"Wrote {path.relative_to(ROOT)} ({path.stat().st_size:,} bytes)")
