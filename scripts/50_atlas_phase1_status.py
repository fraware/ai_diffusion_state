"""Print Atlas Phase 1 readiness flags (JSON with --json)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.validate_atlas_v02 import validate_atlas_v02
from diffusion_state.validate_industry_exposure_v2 import validate_industry_exposure_v2
from diffusion_state.validate_industrial_ai_patents_phase1 import validate_industrial_ai_patents_phase1
from diffusion_state.validate_patent_layer import validate_patent_layer


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    exposure_ok = len(validate_industry_exposure_v2()) == 0
    pat_phase1 = validate_industrial_ai_patents_phase1()
    pat_ok, pat_legacy = validate_patent_layer()
    patent_ok = len(pat_phase1) == 0 and pat_ok
    atlas_ok = len(validate_atlas_v02()) == 0
    models_ok = (ROOT / "outputs" / "tables" / "table_F1_pilot_x_ai_exposure_patents.csv").exists()

    status = {
        "exposure_layer_ready": exposure_ok,
        "patent_layer_ready": patent_ok,
        "atlas_assembly_ready": atlas_ok,
        "atlas_models_ready": models_ok,
        "atlas_phase1_ready": exposure_ok and patent_ok and atlas_ok and models_ok,
        "patent_legacy_issues": pat_legacy if not patent_ok else [],
    }

    if args.json:
        print(json.dumps(status, indent=2))
    else:
        for k, v in status.items():
            if k != "patent_legacy_issues":
                print(f"{k}: {v}")
    return 0 if status["atlas_phase1_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
