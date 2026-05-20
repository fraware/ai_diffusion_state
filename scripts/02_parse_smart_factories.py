from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.build_smart_factories import build_all_smart_factories

if __name__ == "__main__":
    df = build_all_smart_factories()
    print(f"Built {len(df)} smart-factory projects (2024+2025)")
