"""Block publication claims in draft text when IIDS geography evidence is incomplete."""
from __future__ import annotations

from pathlib import Path

from diffusion_state.iids_geography_gate import collect_iids_geography_gate
from diffusion_state.utils import PROJECT_ROOT

DRAFT_ATLAS = PROJECT_ROOT / "paper" / "draft_atlas_v1.md"

# (phrase, flag) — matched case-insensitively; skip if negated with "not " prefix on first word
PATENT_EMPIRICAL_CLAIMS = (
    ("publication-ready f1", "premature_f1_publication_claim"),
    ("publication ready f1", "premature_f1_publication_claim"),
    ("publication-ready patent", "premature_f1_publication_claim"),
    ("publication ready patent", "premature_f1_publication_claim"),
    ("atlas patent evidence chain is publication-ready", "premature_patent_evidence_claim"),
    ("atlas evidence chain is publication-ready", "premature_patent_evidence_claim"),
    ("evidence chain is publication-ready", "premature_patent_evidence_claim"),
    ("pilot zones are associated with stronger industrial ai patenting", "premature_pilot_patent_association"),
    ("pilot zones associated with stronger industrial ai patenting", "premature_pilot_patent_association"),
    ("pilot-zone x ai-exposure", "premature_pilot_patent_association"),
    ("pilot zone x ai exposure", "premature_pilot_patent_association"),
    ("pilot-zone × ai-exposure", "premature_pilot_patent_association"),
    ("pilot-zone x patent causal", "premature_pilot_patent_association"),
    ("pilot zones caused stronger industrial ai patenting", "premature_pilot_patent_association"),
    ("pilot zones cause stronger industrial ai patenting", "premature_pilot_patent_association"),
    ("stronger industrial ai patenting in ai-exposed industries", "premature_pilot_patent_association"),
    ("strict eps/nbs controls pass", "premature_eps_controls_claim"),
    ("strict eps/nbs control pass", "premature_eps_controls_claim"),
    ("eps/nbs controls pass", "premature_eps_controls_claim"),
    ("exact publication-number geocoding", "premature_exact_geocoding_claim"),
    ("exact publication number geocoding", "premature_exact_geocoding_claim"),
    ("exact applicant-address geocoding", "premature_exact_geocoding_claim"),
    ("exact geocoding of all", "premature_exact_geocoding_claim"),
    ("publication-number applicant-address geocoding", "premature_exact_geocoding_claim"),
    ("coef=-0.0207", "stale_f1_coefficient_language"),
    ("coef = -0.0207", "stale_f1_coefficient_language"),
)


def _phrase_present(text: str, phrase: str) -> bool:
    start = 0
    while True:
        idx = text.find(phrase, start)
        if idx < 0:
            return False
        window = text[max(0, idx - 48) : idx]
        negated = any(
            marker in window
            for marker in (
                "not ",
                "do not ",
                "does not ",
                "forbid",
                "forbidden",
                "blocked",
                "must not",
                "cannot ",
                "can't ",
            )
        )
        if not negated:
            return True
        start = idx + len(phrase)


def collect_draft_patent_claim_violations(
    *,
    draft_path: Path | None = None,
    geography_gate: dict | None = None,
) -> list[str]:
    """Forbidden phrasing in draft while ready_for_evidence_chain is false."""
    gate = geography_gate or collect_iids_geography_gate()
    if gate.get("ready_for_evidence_chain"):
        return []

    draft_path = draft_path or DRAFT_ATLAS
    if not draft_path.exists():
        return []

    text = draft_path.read_text(encoding="utf-8").lower()
    text = text.replace("×", "x").replace("–", "-").replace("—", "-")
    for ch in "*_`":
        text = text.replace(ch, "")
    flags: list[str] = []
    for phrase, flag in PATENT_EMPIRICAL_CLAIMS:
        if _phrase_present(text, phrase):
            flags.append(flag)
    return sorted(set(flags))


def collect_premature_patent_claim_flags(
    *,
    draft_path: Path | None = None,
    geography_gate: dict | None = None,
) -> list[str]:
    """Draft violations plus gate meta-flags for atlas_status / forbidden_claim_flags."""
    gate = geography_gate or collect_iids_geography_gate()
    flags = collect_draft_patent_claim_violations(
        draft_path=draft_path,
        geography_gate=gate,
    )
    if gate.get("ready_for_evidence_chain"):
        return []
    if not gate.get("iids_geography_ready"):
        flags.append("geography_not_ready")
    if not gate.get("ready_for_evidence_chain"):
        flags.append("evidence_chain_not_ready")
    return sorted(set(flags))


def assert_no_premature_patent_claims(
    *,
    draft_path: Path | None = None,
    geography_gate: dict | None = None,
) -> None:
    flags = collect_draft_patent_claim_violations(
        draft_path=draft_path,
        geography_gate=geography_gate,
    )
    if flags:
        raise AssertionError(f"premature patent claims in draft: {', '.join(flags)}")
