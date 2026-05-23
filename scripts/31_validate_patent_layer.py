"""Validate Workstream A patent layer outputs."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.validate_patent_layer import validate_patent_layer


def main() -> int:
    ok, issues = validate_patent_layer()
    if ok:
        print("OK patent layer validation passed.")
        return 0
    for issue in issues:
        print(issue)
    if any("BLOCKER" in i for i in issues):
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
