"""Prepare drop zone and checklist for CNIPA/Incopat geography batch imports."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.iids_geography_batch import EXPORT_DIR_DEFAULT_NAME  # noqa: E402

EXPORT_DIR = ROOT / "data" / "interim" / EXPORT_DIR_DEFAULT_NAME
KEY_BATCH_DIR = ROOT / "data/interim/iids_geo_key_batches"
EXPECTED_BATCHES = 17
BATCH_GLOB = "iids_geo_export_batch_*.csv"


def main() -> int:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    KEY_BATCH_DIR.mkdir(parents=True, exist_ok=True)

    batches = sorted(EXPORT_DIR.glob(BATCH_GLOB))
    n_batches = len(batches)

    print("=== External geography import (CNIPA/Incopat) ===")
    print(f"  drop_zone: {EXPORT_DIR}")
    print(f"  expected_batch_files: {EXPECTED_BATCHES} ({BATCH_GLOB})")
    print(f"  batch_files_present: {n_batches}")
    print(f"  key_batches_dir: {KEY_BATCH_DIR}")
    print()
    print("Vendor contract: docs/ATLAS_IIDS_GEO_VENDOR_HANDOFF.md")
    print("Engineer runbook: docs/ATLAS_IIDS_GEOGRAPHY_ENGINEER_RUNBOOK.md")
    print()
    print("After all batches land:")
    print("  make atlas-iids-external-geo-pipeline")
    print("  make atlas-iids-control-evidence-chain")
    print("  python scripts/50_atlas_status.py --json --require-evidence")
    print()

    if n_batches == 0:
        print("No batch exports yet. Place files and re-run this script.")
        return 0

    for path in batches[:5]:
        print(f"  found: {path.name} ({path.stat().st_size:,} bytes)")
    if n_batches > 5:
        print(f"  ... and {n_batches - 5} more")

    if n_batches < EXPECTED_BATCHES:
        print(
            f"\nWARN: {n_batches}/{EXPECTED_BATCHES} batches — pipeline can run partially "
            "but 80% coverage may require full set.",
            file=sys.stderr,
        )
        return 0

    print(f"\nAll {EXPECTED_BATCHES} batch slots appear populated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
