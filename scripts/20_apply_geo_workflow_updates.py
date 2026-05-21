"""Apply audit corrections and external verification queue to override seed."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.apply_geo_workflow_updates import (
    apply_audit_corrections,
    apply_external_verification_queue,
)


def main() -> int:
    seed_ext, n_ext = apply_external_verification_queue()
    seed_audit, n_audit = apply_audit_corrections()
    print(f"external verification rows applied: {n_ext}")
    print(f"audit corrections applied: {n_audit}")
    if n_ext or n_audit:
        print("Re-run: make geo-audit && make panel && make analysis")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
