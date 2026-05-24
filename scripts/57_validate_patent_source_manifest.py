"""Validate patent_source_manifest.csv against evidence-path exports."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.validate_patent_source_manifest import (
    validate_patent_source_manifest,
    write_template_manifest,
)

if __name__ == "__main__":
    write_template_manifest()
    issues = validate_patent_source_manifest()
    if issues:
        for issue in issues:
            print(f"FAIL: {issue}")
        raise SystemExit(1)
    print("PASS patent source manifest")
