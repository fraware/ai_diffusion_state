# Submission readiness (PCS measurement paper)

**Git revision:** `ea0cd37-dirty`  
**PCS gates ready:** `True`  
**Submission package ready:** `True`  
**Geo evidence:** official=102, rule_based=357, external=50

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
| Cover letter draft | `paper/COVER_LETTER_DRAFT.md` (commit hash present) |
| Portal upload archive | `paper/submission_bundle.zip` (208,870 bytes; `make submission-zip`) |
| SHA256 manifest | `paper/SUBMISSION_MANIFEST.json` |
| Language + claim compliance | `make validate-submission` |

## Paper owner checklist

- [ ] Convert `paper/draft_v1_submission.md` to journal Word/LaTeX (`make submission-docx` if Pandoc installed)
- [ ] Author affiliations, acknowledgments, and journal formatting
- [ ] Upload `paper/submission_bundle.zip` to the journal portal
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
