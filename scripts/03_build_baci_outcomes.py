from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import os
from pathlib import Path
from diffusion_state.build_baci_outcomes import build_china_export_outcomes
from diffusion_state.utils import PROJECT_ROOT

if __name__ == "__main__":
    build_china_export_outcomes(Path(os.environ.get("BACI_DIR", PROJECT_ROOT / "data" / "raw" / "baci")))
