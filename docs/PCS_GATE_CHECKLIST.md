# PCS gate checklist

Production-check sprint (PCS) gates for the hub-centered measurement paper. Run after any geo, controls, or analysis change.

## One-command gate chain

```powershell
make pcs
```

Equivalent steps:

```powershell
make purge-stub-controls
make geo-audit
make validate-geo
make panel
make analysis
make public-fallback-controls
make main-tables
make sync-paper-stats
make production-check
make validate-draft
make validate-sprint
python scripts/15_pcs_status.py
```

## Expected pass state (2026-05-22 build)

| Gate | Expected |
|------|----------|
| City resolution | 509/509, 0 unknown |
| Geo evidence hygiene | OK |
| External verification | >= 50 projects (`external_evidence_verified`) |
| Audit sample | 70/70 `auditor_decision` filled |
| External verification queue | 50/50 non-list URLs |
| Paper main tables | 10 CSV files (Tables A–I) |
| Strict Table 5 | Skipped by design |
| Appendix Table I | Present; OLS/log pilot positive; Poisson n.s. |
| Panel EPS controls merged | No (public fallback path) |

## Paper-facing artifacts (Priority 3)

After gates pass, numbers in the draft must come from:

- `paper/main_tables/` only (Tables A–I)
- `make sync-paper-stats` to refresh `paper/results_memo.md`, `paper/reviewer_results_snapshot.md`, `paper/red_team_memo.md`
- `paper/claim_table_map.csv` for claim tiers
- `docs/model_interpretation_matrix.md` for what each table can support

## Allowed main-text claims

- Hub-centered diffusion architecture
- Pilot-zone overlap and typology (descriptive / associational)
- Hub-exclusion attenuation (Table D / 6)
- Ex ante industry heterogeneity (Table F)
- Export relevance descriptives (Tables G, H)

## Appendix only

- Table I (`table_I_appendix_public_fallback_controls.csv`): partial 2024 ChinaUTC controls; not EPS-equivalent

## Forbidden until EPS/NBS

- Strict Table 5 controlled adoption
- Tables 7–8 balance/matching as primary evidence
- Causal pilot-zone treatment effects
- "EPS/NBS model supports the association"

## Submission package (Priority 4 — engineering)

After core gates pass:

```powershell
make paper-figures
make paper-tables
make export-submission
make cover-letter
make submission-bundle
make submission-zip
make validate-submission
```

| Artifact | Role |
|----------|------|
| `paper/figures/fig_1_*.png`, `fig_2_*.png` | Main-text figures (synced from `outputs/figures/`) |
| `paper/figure_manifest.json` | Figure → claim_id traceability |
| `paper/references.bib` | BibTeX for conversion |
| `paper/citation_map.csv` | Section → citation keys |
| `paper/tables_md/*.md` | Markdown renditions of Tables A–I |
| `paper/table_manifest.json` | Table → claim_id traceability |
| `paper/draft_v1_submission.md` | Draft + embedded tables + figures + reference index |
| `paper/draft_v1.tex` | Minimal LaTeX scaffold |
| `paper/COVER_LETTER_DRAFT.md` | Gate-aware cover letter with git commit |
| `paper/submission_bundle.zip` | Portal upload archive (`make submission-zip`) |

`paper/pcs_gate_report.json` includes `submission_ready` when `make validate-submission` passes.

Engineering freeze: `docs/PCS_ENGINEERING_CLOSED.md`.

## Quick status

```powershell
python scripts/15_pcs_status.py --json
```

Writes `paper/pcs_gate_report.json` and prints a human-readable dashboard.

Exit code 0 = all blocking PCS gates pass and `main_table_claim_map` is aligned with `claim_table_map`.

## Traceability

| Artifact | Purpose |
|----------|---------|
| `paper/main_tables/*.csv` | Draft-facing tables A–I |
| `paper/main_table_claim_map.csv` | Table → claim_id mapping |
| `paper/claim_table_map.csv` | Claim → source artifact |
| `paper/pcs_gate_report.json` | Machine-readable gate snapshot |
