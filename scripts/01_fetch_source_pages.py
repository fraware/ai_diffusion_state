from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.fetch_sources import fetch_source_pages

if __name__ == "__main__":
    fetch_source_pages()
