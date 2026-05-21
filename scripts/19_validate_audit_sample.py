"""Validate city-resolution audit sample completeness."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.validate_audit_sample import validate_audit_sample


def main() -> int:
    ok, issues = validate_audit_sample()
    if ok:
        print("OK audit sample validation")
        return 0
    print("FAIL audit sample:")
    for i in issues:
        print(f"  {i}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
