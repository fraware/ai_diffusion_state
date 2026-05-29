"""Verify engineer handoff gates (PCS submission + frozen tiered patent layer)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.validate_atlas_paper_claims import collect_draft_patent_claim_violations  # noqa: E402

PCS_REPORT = ROOT / "paper" / "pcs_gate_report.json"
ATLAS_REPORT = ROOT / "paper" / "atlas_gate_report.json"
CONFIRM_OUT = ROOT / "paper" / "ENGINEER_HANDOFF_CONFIRMATION.json"

PCS_ARTIFACTS = [
    "paper/SUBMISSION_OWNER_BRIEF.md",
    "paper/SUBMISSION_CHECKLIST.md",
    "paper/COVER_LETTER_DRAFT.md",
    "paper/results_memo.md",
    "paper/red_team_memo.md",
    "paper/reviewer_results_snapshot.md",
    "paper/claim_table_map.csv",
    "paper/FINAL_ARTIFACT_INVENTORY.md",
]

ATLAS_ARTIFACTS = [
    "paper/atlas_gate_report.json",
    "outputs/tables/table_P14_tiered_geography_coverage_by_confidence.csv",
    "outputs/tables/table_P17_tiered_geography_tier_breakdown.csv",
    "outputs/tables/table_P17_tiered_robustness_audit.csv",
    "data/processed/industrial_ai_patents_city_industry_year.csv",
]

TIERED_FLAGS_EXPECTED = {
    "ready_for_evidence_chain": False,
    "iids_geography_ready": False,
    "exact_geography_ready": False,
    "ready_for_tiered_evidence_chain": False,
    "ready_for_tiered_robustness_patent_layer": True,
    "atlas_tiered_extension_ready": True,
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    issues: list[str] = []
    sections: dict[str, object] = {}

    # --- PCS ---
    pcs_ok = False
    if not PCS_REPORT.exists():
        issues.append("missing paper/pcs_gate_report.json (run make pcs-paper-owner)")
    else:
        pcs = _load_json(PCS_REPORT)
        pcs_ok = bool(pcs.get("ready")) and bool(pcs.get("submission_ready"))
        if not pcs.get("ready"):
            issues.append("pcs ready=false")
        if not pcs.get("submission_ready"):
            issues.append("pcs submission_ready=false")
        missing_pcs = [p for p in PCS_ARTIFACTS if not (ROOT / p).exists()]
        if missing_pcs:
            issues.append(f"PCS artifacts missing: {missing_pcs}")
        zip_path = ROOT / "paper" / "submission_bundle.zip"
        bundle_dir = ROOT / "paper" / "submission_bundle"
        if not zip_path.exists() and not bundle_dir.exists():
            issues.append("missing submission_bundle.zip and submission_bundle/")
        sections["pcs"] = {
            "ready": pcs.get("ready"),
            "submission_ready": pcs.get("submission_ready"),
            "main_tables_dir": (ROOT / "paper/main_tables").exists(),
        }

    # --- Atlas tiered ---
    atlas_ok = False
    if not ATLAS_REPORT.exists():
        issues.append("missing paper/atlas_gate_report.json (run make atlas-iids-frozen-verify)")
    else:
        atlas = _load_json(ATLAS_REPORT)
        geo = atlas.get("iids_geography_gate") or {}
        flag_checks = {k: geo.get(k) == v for k, v in TIERED_FLAGS_EXPECTED.items()}
        flag_checks["atlas_tiered_extension_ready"] = (
            atlas.get("atlas_tiered_extension_ready") is True
        )
        atlas_ok = all(flag_checks.values())
        for k, ok in flag_checks.items():
            if not ok:
                issues.append(f"atlas flag {k}: got {atlas.get(k) or geo.get(k)}")
        missing_atlas = [p for p in ATLAS_ARTIFACTS if p != "paper/atlas_gate_report.json" and not (ROOT / p).exists()]
        if missing_atlas:
            issues.append(f"Atlas artifacts missing: {missing_atlas}")
        sections["atlas_tiered"] = flag_checks

    # --- Claim guard ---
    claim_ok = False
    geo_gate: dict = {"ready_for_evidence_chain": False}
    if ATLAS_REPORT.exists():
        geo_gate = _load_json(ATLAS_REPORT).get("iids_geography_gate") or geo_gate
    violations = collect_draft_patent_claim_violations(geography_gate=geo_gate)
    claim_ok = len(violations) == 0
    if violations:
        issues.append(f"claim guard violations in draft_atlas_v1.md: {violations}")
    sections["claim_guard"] = {"violations": violations, "pass": claim_ok}

    # Optional live claim-guard subprocess
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/103_validate_atlas_paper_claims.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    sections["claim_guard_script_exit"] = proc.returncode

    payload = {
        "all_pass": pcs_ok and atlas_ok and claim_ok and proc.returncode == 0,
        "pcs_pass": pcs_ok,
        "atlas_tiered_pass": atlas_ok,
        "claim_guard_pass": claim_ok and proc.returncode == 0,
        "issues": issues,
        "sections": sections,
    }
    CONFIRM_OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("=== Engineer handoff verification ===")
    print(f"  PCS ready + submission_ready: {pcs_ok}")
    print(f"  Atlas tiered flags: {atlas_ok}")
    print(f"  Claim guard: {claim_ok and proc.returncode == 0}")
    print(f"  Wrote {CONFIRM_OUT.relative_to(ROOT)}")
    if issues:
        print("\nIssues:", file=sys.stderr)
        for i in issues:
            print(f"  - {i}", file=sys.stderr)
        return 1
    print("\nAll handoff checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
