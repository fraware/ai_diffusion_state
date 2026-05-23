"""Generate paper/SUBMISSION_CHECKLIST.md from PCS gates."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.build_submission_checklist import build_submission_checklist

if __name__ == "__main__":
    build_submission_checklist()
    print("Wrote paper/SUBMISSION_CHECKLIST.md")
