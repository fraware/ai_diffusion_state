from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.parse_smart_factories import parse_smart_factories

if __name__ == "__main__":
    parse_smart_factories()
