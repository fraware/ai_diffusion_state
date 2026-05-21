# Sprint execution status

**Generated:** 2026-05-21 after descriptive production gate (human-input blockers unchanged).  
**Canonical blocker playbook:** [`docs/HUMAN_INPUT_BLOCKERS_ACTION_PLAN.md`](HUMAN_INPUT_BLOCKERS_ACTION_PLAN.md) (`e8f1695`).  
**Latest local gate:** `make purge-stub-controls` through `make test pcs-status` — exit 0; blockers A / B1 / B2 still pending.

## Final production gate results

| Step | Exit | Notes |
|------|-----:|-------|
| `purge-stub-controls` | 0 | No stub artifacts |
| `validate-controls-raw` | **1** | **BLOCKER:** only `city_controls_ingest_template.csv` in `data/raw/city_controls/` |
| `city-controls` | **1** | No production EPS/NBS files (templates excluded) |
| `apply-geo-updates` | 0 | 0 audit corrections; 0 external URLs applied |
| `geo-audit` | 0 | 509/509 resolved |
| `validate-geo` | 0 | Hygiene OK |
| `panel` / `analysis` | 0 | Descriptive + skipped controlled tables |
| `validate-audit` | **1** | 0/70 `auditor_decision` filled |
| `production-check` | 0 | No stub leakage in paper text |
| `validate-sprint` | 0 | PCS tables present |
| `test` | 0 | 48 passed, 1 skipped (2026-05-21) |
| `pcs-status` | 0 | Controls missing; audit 0/70; external 0/50 |

## Expected final state vs actual

| Criterion | Target | Actual |
|-----------|--------|--------|
| City controls | production | **missing** |
| Panel controls merged | yes | **no** |
| Geo hygiene | OK | **OK** |
| Audit validation | OK | **pending** (0/70) |
| External verified | >= 50 | **0** |
| Table 5 | real estimates | **skipped** |
| Table 7 | balance | **skipped** |
| Table 8 | matched | **skipped** |
| Table 17 | audit rates | pending |

## Engineer assignments (action required)

See **`docs/HUMAN_INPUT_BLOCKERS_ACTION_PLAN.md`** for exact columns, allowed values, rejected URLs, and per-workstream command blocks.

### Engineer A — BLOCKED (Workstream A)

Place **real** EPS/NBS export(s) in `data/raw/city_controls/` (not the template; do not commit proprietary downloads). Then run the Workstream A commands in the blocker action plan.

### Engineer B1 — BLOCKED (Workstream B1)

Fill `data/audit/city_resolution_sample_audit.csv` (≥50 `rule_based_text_inference` + ≥20 `official_location_exact`). Then `make apply-geo-updates`, `make recompute-audit`, `make validate-audit`.

### Engineer B2 — BLOCKED (Workstream B2)

Fill `external_evidence_url` (+ type, notes) on ≥50 rows in `data/interim/external_verification_queue.csv` (non-list, facility-level URLs only). Then `make apply-geo-updates`, `make geo-audit`, `make validate-geo`, and downstream tables.

### Engineer C — DONE (descriptive path)

- `outputs/tables/table_15_export_relevance_by_sector.csv` — from `make analysis` when BACI export data present  
- `paper/main_tables/table_G_export_relevance.csv` — from `make main-tables`  
- `docs/export_relevance_memo.md` — descriptive framing (no causal claims)

### Engineer D — DONE (template)

- `docs/model_interpretation_matrix.md` — interpretive matrix; rerun after A/B complete for numeric examples

### Paper owner

Draft from `paper/main_tables/` only. **Do not** cite Table 5–8 or externally verified geo until A/B gates pass. Core thesis: hub-centered diffusion architecture, not uniform pilot treatment.
