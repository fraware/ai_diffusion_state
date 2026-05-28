"""IIDS geography procurement preflight (control-laptop checklist)."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.iids_geography_gate import collect_iids_geography_gate  # noqa: E402
from diffusion_state.iids_paths import (  # noqa: E402
    DEFAULT_GEO_OUTPUT,
    FILTERED_PATENT_IDS_FOR_GEO_OUTPUT,
)

BATCH_DIR = ROOT / "data" / "interim" / "iids_geo_key_batches"
EXPORT_DIR = ROOT / "data" / "interim" / "iids_geo_exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)
RAW_GEO = ROOT / "data" / "raw" / "patents" / "cnipa_patent_geography_2015_2024_raw.csv"
BRIEF = ROOT / "docs" / "ATLAS_IIDS_GEOGRAPHY_PROCUREMENT_BRIEF.md"
STATUS_JSON = ROOT / "outputs" / "tables" / "table_P10_iids_geography_procurement_status.json"


def _count_batches() -> int:
    if not BATCH_DIR.exists():
        return 0
    return len(list(BATCH_DIR.glob("iids_geo_keys_batch_*.csv")))


def _count_exports() -> int:
    if not EXPORT_DIR.exists():
        return 0
    return len(list(EXPORT_DIR.glob("*.csv")))


def main() -> int:
    p = argparse.ArgumentParser(description="IIDS geography procurement preflight.")
    p.add_argument("--json", action="store_true")
    p.add_argument(
        "--require-ready",
        action="store_true",
        help="Exit 1 unless ready_for_evidence_chain is true.",
    )
    args = p.parse_args()

    gate = collect_iids_geography_gate()
    coverage_ok: bool | None = None
    coverage_detail = ""
    if DEFAULT_GEO_OUTPUT.exists():
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "75_validate_geography_coverage.py"), "--json"],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        coverage_ok = proc.returncode == 0
        coverage_detail = proc.stdout.strip() or proc.stderr.strip()

    report = {
        "gate": gate,
        "artifacts": {
            "keys_csv": FILTERED_PATENT_IDS_FOR_GEO_OUTPUT.exists(),
            "geography_csv": DEFAULT_GEO_OUTPUT.exists(),
            "raw_geography_csv": RAW_GEO.exists(),
            "procurement_brief": BRIEF.exists(),
            "batch_files": _count_batches(),
            "batch_export_files": _count_exports(),
        },
        "coverage_validation_passed": coverage_ok,
        "next_commands": _next_commands(gate, coverage_ok),
    }

    STATUS_JSON.parent.mkdir(parents=True, exist_ok=True)
    STATUS_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        _print_human(report, coverage_detail)
        print(f"\nWrote {STATUS_JSON.relative_to(ROOT)}")

    if args.require_ready:
        return 0 if gate.get("ready_for_evidence_chain") else 1
    if gate.get("iids_geography_ready"):
        return 0
    return 0 if gate.get("ready_for_geography_procurement") else 2


def _next_commands(gate: dict, coverage_ok: bool | None) -> list[str]:
    if gate.get("ready_for_evidence_chain"):
        return ["make atlas-iids-control-evidence-chain", "python scripts/50_atlas_status.py --json"]
    if gate.get("iids_geography_ready") and coverage_ok is False:
        return [
            "Improve cnipa_patent_geography_2015_2024.csv coverage",
            "make atlas-iids-geo-coverage-validate",
        ]
    if DEFAULT_GEO_OUTPUT.exists():
        return ["make atlas-iids-geo-coverage-validate", "make atlas-iids-geo-validate"]
    if RAW_GEO.exists():
        return ["make atlas-iids-geo-normalize", "make atlas-iids-geo-coverage-validate"]
    if _count_exports() > 0:
        return [
            "make atlas-iids-geo-validate-batches",
            "make atlas-iids-geo-concat",
            "make atlas-iids-geo-normalize",
        ]
    if _count_batches() > 0:
        return [
            "Export geography per batch into data/interim/iids_geo_exports/",
            "make atlas-iids-geo-concat",
        ]
    return [
        "make atlas-iids-geography-brief",
        "make atlas-iids-geo-key-batches",
        "Export geography from CNIPA/Lens using batch files",
    ]


def _print_human(report: dict, coverage_detail: str) -> None:
    gate = report["gate"]
    art = report["artifacts"]
    print("=== IIDS geography preflight ===")
    for key in (
        "iids_patent_export_ready",
        "iids_geography_ready",
        "ready_for_geography_procurement",
        "ready_for_evidence_chain",
        "geography_city_fill_rate",
        "geography_province_fill_rate",
        "geography_key_match_rate",
        "recommended_next",
    ):
        print(f"  {key}: {gate.get(key)}")
    print(f"  batch_files: {art['batch_files']}")
    print(f"  batch_export_files: {art['batch_export_files']}")
    print(f"  geography_csv: {art['geography_csv']}")
    if coverage_detail:
        print(f"  coverage_validate: {report['coverage_validation_passed']}")
    print("\nNext commands:")
    for cmd in report["next_commands"]:
        print(f"  - {cmd}")


if __name__ == "__main__":
    raise SystemExit(main())
