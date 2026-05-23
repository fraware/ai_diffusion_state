"""Backward-compatible entry point — use scripts/52_build_submission_checklist.py."""
from __future__ import annotations

import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parent / "52_build_submission_checklist.py"), run_name="__main__")
