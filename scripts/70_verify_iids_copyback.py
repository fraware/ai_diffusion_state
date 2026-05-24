"""Verify cloud VM copy-back artifacts before geography procurement or evidence chain."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.iids_copyback import VERIFY_JSON, write_copyback_verification  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="Verify IIDS copy-back artifacts on control laptop.")
    p.add_argument("--json", action="store_true")
    p.add_argument(
        "--require-geography",
        action="store_true",
        help="Exit non-zero unless geography supplement is present and non-template.",
    )
    p.add_argument(
        "--require-evidence",
        action="store_true",
        help="Exit non-zero unless ready for full evidence chain.",
    )
    args = p.parse_args()

    report = write_copyback_verification()
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"IIDS copy-back verification -> {VERIFY_JSON}")
        print(f"  ready_for_geography_procurement: {report['ready_for_geography_procurement']}")
        print(f"  ready_for_evidence_chain: {report['ready_for_evidence_chain']}")
        print(f"  iids_rows: {report['iids_rows']}")
        print(f"  unique_patent_ids: {report['unique_patent_ids']}")
        print(f"  geography_present: {report['geography_present']}")
        print(f"  manifest_fill_me_count: {report['manifest_fill_me_count']}")
        print(f"  recommended_next: {report['recommended_next']}")
        if report["blockers"]:
            print("BLOCKERS:")
            for b in report["blockers"]:
                print(f"  - {b}")
        if report["warnings"]:
            print("WARNINGS:")
            for w in report["warnings"]:
                print(f"  - {w}")

    if report["blockers"]:
        return 2
    if args.require_evidence and not report["ready_for_evidence_chain"]:
        return 3
    if args.require_geography and not report["geography_present"]:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
