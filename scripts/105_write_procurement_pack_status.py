"""Write P18 procurement pack status (frozen tiered layer + vendor handoff)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.iids_geography_gate import collect_iids_geography_gate  # noqa: E402
from diffusion_state.procurement_priority_export import load_unresolved_patent_ids  # noqa: E402

DEFAULT_GEO = ROOT / "data/raw/patents/cnipa_patent_geography_2015_2024.csv"
DEFAULT_PROCUREMENT = ROOT / "data/interim/iids_geo_procurement_priority_unresolved.csv"
DEFAULT_EXPORT_DIR = ROOT / "data/interim/iids_geo_exports"
DEFAULT_OUT = ROOT / "outputs/tables/table_P18_procurement_pack_status.json"
TARGET_80_PCT = 0.80
N_KEYS = 4_014_104


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = p.parse_args()

    gate = collect_iids_geography_gate()
    fill = float(gate.get("geography_city_fill_rate") or 0.0)
    n_city = int((gate.get("geography_key_coverage") or {}).get("rows_with_city") or 0)
    need_80 = int(N_KEYS * TARGET_80_PCT)
    gap = max(0, need_80 - n_city)

    unresolved_n = 0
    if DEFAULT_GEO.exists():
        unresolved_n = len(load_unresolved_patent_ids(DEFAULT_GEO))

    batches = list(DEFAULT_EXPORT_DIR.glob("iids_geo_export_batch_*.csv")) if DEFAULT_EXPORT_DIR.exists() else []

    payload = {
        "frozen_tiered_city_fill_rate": fill,
        "tiered_robustness_ready": gate.get("tiered_robustness_ready"),
        "ready_for_evidence_chain": gate.get("ready_for_evidence_chain"),
        "exact_geography_ready": gate.get("exact_geography_ready"),
        "n_keys": N_KEYS,
        "n_city_on_keys": n_city,
        "n_unresolved_on_geo_file": unresolved_n,
        "cities_needed_for_80pct_gate": gap,
        "external_batch_exports_present": len(batches),
        "external_batch_exports_expected": 17,
        "procurement_priority_csv": str(DEFAULT_PROCUREMENT),
        "procurement_priority_csv_exists": DEFAULT_PROCUREMENT.exists(),
        "recommended_next": gate.get("recommended_next"),
        "commands": [
            "make atlas-iids-frozen-verify",
            "make atlas-iids-procurement-priority-unresolved",
            "make atlas-iids-external-geo-pipeline",
            "make atlas-iids-control-evidence-chain",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
