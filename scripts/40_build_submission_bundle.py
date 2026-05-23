"""Backward-compatible entry point — use scripts/51_build_submission_bundle.py."""
from __future__ import annotations

import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parent / "51_build_submission_bundle.py"), run_name="__main__")
