"""Block publication claims in draft text when IIDS geography evidence is incomplete."""
from __future__ import annotations

from pathlib import Path

from diffusion_state.iids_geography_gate import collect_iids_geography_gate
from diffusion_state.utils import PROJECT_ROOT

DRAFT_ATLAS = PROJECT_ROOT / "paper" / "draft_atlas_v1.md"

# Phrases that imply empirical patent geography results without a grounded city-year panel.
PATENT_EMPIRICAL_CLAIMS = (
    ("publication-ready f1", "premature_f1_publication_claim"),
    ("publication ready f1", "premature_f1_publication_claim"),
    ("atlas patent evidence chain is publication-ready", "premature_patent_evidence_claim"),
    ("atlas evidence chain is publication-ready", "premature_patent_evidence_claim"),
    ("pilot zones are associated with stronger industrial ai patenting", "premature_pilot_patent_association"),
    ("pilot-zone x ai-exposure", "premature_pilot_patent_association"),
    ("stronger industrial ai patenting in ai-exposed industries", "premature_pilot_patent_association"),
    ("coef=-0.0207", "stale_f1_coefficient_language"),
)


def collect_premature_patent_claim_flags(
    *,
    draft_path: Path | None = None,
    geography_gate: dict | None = None,
) -> list[str]:
    """Return flags when draft asserts patent results before geography gate passes."""
    gate = geography_gate or collect_iids_geography_gate()
    if gate.get("ready_for_evidence_chain"):
        return []

    draft_path = draft_path or DRAFT_ATLAS
    if not draft_path.exists():
        return []

    text = draft_path.read_text(encoding="utf-8").lower()
    flags: list[str] = []
    for phrase, flag in PATENT_EMPIRICAL_CLAIMS:
        if phrase in text and f"not {phrase.split()[0]}" not in text:
            flags.append(flag)
    if not gate.get("iids_geography_ready"):
        flags.append("geography_not_ready")
    return sorted(set(flags))
