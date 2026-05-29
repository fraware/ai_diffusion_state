"""Validate Atlas Phase 1 industrial AI patent layer."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.validate_industrial_ai_patents_phase1 import validate_industrial_ai_patents_phase1
from diffusion_state.validate_patent_layer import validate_patent_layer
from diffusion_state.validate_tiered_robustness import validate_tiered_robustness_panel

if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument(
        "--tiered-robustness",
        action="store_true",
        help="Validate tiered 60%% extension panel only (not full Phase 1 long ingest).",
    )
    args = p.parse_args()

    if args.tiered_robustness:
        ok, issues = validate_tiered_robustness_panel()
        if not ok:
            print("FAIL tiered robustness patent panel:")
            for e in issues:
                print(f"  - {e}")
            sys.exit(1)
        print("PASS tiered robustness patent panel validation")
        sys.exit(0)

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
