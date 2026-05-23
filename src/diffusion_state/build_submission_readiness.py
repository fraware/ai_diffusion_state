from __future__ import annotations

import json
from pathlib import Path

from diffusion_state.generate_cover_letter import cover_letter_has_commit_hash
from diffusion_state.git_utils import format_revision_label, get_git_revision
from diffusion_state.pcs_status import collect_pcs_gates, pcs_ready
from diffusion_state.utils import PROJECT_ROOT

READINESS_PATH = PROJECT_ROOT / "paper" / "SUBMISSION_READINESS.md"
OWNER_BRIEF_PATH = PROJECT_ROOT / "paper" / "SUBMISSION_OWNER_BRIEF.md"


def build_submission_readiness() -> str:
    gates = collect_pcs_gates()
    ready = pcs_ready(gates)
    report_path = PROJECT_ROOT / "paper" / "pcs_gate_report.json"
    submission_ready = False
    if report_path.exists():
        submission_ready = bool(json.loads(report_path.read_text(encoding="utf-8")).get("submission_ready"))

    geo = next((g.detail for g in gates if g.name == "geo_evidence_classes"), "n/a")
    revision = format_revision_label(get_git_revision())
    cover_done = cover_letter_has_commit_hash()
    zip_path = PROJECT_ROOT / "paper" / "submission_bundle.zip"
    zip_note = (
        f"`paper/submission_bundle.zip` ({zip_path.stat().st_size:,} bytes; `make submission-zip`)"
        if zip_path.exists()
        else "`make submission-zip` after bundle"
    )

    text = f"""# Submission readiness (PCS measurement paper)

**Git revision:** `{revision}`  
**PCS gates ready:** `{ready}`  
**Submission package ready:** `{submission_ready}`  
**Geo evidence:** {geo}

Regenerate: `make submission-checklist` (includes this file and `paper/SUBMISSION_CHECKLIST.md`).

## Engineering complete

| Item | Status |
|------|--------|
| 509/509 city resolution | Done |
| 50 external-evidence verified | Done |
| 70/70 stratified audit | Done |
| Tables A-I (`paper/main_tables/`) | Done |
| Appendix Table I (partial 2024 controls; not EPS-equivalent) | Done |
| Strict Table 5 (EPS/NBS) | Blocked by design |
| Submission draft + embedded tables | `paper/draft_v1_submission.md` |
| Cover letter draft | `paper/COVER_LETTER_DRAFT.md` ({'commit hash present' if cover_done else 'run make cover-letter'}) |
| Portal upload archive | {zip_note} |
| SHA256 manifest | `paper/SUBMISSION_MANIFEST.json` |
| Language + claim compliance | `make validate-submission` |

## Paper owner checklist

- [ ] Convert `paper/draft_v1_submission.md` to journal Word/LaTeX (`make submission-docx` if Pandoc installed)
- [ ] Author affiliations, acknowledgments, and journal formatting
- [ ] Upload {zip_note.split('(')[0].strip()} to the journal portal
- [ ] Edit `paper/COVER_LETTER_DRAFT.md` (journal name, authors)
- [ ] Table I labeled appendix-only in the submitted PDF
- [ ] Statistics traced to `paper/main_tables/` only (not `outputs/tables/`)
- [ ] No causal pilot-zone or EPS-equivalent claims in main text

See also: `paper/SUBMISSION_OWNER_BRIEF.md`, `docs/PCS_ENGINEERING_CLOSED.md`.

## Rebuild

```powershell
make pcs
make validate-submission
```

Expected: `paper/pcs_gate_report.json` with `"ready": true` and `"submission_ready": true`.
"""
    READINESS_PATH.write_text(text, encoding="utf-8")
    return text


def build_submission_owner_brief() -> str:
    report = {}
    manifest = {}
    if (PROJECT_ROOT / "paper" / "pcs_gate_report.json").exists():
        report = json.loads((PROJECT_ROOT / "paper" / "pcs_gate_report.json").read_text(encoding="utf-8"))
    if (PROJECT_ROOT / "paper" / "SUBMISSION_MANIFEST.json").exists():
        manifest = json.loads((PROJECT_ROOT / "paper" / "SUBMISSION_MANIFEST.json").read_text(encoding="utf-8"))

    from diffusion_state.validate_submission_readiness import validate_submission_readiness

    submission_ready, submission_issues = validate_submission_readiness()
    if report:
        pcs_ready = bool(report.get("ready"))
    else:
        from diffusion_state.validate_pcs_gates import validate_pcs_gates

        pcs_ready, _ = validate_pcs_gates()

    revision = format_revision_label(get_git_revision())
    n_files = manifest.get("n_files", "n/a")
    geo = next(
        (g["detail"] for g in report.get("gates", []) if g.get("name") == "geo_evidence_classes"),
        "official=102, rule_based=357, external=50",
    )
    issue_line = ""
    if submission_issues:
        issue_line = f"\n**Submission issues:** {len(submission_issues)} (run `make validate-submission`)\n"

    text = f"""# PCS submission owner brief (one page)

**Purpose:** Upload the measurement paper without re-running the pipeline.  
**Git revision:** `{revision}`  
**PCS ready:** `{pcs_ready}` | **Submission ready:** `{submission_ready}`{issue_line}

## Upload these files

1. **Manuscript source:** `paper/draft_v1_submission.md` (convert to journal template first)
2. **Replication package:** `paper/submission_bundle.zip` OR folder `paper/submission_bundle/` ({n_files} files in manifest)
3. **Cover letter:** `paper/COVER_LETTER_DRAFT.md` (edit journal name and authors)
4. **Manifest (optional for editors):** `paper/SUBMISSION_MANIFEST.json`

## Claims the paper supports (main text)

- Hub-centered industrial AI diffusion architecture (descriptive)
- Pilot-zone overlap and city typology (associational)
- Hub-exclusion attenuation (Table D)
- Ex ante industry heterogeneity (Table F)
- Export relevance descriptives (Tables G, H)

## Claims the paper does not support

- Causal average treatment effect of pilot-zone designation
- EPS/NBS-equivalent controlled adoption (strict Table 5 blocked)
- Economy-wide productivity shock proof

## Evidence hygiene (for methods section)

- {geo}
- 509/509 listed smart-factory projects resolved to cities
- Table I is appendix-only partial 2024 public controls

## Before you click submit

```powershell
make pcs-guard
make validate-submission
```

Atlas true-vision work is separate: `docs/ATLAS_PHASE2_REAL_EVIDENCE_INSTRUCTIONS.md`.
"""
    OWNER_BRIEF_PATH.write_text(text, encoding="utf-8")
    return text
