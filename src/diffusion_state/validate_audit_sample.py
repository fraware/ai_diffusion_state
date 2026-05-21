"""Validate stratified city-resolution audit sample (Engineer B)."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from diffusion_state.utils import PROJECT_ROOT

AUDIT_PATH = PROJECT_ROOT / "data" / "audit" / "city_resolution_sample_audit.csv"
VALID_DECISIONS = frozenset(
    {"confirmed", "incorrect", "uncertain", "insufficient_evidence"}
)


def validate_audit_sample(audit_path: Path | None = None) -> tuple[bool, list[str]]:
    audit_path = audit_path or AUDIT_PATH
    issues: list[str] = []
    if not audit_path.exists():
        return False, [f"missing {audit_path.relative_to(PROJECT_ROOT)}"]

    audit = pd.read_csv(audit_path)
    required = [
        "project_id",
        "assigned_city",
        "resolution_class",
        "auditor_decision",
    ]
    missing_cols = [c for c in required if c not in audit.columns]
    if missing_cols:
        return False, [f"missing columns: {missing_cols}"]

    decisions = audit["auditor_decision"].fillna("").astype(str).str.strip()
    filled = decisions != ""
    n_filled = int(filled.sum())
    if n_filled == 0:
        issues.append("audit pending: no auditor_decision filled")
        return False, issues

    bad = decisions[filled & ~decisions.isin(VALID_DECISIONS)]
    if not bad.empty:
        issues.append(f"invalid auditor_decision values: {bad.unique().tolist()}")

    incorrect = audit[decisions == "incorrect"]
    for col in ("corrected_city", "corrected_province"):
        if col not in audit.columns:
            issues.append(f"incorrect rows require column {col}")
            continue
        missing_corr = incorrect[incorrect[col].fillna("").astype(str).str.strip() == ""]
        if not missing_corr.empty:
            issues.append(f"{len(missing_corr)} incorrect rows missing {col}")

    for rc, n_min in (("rule_based_text_inference", 50), ("official_location_exact", 20)):
        sub = audit[audit["resolution_class"].astype(str) == rc]
        sub_filled = sub[sub["auditor_decision"].fillna("").astype(str).str.strip() != ""]
        if len(sub_filled) < n_min:
            issues.append(
                f"{rc}: only {len(sub_filled)}/{len(sub)} audited (target >={n_min} decisions)"
            )

    return len(issues) == 0, issues
