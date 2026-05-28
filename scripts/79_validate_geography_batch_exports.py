"""Validate per-batch geography exports against key batches (Engineer A QA)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.iids_geography_batch import validate_all_export_batches  # noqa: E402

BATCH_DIR = ROOT / "data" / "interim" / "iids_geo_key_batches"
EXPORT_DIR = ROOT / "data" / "interim" / "iids_geo_exports"


def main() -> int:
    p = argparse.ArgumentParser(description="Validate geography batch exports vs key batches.")
    p.add_argument("--batch-dir", type=Path, default=BATCH_DIR)
    p.add_argument("--export-dir", type=Path, default=EXPORT_DIR)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    if not args.export_dir.exists() or not any(args.export_dir.glob("*.csv")):
        print(f"ERROR: no exports in {args.export_dir}", file=sys.stderr)
        print("Place iids_geo_export_batch_001.csv … 017.csv before running.", file=sys.stderr)
        return 1

    report = validate_all_export_batches(args.batch_dir, args.export_dir)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(
            f"Batches: {report['n_export_batches']}/{report['n_key_batches']} exports present; "
            f"{report['n_passed']} passed thresholds"
        )
        for batch in report["batches"]:
            if batch.get("error"):
                print(f"  FAIL {batch.get('batch', batch.get('keys_file'))}: {batch['error']}")
            else:
                status = "PASS" if batch.get("passed") else "FAIL"
                print(
                    f"  {status} {batch['batch']}: city={batch.get('city_fill_rate', 0):.1%} "
                    f"province={batch.get('province_fill_rate', 0):.1%} "
                    f"match={batch.get('key_match_rate', 0):.1%}"
                )
    return 0 if report.get("all_passed") else 2


if __name__ == "__main__":
    raise SystemExit(main())
