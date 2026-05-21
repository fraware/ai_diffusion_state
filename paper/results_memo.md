# Results memo (pipeline v2 — hub-centered diffusion sprint)

**Generated from:** `make analysis` on the current processed data. Numbers below are taken from `outputs/tables/*.csv` in this repository build. This memo is descriptive and associational, not causal.

**Sprint question:** Is listed smart-factory adoption merely “pilot vs non-pilot,” or concentrated in a **hub-and-spoke diffusion architecture** (municipal capacity, mega-hubs, industrial ecosystems)?

**Framing:** Listed smart-factory adoption is concentrated in AI pilot-zone cities, but robustness checks show the pattern is heavily driven by major hubs and direct-admin municipalities. Pilot-zone designation marks part of that architecture; it is not evidence of uniform policy treatment across treated cities.

**Blocked until EPS/NBS (paper):** Real city controls for interpretable Models 4–7. Optional `make city-controls-stub` runs CI pipeline only. Hub-exclusion and typology (Tables 6, 14) run now.

## 1. Measurement summary

From `table_1_dataset_summary.csv`:

- 17 AI pilot-zone units (2019–2021).
- 509 MIIT excellence-level smart-factory projects (235 in 2024, 274 in 2025).
- **503** projects with resolved city after geo-audit v2 (**6** remain province-only / unverified).
- **450+** audited override rows in `data/seed/smart_factory_city_overrides.csv` (see `docs/source_notes/city_geo_audit.md`).

Pre-2024 years in `analysis_city_year_panel.csv` are **zero-filled** for smart-factory counts because public excellence lists begin in 2024.

## 2. Descriptive overlap — resolved cities

From `table_pilot_zone_overlap.csv` (2024–2025 totals, cities with known `city`):

| Sample | Cities | Total projects | Mean per city |
|--------|-------:|---------------:|--------------:|
| Pilot-zone cities | 16 | 192 | 12.00 |
| Non-pilot cities | 142 | 311 | 2.19 |
| All resolved | 158 | 503 | 3.18 |

Mean difference (pilot minus non-pilot): **9.81** projects per city.

Top cities (`table_2_top_smart_factory_cities.csv`, pilot flag): Shanghai (30, pilot), Chongqing (22, pilot), Beijing (19, pilot), Tianjin (17, pilot), Qingdao (14, non-pilot).

## 3. Hub-exclusion robustness (Table 6)

Without city economic controls, `pilot_zone` coefficient on 2024–2025 listed project counts. Table 6 adds `interpretation`, `coefficient_relative_to_full_sample`, and `projects_remaining_share`.

| Exclusion rule | Cities | Projects | pilot_zone coef | p-value | Reader takeaway |
|----------------|-------:|---------:|----------------:|--------:|-----------------|
| Full sample | 125 | 382 | 3.92 | <0.001 | Baseline (analysis universe, resolved cities) |
| Drop Beijing, Shanghai, Shenzhen, Hangzhou | 121 | 318 | 2.97 | 0.0002 | Weakens (~76% of coef) |
| Drop above + Guangzhou | 120 | 312 | 3.05 | 0.0004 | Weakens (~78% of coef) |
| Drop direct-admin municipalities | 121 | 294 | 2.04 | <0.001 | Substantially weakens (~52% of coef) |
| Drop top 5 smart-factory cities | 120 | 277 | 2.11 | <0.001 | Weakens (~54% of coef) |
| Drop top 10 GDP cities | 115 | 272 | 3.08 | 0.010 | Sensitive to GDP city definition |

**Conclusion:** With broader city resolution, the association **remains positive** but **attenuates when mega-hubs and direct-admin municipalities are excluded**. Hub architecture remains central; this is not a uniform treatment effect across treated cities.

Controlled rows (`spec=controlled`) append after `make city-controls`.

## 4. City diffusion typology (Table 14)

`table_14_city_diffusion_typology.csv` and `fig_city_typology_smart_factory_counts.png` classify cities into:

- `frontier_municipality_hub` (direct-admin municipalities)
- `pilot_industrial_hub`, `pilot_non_hub`
- `nonpilot_industrial_hub`, `nonpilot_low_adoption`
- `unknown_geo_limited`

Use this table as the central descriptive device: diffusion is clustered by institutional and industrial hub type, not a binary pilot flag alone.

## 5. Adoption models (Table 3)

From `table_3_pilot_zone_adoption_models.csv`, N = 250 city-years, **125** cities (pilot + non-pilot universe).

**Model 1:** `pilot_zone` coef = **3.92**, p &lt; **0.001** — interpret jointly with Table 6 hub attenuation (not collapse).

**Models 2–3:** Within-city `post_pilot` terms are large with city FE; not causal treatment effects.

## 6. Controlled adoption models (Table 5)

**Production:** EPS/NBS still required for paper (`data/raw/city_controls/`).

**CI stub:** `make city-controls-stub` enables Models 4–7; stub Model 4 `pilot_zone` is weaker than baseline (not for claims).

**Decision rule after real controls:**

- Survives controls + hub exclusions → cautious robust association language.
- Survives controls, not hubs → **hub-centered diffusion paper** (current lean).
- Disappears after controls → measurement / geography paper.

## 7. Balance and matching (Tables 7–8)

**Status:** Skipped without city controls.

**Fix deployed:** Matched adoption sample now includes **both** `matched_pilot` and `matched_control` cities, with `n_matched_pilot_cities`, `n_matched_control_cities`, and `matched_city_ratio` on Table 8.

## 8. City-industry models (Table 13)

Preferred specs use **`ai_exposure_ex_ante`** from `industry_ai_exposure_ex_ante.csv` (not derived from outcomes). Tag-derived exposure specs are labeled `descriptive_tag_derived` in the `exposure_source` column.

Paper sentence: *We classify industries by ex ante technological compatibility with industrial AI, then test whether listed adoption is more concentrated in pilot-zone cities within high-exposure industries.*

## 9. Export (descriptive)

- `table_15_export_relevance_by_sector.csv`: strategic relevance of smart-factory sectors vs export basket (not causal).
- Legacy `table_4` / `table_12` remain non-causal / underpowered.

## 10. Geography resolution

`table_9_city_resolution_audit.csv` tracks coverage. Target: ≥250 resolved projects via audited overrides (`data/seed/smart_factory_city_overrides.csv` with evidence fields). Engineer B workstream; not automated.

## 11. What is not claimed

- Pilot zones caused adoption.
- Average treatment effect across all treated cities.
- Causal export effects from smart-factory lists.

See `paper/red_team_memo.md`, `paper/reviewer_results_snapshot.md`, `docs/source_notes/industry_ai_exposure.md`.
