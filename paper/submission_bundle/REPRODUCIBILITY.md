# Reproducibility statement (PCS measurement paper)

## One-command rebuild

```powershell
make pcs
```

This runs the full measurement pipeline, syncs paper memos, builds Tables A–I, exports the submission draft, and writes `paper/pcs_gate_report.json`.

## Submission-only rebuild

```powershell
make paper-figures
make paper-tables
make export-submission
make submission-bundle
make validate-submission
python scripts/15_pcs_status.py --json
```

## Expected gate state

- `ready: true` — geo, audit, external verification, main tables
- `submission_ready: true` — figures, embedded tables, bibliography, language gates

## Software

- Python >= 3.10
- Install: `pip install -e .[dev]`
- See `pyproject.toml` for pinned dependencies

## Data not in repository

- CEPII BACI export files (optional; `make baci`)
- EPS/NBS city controls (strict Table 5 blocked until provided)
- CNIPA full patent microdata (Atlas sprint; not required for PCS paper)

## Primary artifacts for reviewers

| Artifact | Role |
|----------|------|
| `paper/draft_v1_submission.md` | Full draft with embedded tables and figures |
| `paper/main_tables/table_*.csv` | Draft-facing Tables A–I |
| `paper/claim_table_map.csv` | Claim tier traceability |
| `paper/pcs_gate_report.json` | Machine-readable gate snapshot |

## Commit hash

Record the git commit used for submission in the journal cover letter. Build manifest: `paper/SUBMISSION_MANIFEST.json`.
