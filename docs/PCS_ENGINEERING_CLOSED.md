# PCS engineering — closed

**Status:** Measurement-paper engineering is **frozen** as of the submission package in commit `248b4a5` and follow-on gates. Do not add submission-bundle features, claim-compliance scripts, or checklist refinements unless the paper owner requests a specific formatting fix.

**True-vision work:** See `docs/POST_PCS_TRUE_VISION_HANDOFF.md` and `make atlas-phase1`.

## Guard command (run before any geo/analysis change)

```powershell
make pcs-guard
```

Equivalent:

```powershell
python scripts/15_pcs_status.py --json
```

Expected in `paper/pcs_gate_report.json`:

```json
"ready": true,
"submission_ready": true
```

## Full rebuild (only if pipeline inputs change)

```powershell
make pcs
make validate-submission
```

## Engineering deliverables (complete)

| Deliverable | Path |
|-------------|------|
| Draft | `paper/draft_v1.md` |
| Submission draft (tables + figures) | `paper/draft_v1_submission.md` |
| Tables A–I | `paper/main_tables/` |
| Gate report | `paper/pcs_gate_report.json` |
| Submission bundle + SHA256 manifest | `paper/submission_bundle/`, `paper/SUBMISSION_MANIFEST.json` |
| Checklist | `paper/SUBMISSION_CHECKLIST.md` |
| Reproducibility / data availability | `paper/REPRODUCIBILITY.md`, `paper/DATA_AVAILABILITY.md` |
| Cover letter draft | `paper/COVER_LETTER_DRAFT.md` (`make cover-letter`; includes git commit) |
| Portal zip | `paper/submission_bundle.zip` (`make submission-zip`) |

## Paper owner only (not engineering)

- Journal Word/LaTeX template and author block
- Final proofread and citation formatting
- Cover letter edits and journal portal upload
- Optional: `make submission-docx` if Pandoc is installed

## Forbidden engineering changes

- Weakening geo gates (509/509, 50 external, 70/70 audit)
- Moving Table I to main text as EPS-equivalent controls
- Claiming causal pilot-zone effects in automated draft checks
