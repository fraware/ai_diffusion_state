from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.build_baci_outcomes import build_china_export_outcomes
from diffusion_state.fetch_baci import fetch_baci_hs17
from diffusion_state.utils import PROJECT_ROOT


def _baci_ready() -> bool:
    baci_dir = PROJECT_ROOT / "data" / "raw" / "baci"
    return bool(list(baci_dir.glob("BACI_HS17_Y*_V*.csv")))


if __name__ == "__main__":
    if not _baci_ready():
        print("Downloading CEPII BACI HS17 (202601); this is ~800 MB compressed...")
        fetch_baci_hs17()
    hs6 = build_china_export_outcomes()
    print(f"export_outcomes_hs6_year.csv: {len(hs6)} rows, years {sorted(hs6['year'].unique())}")
