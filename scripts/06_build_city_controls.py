from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.build_city_controls import build_city_controls_year

if __name__ == "__main__":
    df = build_city_controls_year()
    print(f"city_controls_year.csv: {len(df)} rows")
