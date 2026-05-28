"""Fail fast unless IIDS geography gate is ready for the evidence chain."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.iids_geography_gate import collect_iids_geography_gate  # noqa: E402

EXPORT_DIR = ROOT / "data" / "interim" / "iids_geo_exports"
GEO_CSV = ROOT / "data" / "raw" / "patents" / "cnipa_patent_geography_2015_2024.csv"


def main() -> int:
    gate = collect_iids_geography_gate()
    if gate.get("ready_for_evidence_chain"):
        print("IIDS geography gate: ready for evidence chain")
        return 0

    print("=" * 72, file=sys.stderr)
    print("BLOCKED: atlas-iids-control-evidence-chain cannot run yet.", file=sys.stderr)
    print("=" * 72, file=sys.stderr)
    print(file=sys.stderr)
    print("Reason: applicant geography is not on disk or fails coverage gates.", file=sys.stderr)
    print(f"  geography_csv exists: {GEO_CSV.exists()}", file=sys.stderr)
    print(f"  batch_export_files:   {EXPORT_DIR.exists() and any(EXPORT_DIR.glob('*.csv'))}", file=sys.stderr)
    print(file=sys.stderr)
    print("Engineer A — export 17 batches to:", file=sys.stderr)
    print(f"  {EXPORT_DIR}", file=sys.stderr)
    print("  iids_geo_export_batch_001.csv … iids_geo_export_batch_017.csv", file=sys.stderr)
    print(file=sys.stderr)
    print("Then run:", file=sys.stderr)
    print("  make atlas-iids-geo-validate-batches", file=sys.stderr)
    print("  make atlas-iids-geo-normalize  # or concat + normalize", file=sys.stderr)
    print("  make atlas-iids-geo-coverage-validate", file=sys.stderr)
    print("  make atlas-iids-control-evidence-chain", file=sys.stderr)
    print(file=sys.stderr)
    print(f"recommended_next: {gate.get('recommended_next')}", file=sys.stderr)
    for key in (
        "iids_patent_export_ready",
        "iids_geography_ready",
        "geography_city_fill_rate",
        "geography_province_fill_rate",
        "geography_key_match_rate",
    ):
        print(f"  {key}: {gate.get(key)}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
