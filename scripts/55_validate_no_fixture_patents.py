"""Atlas Phase 2: detect fixture-backed patent microdata (see docs/ATLAS_PHASE2_REAL_EVIDENCE_INSTRUCTIONS.md)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.validate_no_fixture_patents import (
    collect_evidence_gate_report,
    write_evidence_gate_report,
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Atlas no-fixture patent evidence gate")
    parser.add_argument(
        "--json",
        nargs="?",
        const=str(ROOT / "paper" / "atlas_evidence_gate_report.json"),
        metavar="PATH",
        help="Write JSON report",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 when fixture patents detected or evidence gate fails",
    )
    args = parser.parse_args()

    if args.json:
        report = write_evidence_gate_report(Path(args.json))
    else:
        report = collect_evidence_gate_report()

    print("=== Atlas patent evidence gate ===")
    for key in (
        "fixture_patents_detected",
        "real_patent_source_present",
        "patent_source_status",
        "n_raw_patent_records",
        "n_unique_patent_ids",
        "n_source_files",
    ):
        print(f"  {key}: {report[key]}")
    if report.get("source_files"):
        print(f"  source_files: {', '.join(report['source_files'])}")

    if args.json:
        print(f"\nWrote {Path(args.json).relative_to(ROOT)}")

    failed = report["fixture_patents_detected"] or not report.get("evidence_gate_passed", False)
    if args.strict and failed:
        raise SystemExit(1)
    raise SystemExit(0)
