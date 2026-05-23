"""Print PCS sprint gate dashboard for paper owner / reviewers."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.pcs_status import collect_pcs_gates, format_pcs_report, pcs_ready
from diffusion_state.validate_pcs_gates import validate_main_table_claim_map, write_pcs_gate_report


def main() -> int:
    parser = argparse.ArgumentParser(description="PCS sprint gate status")
    parser.add_argument(
        "--json",
        nargs="?",
        const=str(ROOT / "paper" / "pcs_gate_report.json"),
        metavar="PATH",
        help="Write machine-readable gate report (default: paper/pcs_gate_report.json)",
    )
    args = parser.parse_args()

    gates = collect_pcs_gates()
    print(format_pcs_report(gates))

    claim_issues = validate_main_table_claim_map()
    if claim_issues:
        print("\nClaim map issues:")
        for issue in claim_issues:
            print(f"  {issue}")
    else:
        print("\n[PASS] main_table_claim_map aligned with claim_table_map")

    if args.json:
        report_path = Path(args.json)
        report = write_pcs_gate_report(report_path)
        print(f"\nWrote {report_path.relative_to(ROOT)} (ready={report['ready']})")

    ok = pcs_ready(gates) and not claim_issues
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
