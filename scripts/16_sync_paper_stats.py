"""Refresh auto-synced statistics in paper memos from outputs/tables/."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.sync_paper_stats import sync_all


def main() -> int:
    try:
        updated = sync_all()
    except ValueError as exc:
        print(f"FAIL: {exc}")
        print("Add PCS markers to paper memos or run make analysis first.")
        return 1
    for p in updated:
        print(f"Synced {p.relative_to(ROOT)}")
    if not updated:
        print("No memo files updated.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
