"""Build Atlas-format smart-factory city-industry-year panel."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.build_smart_factory_atlas import build_smart_factory_city_industry_year

if __name__ == "__main__":
    panel = build_smart_factory_city_industry_year()
    print(f"Wrote {len(panel)} city-industry-year rows; total projects {int(panel['smart_factory_count'].sum())}")
