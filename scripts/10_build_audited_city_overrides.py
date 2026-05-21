"""Generate audited city overrides and rebuild smart-factory tables."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.audited_city_resolution import build_audited_city_overrides
from diffusion_state.build_smart_factories import build_smart_factories_clean
from diffusion_state.utils import PROJECT_ROOT


def main() -> int:
    print("Step 1: rebuild clean with audited geo resolver...")
    build_smart_factories_clean()

    clean = PROJECT_ROOT / "data" / "processed" / "smart_factories_clean.csv"
    import pandas as pd

    before = int((pd.read_csv(clean)["city"] == "unknown").sum())
    print(f"  unknown after geo pass: {before}")

    print("Step 2: write audited overrides for remaining unknown rows...")
    overrides = build_audited_city_overrides(priority_provinces_only=False)
    print(f"  override rows: {len(overrides)}")

    print("Step 3: rebuild clean applying overrides...")
    build_smart_factories_clean()

    after = int((pd.read_csv(clean)["city"] == "unknown").sum())
    resolved = 509 - after
    print(f"  resolved city projects: {resolved} (target >=250)")
    print(f"  remaining unknown: {after}")

    if len(overrides) < 75 and resolved < 250:
        print(f"WARN: fewer than 75 override rows ({len(overrides)}) and resolved {resolved}<250.")
        return 1
    if resolved < 250:
        print(f"WARN: resolved count {resolved} below 250 target.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
