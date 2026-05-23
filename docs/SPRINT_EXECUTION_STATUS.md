# Sprint execution status

**Updated:** 2026-05-22 — **PCS sprint closed** (full gate chain + Priority 3 paper artifacts). Atlas patent pipeline landed separately. B1 + B2 complete.

**Canonical priorities:** [`docs/CURRENT_SPRINT_PRIORITIES.md`](CURRENT_SPRINT_PRIORITIES.md)  
**Blocker playbook:** [`docs/HUMAN_INPUT_BLOCKERS_ACTION_PLAN.md`](HUMAN_INPUT_BLOCKERS_ACTION_PLAN.md)  
**Table I interpretation:** [`docs/PUBLIC_FALLBACK_CONTROLS_INTERPRETATION.md`](PUBLIC_FALLBACK_CONTROLS_INTERPRETATION.md)

## Workstream status

| Workstream | Status | Notes |
|------------|--------|-------|
| **Atlas A — Industrial AI patents** | **Pipeline ready** | `make patents`; needs CNIPA microdata in `data/raw/patents/`. CSET auto-fetch for validation only. |
| **A — Strict EPS/NBS controls** | **Closed** (public limit reached) | Strict Table 5 **skipped** by design. Table I / 5b appendix robustness **done**. |
| **A — EPS/NBS (if later)** | Blocked on human export | Rerun controls pipeline only when real EPS/NBS files arrive. |
| **B1 — Audit sample** | **Done** | 70/70 decisions; `validate-audit` OK; Table 17 |
| **B2 — External verification** | **Done** | 50/50 non-list URLs; Table 16 `external_evidence_verified` |
| **Descriptive + geo** | **OK** | 509/509 cities; hygiene OK; `production-check` OK |
| **Table I (5b)** | **Done** | `paper/main_tables/table_I_appendix_public_fallback_controls.csv` |

## Latest gates (descriptive + appendix)

| Step | Status |
|------|--------|
| `geo-audit` / `validate-geo` | OK |
| `production-check` | OK |
| `public-fallback-controls` | OK → Table 5b |
| `main-tables` | OK (10 tables incl. Table I) |
| `validate-audit` | OK |
| `validate-sprint` | OK |
| Strict Table 5 / panel merged | **Skipped / no** (expected) |

## Engineer assignments

### Engineer A — Done (no further ChinaUTC work)

Public ChinaUTC path complete. Do not scrape further unless FDI or fixed-asset investment tables appear. See `CURRENT_SPRINT_PRIORITIES.md`.

### Engineer B — Done

B1 audit + B2 external verification applied; queue synced from seed via `scripts/29_apply_b2_research_to_queue.py`.

### Engineer C — Appendix documentation

Table I wording + export relevance descriptives. No causal export claims.

### Engineer D — Done (2026-05-22)

```powershell
make geo-audit validate-geo panel analysis public-fallback-controls main-tables paper production-check validate-sprint
python scripts/15_pcs_status.py
```

Then refresh `docs/model_interpretation_matrix.md`.

### Paper owner — Draft now

Use `paper/main_tables/` (Tables A–I). Hub-centered measurement paper; appendix Table I; no strict Table 5 or causal pilot claims. Gates pass: `python scripts/15_pcs_status.py`.

### Priority 3 — Paper-facing updates (done)

- `paper/results_memo.md`, `paper/red_team_memo.md`, `paper/reviewer_results_snapshot.md` synced via `make sync-paper-stats`
- `paper/claim_table_map.csv` and `paper/main_table_claim_map.csv` (Tables A–I traceability)
- `paper/draft_v1.md` hub-centered measurement draft
- `paper/pcs_gate_report.json` via `make pcs-status`
- `docs/model_interpretation_matrix.md` and `docs/PCS_GATE_CHECKLIST.md` updated
- `validate-sprint` enforces PCS blocking gates via `validate_pcs_gates.py`
- `validate-draft` cross-checks `paper/draft_v1.md` statistics against output tables
- `paper/SUBMISSION_READINESS.md` paper-owner checklist
- CI runs full PCS chain (`.github/workflows/ci.yml`)
