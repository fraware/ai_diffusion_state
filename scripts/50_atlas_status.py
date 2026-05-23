"""Atlas status dashboard (software vs evidence readiness)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.atlas_status import collect_atlas_status, write_atlas_gate_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Atlas gate status")
    parser.add_argument(
        "--json",
        nargs="?",
        const=str(ROOT / "paper" / "atlas_gate_report.json"),
        metavar="PATH",
        help="Write JSON report (default: paper/atlas_gate_report.json)",
    )
    parser.add_argument(
        "--require-evidence",
        action="store_true",
        help="Exit 1 unless atlas_evidence_ready is true",
    )
    args = parser.parse_args()

    if args.json:
        report = write_atlas_gate_report(Path(args.json))
    else:
        report = collect_atlas_status()

    print("=== Atlas status ===")
    for key in (
        "pcs_ready",
        "atlas_software_ready",
        "atlas_evidence_ready",
        "atlas_ready",
        "atlas_phase1_ready",
        "fixture_patents_detected",
        "patent_source_status",
        "patent_layer_ready",
        "atlas_models_ready",
    ):
        print(f"  {key}: {report[key]}")
    print(
        f"  cities/industries/years: {report['n_cities']}/{report['n_industries']}/"
        f"{report['years_min']}-{report['years_max']}"
    )
    print(f"  main_result: {report['main_result_summary']}")
    if report.get("f1_publication_ready_detail"):
        print(f"  f1_detail: {report['f1_publication_ready_detail']}")

    if args.json:
        print(f"\nWrote {Path(args.json).relative_to(ROOT)}")

    if args.require_evidence:
        return 0 if report["atlas_evidence_ready"] else 1
    return 0 if report["atlas_software_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
