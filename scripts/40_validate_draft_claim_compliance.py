"""Language and claim-tier compliance for paper drafts."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.validate_draft_claim_compliance import validate_draft_claim_compliance


def main() -> int:
    issues = validate_draft_claim_compliance()
    if not issues:
        print("OK draft claim compliance (PCS + appendix).")
        return 0
    print("FAIL draft claim compliance:")
    for issue in issues:
        print(f"  {issue}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
