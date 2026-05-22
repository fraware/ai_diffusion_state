# Sprint execution status

**Updated:** 2026-05-22 — Workstream A closed (public appendix path). **Critical path: B1 + B2.**

**Canonical priorities:** [`docs/CURRENT_SPRINT_PRIORITIES.md`](CURRENT_SPRINT_PRIORITIES.md)  
**Blocker playbook:** [`docs/HUMAN_INPUT_BLOCKERS_ACTION_PLAN.md`](HUMAN_INPUT_BLOCKERS_ACTION_PLAN.md)  
**Table I interpretation:** [`docs/PUBLIC_FALLBACK_CONTROLS_INTERPRETATION.md`](PUBLIC_FALLBACK_CONTROLS_INTERPRETATION.md)

## Workstream status

| Workstream | Status | Notes |
|------------|--------|-------|
| **A — Strict EPS/NBS controls** | **Closed** (public limit reached) | Strict Table 5 **skipped** by design. Table I / 5b appendix robustness **done**. |
| **A — EPS/NBS (if later)** | Blocked on human export | Rerun controls pipeline only when real EPS/NBS files arrive. |
| **B1 — Audit sample** | **Pending** | 0/70 `auditor_decision` filled; `validate-audit` fails |
| **B2 — External verification** | **Pending** | 0/50 `external_evidence_url` filled |
| **Descriptive + geo** | **OK** | 509/509 cities; hygiene OK; `production-check` OK |
| **Table I (5b)** | **Done** | `paper/main_tables/table_I_appendix_public_fallback_controls.csv` |

## Latest gates (descriptive + appendix)

| Step | Status |
|------|--------|
| `geo-audit` / `validate-geo` | OK |
| `production-check` | OK |
| `public-fallback-controls` | OK → Table 5b |
| `main-tables` | OK (10 tables incl. Table I) |
| `validate-audit` | **Fails** until B1 complete |
| Strict Table 5 / panel merged | **Skipped / no** (expected) |

## Engineer assignments

### Engineer A — Done (no further ChinaUTC work)

Public ChinaUTC path complete. Do not scrape further unless FDI or fixed-asset investment tables appear. See `CURRENT_SPRINT_PRIORITIES.md`.

### Engineer B — Critical path

1. **B1:** `data/audit/city_resolution_sample_audit.csv` (≥50 rule-based + ≥20 official)  
2. **B2:** `data/interim/external_verification_queue.csv` (≥50 facility-level URLs)  
3. Memos: `docs/DEEP_RESEARCH_A_B2_*.md`

### Engineer C — Appendix documentation

Table I wording + export relevance descriptives. No causal export claims.

### Engineer D — After B1/B2

```powershell
make geo-audit validate-geo panel analysis public-fallback-controls main-tables paper production-check validate-sprint
python scripts/15_pcs_status.py
```

Then refresh `docs/model_interpretation_matrix.md`.

### Paper owner — Draft now

Use `paper/main_tables/`. Hub-centered measurement paper; appendix Table I; no strict Table 5 or causal pilot claims until gates pass.
