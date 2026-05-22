# Current Sprint Priorities

**Decision:** Stop forcing ChinaUTC into strict Table 5. Keep strict Table 5 skipped. Use Table I / 5b as appendix robustness only. Move engineering effort to B1, B2, and paper drafting.

## Workstream A — Closed (public path complete)

**Delivered:**

- `paper/main_tables/table_I_appendix_public_fallback_controls.csv` (from `table_5b_public_fallback_controls.csv`)
- `docs/PUBLIC_FALLBACK_CONTROLS_INTERPRETATION.md`

**Usable as:** appendix robustness only.

**Not usable as:** strict EPS/NBS controlled evidence (no FDI or fixed-asset investment in the public bundle; 51 complete 2024 observations).

**Engineer instruction:** Do not expand ChinaUTC scraping unless a new source contains FDI or fixed-asset investment. The public fallback has reached its useful limit.

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

Until then, Workstream A is closed for engineering.

### Required paper wording (controls)

> Strict EPS/NBS controlled models remain unavailable because the public ChinaUTC bundle lacks FDI and fixed-asset investment. We therefore report a separate appendix robustness specification using partial public China City Statistical Yearbook controls.

### Required paper wording (Table I)

> In the 2024 ChinaUTC public-control subset, pilot-zone status remains positively associated with listed smart-factory counts in OLS count and log-count models, while the Poisson specification is not statistically significant.

### Interpretation (one sentence)

> The pilot-zone association survives in a limited 2024 public-control cross-section, but this result is not EPS-equivalent because the public ChinaUTC bundle lacks FDI and fixed-asset investment and covers only 51 complete observations.

This supports hub-centered diffusion framing. It does **not** support causal language.

### Forbidden wording

- The controlled model passes.
- The EPS/NBS model supports the association.
- Pilot-zone effects survive full controls.

---

## Priority 1 — Engineer B1: City-resolution audit

Fill `data/audit/city_resolution_sample_audit.csv`:

- at least 50 `rule_based_text_inference` rows
- at least 20 `official_location_exact` rows

Then:

```powershell
make apply-geo-updates
make recompute-audit
make validate-audit
make sync-paper-stats
make main-tables
python scripts/15_pcs_status.py
```

**Paper gate:** Do not say "audited city resolution" until `make validate-audit` exits 0.

Optional conservative path (label honestly as AI-assisted, not independent human audit):

```powershell
python scripts/23_fill_conservative_audit_decisions.py
make apply-geo-updates
make recompute-audit
make validate-audit
```

Human review remains the better option.

---

## Priority 2 — Engineer B2: External verification

Use:

- `docs/DEEP_RESEARCH_A_B2_FINDINGS.md`
- `docs/DEEP_RESEARCH_A_B2_ROUND2.md`
- `docs/DEEP_RESEARCH_A_B2_ROUND3.md`

Fill at least 50 rows in `data/interim/external_verification_queue.csv` (`external_evidence_url`, `external_evidence_type`, `audit_notes`).

Then:

```powershell
make apply-geo-updates
make geo-audit
make validate-geo
make panel
make analysis
make sync-paper-stats
make main-tables
python scripts/15_pcs_status.py
```

**Target:** external evidence verified >= 50.

**Paper gate:** Do not say "externally verified city assignments" until Table 16 shows `external_evidence_verified` >= 50.

---

## Priority 3 — Paper-facing updates (after B1/B2)

Update:

- `paper/results_memo.md`
- `paper/red_team_memo.md`
- `paper/reviewer_results_snapshot.md`
- `paper/claim_table_map.csv`
- `docs/model_interpretation_matrix.md`

---

## Evidence hierarchy

### Main text can use

- Dataset construction
- Pilot-zone and smart-factory overlap
- Hub-exclusion robustness
- City typology
- Ex ante industry heterogeneity
- Export relevance descriptives

### Appendix can use

- Table I / 5b public fallback controls
- ChinaUTC missingness report
- Conservative audit results (if labeled honestly)
- External-verification table (once 50 rows pass)

### Main text should not use as primary claims

- Strict Table 5
- Tables 7–8 when they depend on unavailable strict controls
- Causal treatment-effect language
- Productivity or export-effect language

---

## Role assignments

| Role | Status |
|------|--------|
| **Engineer A** | Done unless EPS/NBS export appears |
| **Engineer B** | Critical path: B1 + B2 |
| **Engineer C** | Appendix docs for Table I and export relevance; no causal export claims |
| **Engineer D** | After B1/B2: full gate rerun + `docs/model_interpretation_matrix.md` |
| **Paper owner** | Draft from `paper/main_tables/` now |

---

## Final paper positioning

> We build a new measurement pipeline for China's industrial AI diffusion by linking national AI pilot zones, MIIT excellence-level smart-factory recognition, city-resolution evidence classes, hub typologies, and sector/export relevance. The evidence shows that listed smart-factory adoption is concentrated in pilot-zone and high-capacity hub cities. Public fallback controls suggest that the association is not entirely explained by GDP, population, industrial structure, trade, telecom, and industrial-output proxies in a limited 2024 sample, but the strict EPS/NBS control design remains unavailable. The paper therefore interprets China's AI diffusion state as a hub-centered industrial adoption architecture, not as a uniform causal treatment effect of pilot-zone designation.
