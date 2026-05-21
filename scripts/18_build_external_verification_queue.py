"""Build prioritized queue for external city-verification (Engineer B)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.build_external_verification_queue import build_external_verification_queue


def main() -> int:
    q = build_external_verification_queue()
    print(f"Wrote {len(q)} rows to data/interim/external_verification_queue.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
