from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from diffusion_state.pcs_status import PAPER_TABLES, collect_pcs_gates, pcs_ready
from diffusion_state.utils import PROJECT_ROOT

MAIN_TABLE_CLAIM_MAP = PROJECT_ROOT / "data" / "seed" / "main_table_claim_map.csv"
CLAIM_TABLE_MAP = PROJECT_ROOT / "paper" / "claim_table_map.csv"


def validate_main_table_claim_map() -> list[str]:
    issues: list[str] = []
    main_dir = PROJECT_ROOT / "paper" / "main_tables"
    if not MAIN_TABLE_CLAIM_MAP.exists():
        return [f"MISSING {MAIN_TABLE_CLAIM_MAP.relative_to(PROJECT_ROOT)}"]
    mapping = pd.read_csv(MAIN_TABLE_CLAIM_MAP)
    if not CLAIM_TABLE_MAP.exists():
        issues.append(f"MISSING {CLAIM_TABLE_MAP.relative_to(PROJECT_ROOT)}")
        return issues

    claims = pd.read_csv(CLAIM_TABLE_MAP)
    claim_ids = set(claims["claim_id"].astype(str))

    for table in PAPER_TABLES:
        if not (main_dir / table).exists():
            issues.append(f"main_tables missing: {table}")
    for _, row in mapping.iterrows():
        cid = str(row["claim_id"])
        if cid not in claim_ids:
            issues.append(f"main_table_claim_map claim_id not in claim_table_map: {cid}")
    mapped_tables = set(mapping["paper_table"].astype(str))
    for table in PAPER_TABLES:
        if table not in mapped_tables:
            issues.append(f"main_table_claim_map missing row for {table}")
    return issues


def write_pcs_gate_report(path: Path | None = None) -> dict:
    path = path or PROJECT_ROOT / "paper" / "pcs_gate_report.json"
    gates = collect_pcs_gates()
    claim_issues = validate_main_table_claim_map()
    submission_ready = False
    submission_issues: list[str] = []
    try:
        from diffusion_state.validate_submission_readiness import validate_submission_readiness

        submission_ready, submission_issues = validate_submission_readiness()
    except Exception as exc:  # noqa: BLE001
        submission_issues = [str(exc)]

    report = {
        "ready": bool(pcs_ready(gates) and not claim_issues),
        "submission_ready": bool(submission_ready),
        "gates": [
            {
                "name": g.name,
                "passed": bool(g.passed),
                "detail": str(g.detail),
                "severity": str(g.severity),
            }
            for g in gates
        ],
        "main_table_claim_issues": claim_issues,
        "submission_issues": submission_issues,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    return report


def validate_pcs_gates() -> tuple[bool, list[str]]:
    gates = collect_pcs_gates()
    issues: list[str] = []
    if not pcs_ready(gates):
        for g in gates:
            if not g.passed and g.severity == "error":
                issues.append(f"{g.name}: {g.detail}")
    issues.extend(validate_main_table_claim_map())
    return len(issues) == 0, issues
