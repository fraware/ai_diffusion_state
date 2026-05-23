"""Verify key statistics in paper/draft_v1.md match regenerated output tables."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.validate_draft_numbers import validate_draft_numbers


def main() -> int:
    ok, issues = validate_draft_numbers()
    if ok:
        print("OK draft_v1.md key numbers match output tables.")
        return 0
    print("FAIL draft number checks:")
    for issue in issues:
        print(f"  {issue}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
