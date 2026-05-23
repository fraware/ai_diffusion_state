"""Validate Atlas smart-factory city-industry-year layer."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.validate_smart_factory_atlas import validate_smart_factory_city_industry_year

if __name__ == "__main__":
    errors = validate_smart_factory_city_industry_year()
    if errors:
        print("FAIL smart-factory atlas validation:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print("PASS smart-factory atlas validation")
