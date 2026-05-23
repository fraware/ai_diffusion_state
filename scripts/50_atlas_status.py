"""Atlas Phase 1 status dashboard (JSON with --json)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.atlas_status import collect_atlas_status, write_atlas_gate_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Atlas Phase 1 gate status")
    parser.add_argument(
        "--json",
        nargs="?",
        const=str(ROOT / "paper" / "atlas_gate_report.json"),
        metavar="PATH",
        help="Write JSON report (default: paper/atlas_gate_report.json)",
    )
    args = parser.parse_args()

    if args.json:
        report = write_atlas_gate_report(Path(args.json))
    else:
        report = collect_atlas_status()

    print("=== Atlas Phase 1 status ===")
    for key in (
        "pcs_ready",
        "atlas_ready",
        "exposure_layer_ready",
        "patent_layer_ready",
        "smart_factory_layer_ready",
        "atlas_panel_ready",
        "atlas_models_ready",
    ):
        print(f"  {key}: {report[key]}")
    print(f"  cities/industries/years: {report['n_cities']}/{report['n_industries']}/{report['years_min']}-{report['years_max']}")
    print(f"  main_result: {report['main_result_summary']}")

    if args.json:
        print(f"\nWrote {Path(args.json).relative_to(ROOT)} (atlas_ready={report['atlas_ready']})")

    return 0 if report["atlas_phase1_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
