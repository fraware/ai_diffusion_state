"""Assemble journal submission bundle under paper/submission_bundle/."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.build_submission_bundle import build_submission_bundle

if __name__ == "__main__":
    manifest = build_submission_bundle()
    print(f"Wrote paper/submission_bundle/ ({manifest['n_files']} files)")
    print(f"Manifest: paper/SUBMISSION_MANIFEST.json")
