from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.run_models import run_baseline_models

if __name__ == "__main__":
    run_baseline_models()
