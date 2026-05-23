# Submission readiness (PCS measurement paper)

**Build date:** Regenerate with `make pcs` and `make validate-submission`.  
**Gate report:** `paper/pcs_gate_report.json` — `ready` (PCS gates) and `submission_ready` (full package).

## Engineering complete

| Item | Status | Command |
|------|--------|---------|
| 509/509 city resolution | Done | `make pcs` |
| 50 external-evidence verified | Done | `make pcs` |
| 70/70 stratified audit | Done | `make validate-audit` |
| Tables A–I in `paper/main_tables/` | Done | `make main-tables` |
| Hub-exclusion + typology + ex ante exposure | Done | `make analysis` |
| Appendix Table I (partial 2024 controls) | Done | `make public-fallback-controls` |
| Strict Table 5 (EPS/NBS) | Blocked by design | — |
| Draft number cross-check | Done | `make validate-draft` |
| Main-text figures (timing + typology) | Done | `make paper-figures` |
| Tables A–I embedded in submission draft | Done | `make paper-tables` |
| BibTeX + citation map | Done | `paper/references.bib`, `paper/citation_map.csv` |
| Submission draft export | Done | `make export-submission` |
| Language + package validation | Done | `make validate-submission` |
| Claim-tier language compliance | Done | `validate_draft_claim_compliance` |
| Submission bundle (42 files + SHA256 manifest) | Done | `make submission-bundle` |
| Reproducibility + data availability statements | Done | `paper/REPRODUCIBILITY.md`, `paper/DATA_AVAILABILITY.md` |
| Auto submission checklist | Done | `make submission-checklist` |
| CI PCS gate chain | Done | `.github/workflows/ci.yml` |

## Paper owner checklist

- [ ] All statistics traced to `paper/main_tables/` (not `outputs/tables/` directly)
- [ ] Claim tiers respected (`paper/claim_table_map.csv`)
- [ ] No causal pilot-zone or export-effect language (run `make validate-submission`)
- [ ] Table I labeled appendix / not EPS-equivalent
- [ ] Geo language: 102 official, 357 rule-based, 50 external (not "fully audited")
- [x] Citations scaffolded (`paper/references.bib`; inline keys in `draft_v1.md`)
- [x] Tables A–I embedded in `paper/draft_v1_submission.md` (summaries for large panels)
- [ ] LaTeX/Word conversion in journal template (`paper/draft_v1.tex` is a scaffold only)
- [ ] Author block, acknowledgments, and journal formatting

## Forbidden main-text claims

See `docs/model_interpretation_matrix.md` and `paper/red_team_memo.md` §11.

## Rebuild before submission

```powershell
make pcs
make paper-figures
make paper-tables
make export-submission
make submission-bundle
make submission-checklist
make validate-submission
python scripts/15_pcs_status.py --json
```

Expected JSON: `"ready": true`, `"submission_ready": true`.
