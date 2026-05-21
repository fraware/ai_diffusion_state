"""Remove CI stub city controls from raw/ and processed/."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.panel_controls import purge_stub_city_controls


def main() -> int:
    removed = purge_stub_city_controls()
    if removed:
        print("Removed:")
        for p in removed:
            print(f"  {p}")
    else:
        print("No stub city-control artifacts found.")
    print("Next: place EPS/NBS in data/raw/city_controls/, then make city-controls && make panel && make analysis")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
