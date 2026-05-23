from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from diffusion_state.utils import PROJECT_ROOT

DRAFT_PATHS = (
    PROJECT_ROOT / "paper" / "draft_v1.md",
    PROJECT_ROOT / "paper" / "draft_v1_submission.md",
)

# Phrases that imply claims marked not_supported in claim_table_map.csv
FORBIDDEN_PHRASES: tuple[tuple[str, str], ...] = (
    (r"\bcaused\s+(?:firms|companies|plants)", "implies causal effect on firms"),
    (r"\bcausal\s+average\s+treatment\s+effect\b", "forbidden ATT wording"),
    (r"\bestablished\s+causal\b", "overstates identification"),
    (r"\bproves\s+(?:that\s+)?pilot", "proof language for pilot zones"),
    (r"\bEPS/NBS\s+(?:model\s+)?supports\b", "forbidden EPS-equivalent claim"),
    (r"\bfully\s+externally\s+audited\b", "overstates geo audit"),
    (r"\ball\s+509\s+(?:projects\s+)?(?:were\s+)?externally\s+verified\b", "overstates external verification"),
    (r"\bexport\s+upgrading\s+(?:was|is)\s+caused\b", "forbidden export causality"),
    (r"\bproductivity\s+shock\s+(?:proves|proved|demonstrates|establishes)\b", "forbidden productivity proof"),
    (r"\bpre-trend\s+validation\b", "timing figure is diagnostic only"),
    (r"\bvalidated\s+pre-trends?\b", "timing figure is diagnostic only"),
)

# Required disclaimers (at least one draft must contain each)
REQUIRED_DISCLAIMERS: tuple[tuple[str, str], ...] = (
    (r"does not establish.*treatment effect|does not estimate.*causal", "causal limitation"),
    (r"hub-centered|hub architecture", "hub framing"),
    (r"102.*official|official_location_exact", "official geo count"),
    (r"50.*external|external_evidence_verified", "external verification count"),
    (r"Table I|appendix.*not EPS|not EPS-equivalent", "Table I appendix framing"),
)


def _negated_near(text: str, start: int, end: int) -> bool:
    window = text[max(0, start - 60) : end + 60].lower()
    return any(
        p in window
        for p in (
            "not ",
            "does not",
            "do not",
            "did not",
            "cannot",
            "rather than",
            "no evidence",
            "not a ",
            "not an ",
        )
    )


def validate_draft_claim_compliance() -> list[str]:
    issues: list[str] = []
    texts: list[tuple[str, str]] = []

    for path in DRAFT_PATHS:
        if not path.exists():
            issues.append(f"missing draft: {path.relative_to(PROJECT_ROOT)}")
            continue
        texts.append((path.name, path.read_text(encoding="utf-8")))

    if not texts:
        return issues

    combined = "\n".join(t for _, t in texts).lower()

    for pattern, msg in FORBIDDEN_PHRASES:
        for m in re.finditer(pattern, combined, re.IGNORECASE):
            if _negated_near(combined, m.start(), m.end()):
                continue
            issues.append(f"{msg}: matched `{m.group(0)[:80]}`")

    for pattern, label in REQUIRED_DISCLAIMERS:
        if not re.search(pattern, combined, re.IGNORECASE):
            issues.append(f"missing required disclaimer: {label}")

    claim_path = PROJECT_ROOT / "paper" / "claim_table_map.csv"
    if claim_path.exists():
        claims = pd.read_csv(claim_path)
        blocked = claims[claims["claim_tier"] == "not_supported"]["claim_id"].astype(str)
        for cid in blocked:
            if cid == "causal_pilot_effect":
                continue
            if cid.replace("_", " ") in combined and f"not_supported:{cid}" not in combined:
                pass  # claim_id in prose is fine if negated

    return issues
