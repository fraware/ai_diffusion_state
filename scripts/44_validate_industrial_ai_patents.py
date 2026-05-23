"""Validate Atlas Phase 1 industrial AI patent layer."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.validate_industrial_ai_patents_phase1 import validate_industrial_ai_patents_phase1
from diffusion_state.validate_patent_layer import validate_patent_layer

if __name__ == "__main__":
    errors = validate_industrial_ai_patents_phase1()
    ok, legacy_issues = validate_patent_layer()
    if not ok:
        errors.extend(legacy_issues)
    if errors:
        print("FAIL industrial AI patent validation:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print("PASS industrial AI patent validation (Phase 1)")
