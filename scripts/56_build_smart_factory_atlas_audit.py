"""Build SF1/SF2 smart-factory Atlas audit tables."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.build_smart_factory_atlas_audit import (
    build_smart_factory_atlas_audit,
    validate_smart_factory_audit,
)

if __name__ == "__main__":
    sf1, sf2 = build_smart_factory_atlas_audit()
    issues = validate_smart_factory_audit()
    print(f"SF1: {len(sf1)} industry mapping rows")
    print(f"SF2: {len(sf2)} top city-industry cells")
    if issues:
        for issue in issues:
            print(f"FAIL: {issue}")
        raise SystemExit(1)
    print("PASS smart-factory Atlas audit")
