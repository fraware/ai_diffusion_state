"""Fail if draft asserts publication patent claims before evidence chain."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.validate_atlas_paper_claims import (  # noqa: E402
    assert_no_premature_patent_claims,
    collect_draft_patent_claim_violations,
)

GATE_REPORT = ROOT / "paper" / "atlas_gate_report.json"


def _gate_snapshot() -> dict:
    if GATE_REPORT.exists():
        report = json.loads(GATE_REPORT.read_text(encoding="utf-8"))
        return dict(report.get("iids_geography_gate") or {})
    return {"ready_for_evidence_chain": False}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--draft", type=Path, default=ROOT / "paper" / "draft_atlas_v1.md")
    args = p.parse_args()

    flags = collect_draft_patent_claim_violations(
        draft_path=args.draft,
        geography_gate=_gate_snapshot(),
    )
    if flags:
        print("FAIL premature patent / F1 claims in draft:", file=sys.stderr)
        for f in flags:
            print(f"  - {f}", file=sys.stderr)
        print(
            "\nWhile ready_for_evidence_chain=false: use tiered robustness framing only. "
            "See docs/ATLAS_IIDS_TIERED_ROBUSTNESS_FROZEN.md",
            file=sys.stderr,
        )
        return 1

    assert_no_premature_patent_claims(
        draft_path=args.draft,
        geography_gate=_gate_snapshot(),
    )
    print("PASS atlas paper claim guard (no premature patent/F1 language)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
