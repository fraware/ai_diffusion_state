from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.build_descriptive_tables import build_all_descriptive_tables
from diffusion_state.build_export_upgrading_tables import build_table_export_upgrading
from diffusion_state.run_models import run_sprint_analysis
from diffusion_state.utils import PROJECT_ROOT

if __name__ == "__main__":
    build_all_descriptive_tables()
    run_sprint_analysis()
    sector = PROJECT_ROOT / "data" / "processed" / "export_outcomes_sector_year.csv"
    if sector.exists():
        build_table_export_upgrading()
        print("Legacy table_4 export-upgrading table written.")
    print("Sprint analysis complete (baseline + credibility extensions).")
