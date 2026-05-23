# Model interpretation matrix

**Paper frame:** Hub-centered diffusion architecture; **not** uniform pilot-zone treatment, productivity causality, or export effects.

**Last rebuilt:** 2026-05-22 full PCS gate chain (`make pcs`). Use only `paper/main_tables/` in the draft; run `make sync-paper-stats` after every `make analysis`.

## PCS gates (current build)

| Gate | Status |
|------|--------|
| 509/509 city resolution | Pass |
| External verification | 50 projects |
| Stratified audit (Table 17) | 70/70 decisions |
| Geo evidence hygiene | Pass |
| Strict Table 5 | Skipped (expected) |
| Appendix Table I | Pass |
| Paper main tables A–I | 10/10 |

Quick check: `python scripts/15_pcs_status.py` or `docs/PCS_GATE_CHECKLIST.md`.

## Table map

| Table | What variation identifies the coefficient | Supports (claim tier) | Cannot support |
|-------|----------------------------------------|------------------------|----------------|
| **Table A** — dataset counts | Coverage of pilots, projects, geo classes | Measured data construction | Representativeness of all China smart manufacturing |
| **Table B** — city resolution | Evidence-class distribution (official / rule-based / external) | Validated descriptive geo quality | Full external audit of all 509 assignments |
| **Table C** — pilot overlap | Cross-city 2024–2025 listed counts by pilot status | Pilot-zone concentration (descriptive) | Causal treatment effect |
| **Table D / 6** — hub exclusion | `pilot_zone` under sample restrictions | Hub-centered architecture; attenuation outside mega-hubs | Zero national association; ATT |
| **Table E** — city typology | Descriptive counts by diffusion type | Institutional/industrial hub clustering | Binary pilot flag as sufficient summary |
| **Table E (ex ante)** — typology | Capacity typology without top-SF-city labels | Ex ante capacity framing | Outcome-driven labels |
| **Table F / 13** — city-industry | `pilot_zone` × ex ante AI exposure | Heterogeneity in pilot cities (associational) | Causal mechanism; tag-derived specs in main text |
| **Table G / 15** — export relevance | Sector shares vs export basket | Descriptive strategic overlap | Export causality |
| **Table H** — export share comparison | Listed sectors vs 2024 export basket shares | Descriptive overlap | Productivity or upgrading claims |
| **Table I / 5b** — public fallback | 2024 cross-section; partial ChinaUTC controls | Appendix robustness: pilot survives OLS count/log | EPS-equivalent controls; causal claims; Poisson as primary |
| **Table 3** — baseline adoption | Cross-city pilot indicator | Baseline associational adoption | Causal pilot effect |
| **Table 3** — Models 2–3 | Within-city `post_pilot` + city FE | Post-designation years vs pre (list from 2024) | Pre-trend validation |
| **Table 5** — controlled adoption | City-year covariates (GDP, FDI, etc.) | — | **Blocked** until EPS/NBS; do not cite |
| **Table 7–8** — balance / matched | Pre-treatment balance; matched sample | — | **Blocked** without strict controls |
| **Table 19** — province-year | Province-year FE; pilot-province indicator | Coarse descriptive check | Pilot-city isolation |
| **Table 4 / 12** — export models | — | — | **Do not use** in main text |
| **Timing diagnostic** | Event-time bins | Timing diagnostic only | Pre-trend validation |

## Table I (appendix) — required wording

Strict EPS/NBS Table 5 remains unavailable (no FDI / fixed-asset investment in public bundle).

**Allowed (Table I):**

> In the 2024 ChinaUTC public-control subset, pilot-zone status remains positively associated with listed smart-factory counts in OLS count and log-count models, while the Poisson specification is not statistically significant.

**Forbidden:**

- The controlled model passes.
- The EPS/NBS model supports the association.
- Pilot-zone effects survive full controls.

See `docs/PUBLIC_FALLBACK_CONTROLS_INTERPRETATION.md`.

## Table 5–8 gate (strict controls)

Until real EPS/NBS files are ingested and `make city-controls` merges adoption-year controls:

- Table 5 must remain skipped or explicitly non-EPS.
- Tables 7–8 remain skipped for paper claims.

## Geo gate — passed

- Table 16 / B: **50** `external_evidence_verified`, **102** `official_location_exact`, **312+** `rule_based_text_inference` (exact split from current register).
- Table 17: stratified audit **70/70** complete.
- **Allowed:** “At least 50 city assignments are supported by non-list external evidence…”
- **Not allowed:** “all assignments externally verified” or “fully audited geocoding.”

## Drafting rule

1. Numbers from `paper/main_tables/` only.
2. Run `make sync-paper-stats` after `make analysis`.
3. Match claim tier in `paper/claim_table_map.csv`.
4. Identification limits in `paper/red_team_memo.md`.
