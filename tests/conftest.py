from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.build_pilot_zones import build_pilot_zones


@pytest.fixture(scope="session")
def pilot_zones_processed() -> None:
    build_pilot_zones()
