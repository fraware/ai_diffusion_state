"""Print Atlas IIDS workflow phase status (cloud-first execution checklist)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.iids_workflow import WORKFLOW_JSON, write_workflow_report  # noqa: E402

_STATUS_ICON = {
    "complete": "[DONE]",
    "active": "[NOW]",
    "blocked": "[BLOCKED]",
    "pending": "[ ]",
}


def main() -> int:
    p = argparse.ArgumentParser(description="Atlas IIDS workflow phase dashboard.")
    p.add_argument("--json", action="store_true")
    p.add_argument("--strict", action="store_true", help="Exit 1 if any phase is blocked.")
    args = p.parse_args()

    report = write_workflow_report()
    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    print(f"IIDS workflow -> {WORKFLOW_JSON}")
    print(f"Progress: {report['phases_complete']}/{report['phases_total']} phases complete")
    print(f"Canonical production host: {report['canonical_host']}")
    print()
    for phase in report["phases"]:
        icon = _STATUS_ICON.get(phase["status"], "[ ]")
        print(f"{icon} {phase['title']} ({phase['id']})")
        print(f"      {phase['detail']}")
        if phase["blockers"]:
            for b in phase["blockers"]:
                print(f"      ! {b}")
    print()
    print(f"Next: {report['next_command']}")

    if args.strict and report["blocked_phase_ids"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
