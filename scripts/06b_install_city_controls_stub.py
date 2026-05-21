"""Install synthetic city controls for CI / pipeline verification only."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.build_city_controls import build_city_controls_year
from diffusion_state.build_city_controls_stub import STUB_NOTE, install_ci_stub_to_raw


def main() -> int:
    dest = install_ci_stub_to_raw()
    print(f"Installed CI stub to {dest}")
    print(f"NOTE: {STUB_NOTE}")
    df = build_city_controls_year()
    print(f"Built city_controls_year.csv: {len(df)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
