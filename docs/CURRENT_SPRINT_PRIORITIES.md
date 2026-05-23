# Current Sprint Priorities

**Status (2026-05-22):** PCS measurement sprint **closed**. All blocking gates pass. Paper draft (`paper/draft_v1.md`) is grounded in `paper/main_tables/` Tables A–I.

**Gate check:** `make pcs` or `python scripts/15_pcs_status.py --json`

## Workstream A — Closed (public path complete)

**Delivered:**

- `paper/main_tables/table_I_appendix_public_fallback_controls.csv` (from `table_5b_public_fallback_controls.csv`)
- `docs/PUBLIC_FALLBACK_CONTROLS_INTERPRETATION.md`

**Usable as:** appendix robustness only.

**Not usable as:** strict EPS/NBS controlled evidence (no FDI or fixed-asset investment in the public bundle; 51 complete 2024 observations).

**Engineer instruction:** Do not expand ChinaUTC scraping unless a new source contains FDI or fixed-asset investment.

**If EPS/NBS becomes available later:**

```powershell
make purge-stub-controls
python scripts/06a_validate_city_controls_raw.py
make city-controls
make panel
make analysis
make production-check
python scripts/15_pcs_status.py
```

## Priority 1 — Engineer B1: City-resolution audit — Done

70/70 `auditor_decision` filled; `make validate-audit` passes.

## Priority 2 — Engineer B2: External verification — Done

50/50 non-list `external_evidence_url`; Table 16 `external_evidence_verified` >= 50.

## Priority 3 — Paper-facing updates — Done

- `paper/results_memo.md`, `paper/red_team_memo.md`, `paper/reviewer_results_snapshot.md` (PCS markers via `make sync-paper-stats`)
- `paper/claim_table_map.csv` and `paper/main_table_claim_map.csv`
- `docs/model_interpretation_matrix.md`, `docs/PCS_GATE_CHECKLIST.md`
- `paper/draft_v1.md` (hub-centered measurement draft)
- `paper/pcs_gate_report.json` (via `python scripts/15_pcs_status.py --json`)

## Evidence hierarchy

### Main text can use

- Dataset construction (Tables A, B)
- Pilot-zone and smart-factory overlap (Table C)
- Hub-exclusion robustness (Table D)
- City typology (Tables E)
- Ex ante industry heterogeneity (Table F)
- Export relevance descriptives (Tables G, H)

### Appendix can use

- Table I / 5b public fallback controls
- ChinaUTC missingness report
- Stratified audit results (Table 17 via outputs)
- External-verification evidence class (50 projects)

### Main text should not use as primary claims

- Strict Table 5
- Tables 7–8 when they depend on unavailable strict controls
- Causal treatment-effect language
- Productivity or export-effect language

## Role assignments

| Role | Status |
|------|--------|
| **Engineer A** | Done unless EPS/NBS export appears |
| **Engineer B** | Done (B1 + B2) |
| **Engineer C** | Done (Table I docs + export descriptives) |
| **Engineer D** | Done (gate chain + interpretation matrix) |
| **Paper owner** | Draft from `paper/draft_v1.md` and `paper/main_tables/` |

## Final paper positioning

> We build a new measurement pipeline for China's industrial AI diffusion by linking national AI pilot zones, MIIT excellence-level smart-factory recognition, city-resolution evidence classes, hub typologies, and sector/export relevance. The evidence shows that listed smart-factory adoption is concentrated in pilot-zone and high-capacity hub cities. Public fallback controls suggest that the association is not entirely explained by GDP, population, industrial structure, trade, telecom, and industrial-output proxies in a limited 2024 sample, but the strict EPS/NBS control design remains unavailable. The paper therefore interprets China's AI diffusion state as a hub-centered industrial adoption architecture, not as a uniform causal treatment effect of pilot-zone designation.
