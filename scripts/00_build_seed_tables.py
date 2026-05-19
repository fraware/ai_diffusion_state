from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.build_pilot_zones import build_pilot_zones

if __name__ == "__main__":
    df = build_pilot_zones()
    print(f"Built pilot_zones.csv ({len(df)} rows)")
