from __future__ import annotations

import re
from pathlib import Path

from diffusion_state.validate_draft_numbers import validate_draft_numbers
from diffusion_state.validate_paper_figures import validate_paper_figures
from diffusion_state.validate_draft_claim_compliance import validate_draft_claim_compliance
from diffusion_state.validate_paper_tables import validate_paper_tables
from diffusion_state.validate_submission_bundle import validate_submission_bundle
from diffusion_state.validate_pcs_gates import validate_pcs_gates
from diffusion_state.utils import PROJECT_ROOT

FORBIDDEN_MAIN_TEXT = [
    (r"\bEPS/NBS model supports\b", "forbidden EPS-equivalent claim"),
    (r"\bfully audited\b.{0,80}\b509\b", "overstates external audit coverage"),
    (r"\bproductivity shock\b.{0,40}\b(proves|proved|demonstrates|establishes)\b", "productivity shock proof language"),
]


def _negated_context(text: str, start: int, end: int) -> bool:
    window = text[max(0, start - 50) : end + 50].lower()
    return any(
        p in window
        for p in (
            "not ",
            "does not",
            "do not",
            "did not",
            "cannot",
            "does not claim",
            "do not estimate",
            "not establish",
            "not identify",
            "not a causal",
            "rather than",
            "not evidence",
        )
    )


def _affirmative_caused(text: str) -> bool:
    for m in re.finditer(r"\bcaused\b", text, re.IGNORECASE):
        if not _negated_context(text, m.start(), m.end()):
            return True
    return False


def _treatment_effect_without_negation(text: str) -> bool:
    for m in re.finditer(r"\btreatment effect\b", text, re.IGNORECASE):
        if not _negated_context(text, m.start(), m.end()):
            return True
    return False

RECOMMENDED_FILES = [
    "paper/draft_v1_submission.md",
    "paper/references.bib",
    "paper/citation_map.csv",
    "paper/figure_manifest.json",
    "paper/table_manifest.json",
    "paper/SUBMISSION_READINESS.md",
    "paper/SUBMISSION_MANIFEST.json",
    "paper/REPRODUCIBILITY.md",
    "paper/DATA_AVAILABILITY.md",
    "paper/SUBMISSION_CHECKLIST.md",
]


def validate_draft_language(draft_path: Path | None = None) -> list[str]:
    draft_path = draft_path or PROJECT_ROOT / "paper" / "draft_v1.md"
    if not draft_path.exists():
        return [f"missing {draft_path.relative_to(PROJECT_ROOT)}"]
    text = draft_path.read_text(encoding="utf-8").lower()
    issues: list[str] = []
    for pattern, msg in FORBIDDEN_MAIN_TEXT:
        if re.search(pattern, text, re.IGNORECASE):
            issues.append(f"language gate: {msg}")
    if _affirmative_caused(text):
        issues.append("language gate: affirmative causal verb 'caused'")
    if _treatment_effect_without_negation(text):
        issues.append("language gate: affirmative treatment-effect claim without negation")
    return issues


def validate_submission_readiness() -> tuple[bool, list[str]]:
    issues: list[str] = []

    pcs_ok, pcs_issues = validate_pcs_gates()
    if not pcs_ok:
        issues.extend([f"pcs: {i}" for i in pcs_issues])

    issues.extend(validate_paper_figures())
    issues.extend(validate_paper_tables())
    issues.extend(validate_submission_bundle())
    issues.extend(validate_draft_claim_compliance())

    bib = PROJECT_ROOT / "paper" / "references.bib"
    if not bib.exists():
        issues.append("missing paper/references.bib")
    else:
        entries = bib.read_text(encoding="utf-8").count("@")
        if entries < 10:
            issues.append(f"references.bib has only {entries} entries (expected >= 10)")

    cmap = PROJECT_ROOT / "paper" / "citation_map.csv"
    if not cmap.exists():
        issues.append("missing paper/citation_map.csv")
    else:
        lines = [ln for ln in cmap.read_text(encoding="utf-8").splitlines() if ln.strip()]
        if len(lines) < 8:
            issues.append("citation_map.csv too sparse")

    sub_draft = PROJECT_ROOT / "paper" / "draft_v1_submission.md"
    if not sub_draft.exists():
        issues.append("missing paper/draft_v1_submission.md — run make export-submission")

    draft_ok, draft_issues = validate_draft_numbers()
    if not draft_ok:
        issues.extend([f"draft_numbers: {d}" for d in draft_issues])

    issues.extend(validate_draft_language())

    for rel in RECOMMENDED_FILES:
        if not (PROJECT_ROOT / rel).exists():
            issues.append(f"recommended artifact missing: {rel}")

    return len(issues) == 0, issues
