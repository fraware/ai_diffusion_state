# Engineer next steps

**PCS measurement paper:** Engineering **closed**. See `docs/PCS_ENGINEERING_CLOSED.md`. Guard: `make pcs-guard`.

**Atlas true vision:** Active sprint — `docs/POST_PCS_TRUE_VISION_HANDOFF.md`, `make atlas-phase1`.

**One command:**

```powershell
make pcs
```

**Quick status:**

```powershell
python scripts/15_pcs_status.py --json
```

Reads `paper/pcs_gate_report.json`.

---

## Paper owner (active)

1. Draft from `paper/draft_v1.md` using **only** `paper/main_tables/` (Tables A–I).
2. After any pipeline rerun:

```powershell
make analysis
make public-fallback-controls
make main-tables
make sync-paper-stats
make validate-draft
make production-check
```

3. Submission package (engineering — run after pipeline changes):

```powershell
make paper-figures
make export-submission
make validate-submission
```

4. Remaining drafting work (paper owner):
   - Journal template conversion (`paper/draft_v1_submission.md` or `paper/draft_v1.tex`)
   - Paste numbered tables from `paper/main_tables/`
   - Author block and final citation formatting from `paper/references.bib`

## Atlas IIDS evidence (active)

**Critical path:** geography batch exports (Engineer A). See [ATLAS_IIDS_GEO_PROGRAM_STATUS.md](ATLAS_IIDS_GEO_PROGRAM_STATUS.md) and [ATLAS_IIDS_GEOGRAPHY_ENGINEER_RUNBOOK.md](ATLAS_IIDS_GEOGRAPHY_ENGINEER_RUNBOOK.md).

Control laptop:

```powershell
git pull
make atlas-iids-geography-preflight
python scripts/50_atlas_status.py --json
```

Sequence: Engineer A places 17 batch exports → Engineer B pilot (batch 001) → full concat/normalize/coverage → Engineer C `make atlas-iids-control-evidence-chain` → Engineer D regenerates paper from new tables only.

Do not weaken `atlas_evidence_ready` or claim publication-ready patent/F1 results until `ready_for_evidence_chain` is true.

---

## If EPS/NBS city controls arrive
python scripts/06a_validate_city_controls_raw.py
make city-controls
make panel
make analysis
make public-fallback-controls
make main-tables
make sync-paper-stats
make validate-draft
make pcs
```

Then update draft §8: strict Table 5 may replace appendix-only language if Model 4 is no longer skipped.

---

## Gate artifacts (traceability)

| File | Role |
|------|------|
| `paper/main_tables/*.csv` | Draft tables A–I |
| `paper/main_table_claim_map.csv` | Table → claim_id |
| `paper/claim_table_map.csv` | Claim → source script |
| `paper/pcs_gate_report.json` | Machine-readable PCS snapshot |
| `docs/model_interpretation_matrix.md` | What each table can support |
| `docs/PCS_GATE_CHECKLIST.md` | Full gate list |

---

## Do not claim (until new evidence)

- Causal pilot-zone treatment effects
- EPS-equivalent controls (Table I is appendix partial controls only)
- Full external audit of all 509 city assignments
- Export upgrading causality

See `paper/red_team_memo.md` and `docs/PUBLIC_FALLBACK_CONTROLS_INTERPRETATION.md`.
