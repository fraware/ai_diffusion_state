# PCS submission checklist (auto-generated)

**PCS gates ready:** `True`
**Submission package ready:** `True`

Regenerate: `make submission-checklist` after `make pcs`.

## Engineering gates

- [x] **city_resolution** — 509/509 projects resolved (0 unknown)
- [x] **geo_evidence_hygiene** — OK
- [x] **external_verification** — 50 external_evidence_verified (target >= 50)
- [x] **geo_evidence_classes** — official=102, rule_based=357, external=50
- [x] **audit_sample** — 70/70 auditor_decision filled
- [x] **external_verification_queue** — 50/50 queue rows with external_evidence_url
- [x] **paper_main_tables** — 10/10 tables present
- [x] **sprint_core_tables** — 8/8 core tables
- [x] **strict_table_5** — skipped by design (expected until EPS/NBS)
- [x] **appendix_table_i** — Table I OLS count: pilot_zone coef=1.58, p=0.020, N=51, R2=0.52 (appendix only; not EPS-equivalent)
- [x] **city_controls_source** — source=production; panel merged adoption-year controls: no (expected for public fallback path)
- [x] **paper_figures** — main-text figures synced to paper/figures/
- [x] **references_bib** — paper/references.bib (14 entries)
- [x] **submission_draft_export** — draft_v1_submission.md present
- [x] **paper_tables_embedded** — Tables A–I markdown built in paper/tables_md/
- [x] **submission_tables_in_draft** — draft_v1_submission.md includes embedded tables
- [x] **submission_bundle** — paper/submission_bundle/ assembled
- [x] **draft_claim_compliance** — OK
- [x] **cover_letter_draft** — COVER_LETTER_DRAFT.md with git commit
- [x] **submission_manifest_revision** — manifest git_revision_short=49a6b6c
- [x] **submission_zip** — submission_bundle.zip (208,878 bytes)

## Paper owner (manual)

- [ ] Journal template applied (`paper/draft_v1_submission.md` → Word/LaTeX)
- [ ] Author affiliations and acknowledgments
- [ ] Table/figure numbering matches journal style
- [x] Cover letter cites git commit (`paper/COVER_LETTER_DRAFT.md`)
- [ ] Upload `paper/submission_bundle.zip` or folder to journal portal
- [ ] Table I labeled appendix-only in submitted PDF
- [ ] No strict Table 5 in main text unless EPS/NBS ingested

## Rebuild

```powershell
make pcs
make validate-submission
```
