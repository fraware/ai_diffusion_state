from __future__ import annotations

import json
from pathlib import Path

from diffusion_state.git_utils import format_revision_label, get_git_revision
from diffusion_state.utils import PROJECT_ROOT

OUT_PATH = PROJECT_ROOT / "paper" / "COVER_LETTER_DRAFT.md"
PCS_REPORT = PROJECT_ROOT / "paper" / "pcs_gate_report.json"
PLACEHOLDER_COMMIT = "[Git commit hash at submission]"


def generate_cover_letter() -> str:
    report = {}
    if PCS_REPORT.exists():
        report = json.loads(PCS_REPORT.read_text(encoding="utf-8"))

    ready = report.get("ready", True)
    sub_ready = report.get("submission_ready", True)
    gates = {g["name"]: g for g in report.get("gates", [])}

    geo = gates.get("geo_evidence_classes", {}).get("detail", "102 official, 357 rule-based, 50 external")
    table_i = gates.get("appendix_table_i", {}).get("detail", "Table I appendix partial controls")
    revision = get_git_revision()
    commit_label = format_revision_label(revision)
    dirty_note = " (working tree has uncommitted changes)" if revision.get("dirty") else ""

    text = f"""# Cover letter draft (PCS measurement paper)

**Regenerate:** `make cover-letter` after `make pcs`.

---

Dear Editor,

We submit our manuscript on China's hub-centered industrial AI adoption architecture, linking national AI pilot zones to Ministry of Industry and Information Technology excellence-level smart-factory recognition.

**Data and measurement.** We construct a reproducible dataset of 17 AI pilot-zone units and 509 listed smart-factory projects (2024–2025), with evidence-classified city assignment ({geo}). A stratified audit supports the resolution protocol. This is not a claim that all assignments are externally audited.

**Empirical contribution.** The paper documents strong descriptive overlap between pilot-zone geography and listed smart-factory recognition, then shows that the association attenuates when major hubs and direct-admin municipalities are removed—consistent with a hub-centered diffusion architecture rather than a uniform treatment effect. We do not estimate a causal average treatment effect of pilot-zone designation.

**Robustness.** Appendix Table I reports partial 2024 public city controls ({table_i}). Strict EPS/NBS controlled specifications remain unavailable by design until licensed city economic controls are ingested.

**Replication.** Engineering gates: PCS ready={ready}, submission package ready={sub_ready}. Replication package: `paper/submission_bundle/` (or `paper/submission_bundle.zip`) with manifest `paper/SUBMISSION_MANIFEST.json`. Rebuild: `make pcs` at git commit `{commit_label}`{dirty_note}.

We believe the paper fits [JOURNAL NAME] because it offers a measurement framework for industrial AI diffusion distinct from frontier-model capability rankings.

Sincerely,

[Author names and affiliations]

Git commit: `{commit_label}`{dirty_note}
"""
    return text


def cover_letter_has_commit_hash(text: str | None = None) -> bool:
    body = text if text is not None else (OUT_PATH.read_text(encoding="utf-8") if OUT_PATH.exists() else "")
    return PLACEHOLDER_COMMIT not in body and "Git commit:" in body


def write_cover_letter(path: Path | None = None) -> Path:
    path = path or OUT_PATH
    path.write_text(generate_cover_letter(), encoding="utf-8")
    return path
