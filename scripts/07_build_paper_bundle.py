from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.build_paper_bundle import build_paper_bundle

if __name__ == "__main__":
    build_paper_bundle(strict=True)
    print("Paper bundle complete.")
