from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.build_panel import build_city_year_panel

if __name__ == "__main__":
    df = build_city_year_panel()
    print(f"analysis_city_year_panel.csv: {len(df)} rows")
