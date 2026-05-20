# Results memo (pipeline v2 — credibility sprint)

**Generated from:** `make analysis` on the current processed data. Numbers below are taken from `outputs/tables/*.csv` in this repository build. This memo is descriptive and associational, not causal.

**Sprint focus:** Are pilot-zone patterns visible after accounting for city size, industrial base, and hub selection? **Controlled models (Table 5) and balance (Tables 7–8) are blocked until EPS/NBS files are placed in `data/raw/city_controls/`.** Hub-exclusion results (Table 6) are available now.

## 1. Measurement summary

From `table_1_dataset_summary.csv`:

- 17 AI pilot-zone units (2019–2021).
- 509 MIIT excellence-level smart-factory projects (235 in 2024, 274 in 2025).
- 316 projects without a resolved city (`city=unknown`); 193 projects used in city-level overlap (102 `exact` + 91 `high` city confidence).

Pre-2024 years in `analysis_city_year_panel.csv` are **zero-filled** for smart-factory counts because public excellence lists begin in 2024.

## 2. Descriptive overlap — resolved cities

From `table_pilot_zone_overlap.csv` (2024–2025 totals, cities with known `city`):

| Sample | Cities | Total projects | Mean per city |
|--------|-------:|---------------:|--------------:|
| Pilot-zone cities | 15 | 125 | 8.33 |
| Non-pilot cities | 24 | 68 | 2.83 |
| All resolved | 39 | 193 | 4.95 |

Mean difference (pilot minus non-pilot): **5.50** projects per city.

Top cities (`table_2_top_smart_factory_cities.csv`, pilot flag): Shanghai (30, pilot), Chongqing (22, pilot), Beijing (19, pilot), Tianjin (17, pilot), Qingdao (14, non-pilot).

## 3. Province-level overlap (all projects)

From `table_pilot_zone_province_overlap.csv` (includes province-only locations):

| Sample | Provinces | Total projects | Mean per province |
|--------|----------:|---------------:|------------------:|
| Pilot-zone provinces | 15 | 395 | 26.33 |
| Non-pilot provinces | 16 | 114 | 7.13 |
| All | 31 | 509 | 16.42 |

Province totals **attribute every project in a pilot province** to the pilot-province sample, including projects in non-pilot cities within that province. Use city-level overlap for geographic comparisons; use province-level only with that aggregation caveat.

## 4. Adoption models (2024–2025, clustered by city)

From `table_3_pilot_zone_adoption_models.csv`, N = 82 city-years, 41 cities.

**Model 1** (`smart_factory_projects ~ pilot_zone + C(year)`):

- `pilot_zone`: coef = **2.26**, p = **0.044**, R² = 0.109.
- `C(year)[T.2025]`: coef = 0.32, p = 0.343.

**Model 2** (`smart_factory_projects ~ post_pilot + C(city) + C(year)`):

- `post_pilot`: coef = **3.00**, p below 0.001 (city and year FE absorbed; interpret as within-city post-designation contrast, not a causal effect).

**Model 3** (`log1p_projects ~ post_pilot + C(city) + C(year)`):

- `post_pilot`: coef = **0.75**, p below 0.001 on log(1 + projects).

Standard errors are clustered by city. Positive coefficients indicate higher **listed** smart-factory recognition in post-pilot years or pilot-zone cities; they do not identify the effect of designation.

## 5. Hub-exclusion robustness (Table 6, baseline specs)

Without city economic controls, `pilot_zone` coefficient on 2024–2025 listed project counts:

| Exclusion rule | Cities | Projects | pilot_zone coef | p-value |
|----------------|-------:|---------:|----------------:|--------:|
| Full sample | 41 | 193 | 2.26 | 0.044 |
| Drop Beijing, Shanghai, Shenzhen, Hangzhou | 37 | 139 | 1.31 | 0.174 |
| Drop above + Guangzhou | 36 | 136 | 1.42 | 0.170 |
| Drop direct-admin municipalities | 37 | 105 | **0.01** | **0.988** |
| Drop top 5 smart-factory cities | 36 | 91 | 0.25 | 0.492 |
| Drop top 10 GDP cities | — | — | skipped (no GDP controls) |

**Interim conclusion:** The baseline association **weakens outside mega-hubs** and **disappears when direct-admin municipalities are excluded**. This is consistent with a **hub-selection pattern** until controlled models are estimated.

Controlled hub exclusions will re-run automatically after `make city-controls`.

## 6. Controlled adoption models (Table 5)

**Status:** Skipped — `city_controls_year.csv` not built (no files in `data/raw/city_controls/`). See `data/raw/city_controls/README.md`.

After ingestion, re-run `make city-controls && make panel && make analysis` and update this section with whether `pilot_zone` remains positive under Models 4–7.

## 7. Timing diagnostic (pilot cities only)

From `table_timing_diagnostic_coefficients.csv` and `fig_timing_diagnostic_pilot_zones.png`:

**Label:** Timing diagnostic only — not pre-trend validation.

- Reference bin: year −1 relative to `pilot_year` (omitted).
- Pre-2024 bins (`m2`, `m3`, `m4`, `le_m4`) are dominated by zeros because the outcome did not exist in source lists.
- Post bins (`p0`–`p3`) are positive but imprecise (e.g. `p0` coef ≈ 8.08, p ≈ 0.24).

**Do not** interpret pre-2024 coefficients as parallel pre-trends in adoption.

## 8. Export upgrading (descriptive)

From `table_4_export_upgrading_models.csv` (requires `make baci`):

- `mean_province_sf_share` on `export_value_growth`: coef = 0.11, p = 0.82, N = 9 sector-years.
- Insufficient sector-year variation for strong inference; labeled non-causal in the table `note` column.

## 9. City-industry models (Table 13, exploratory)

`industry_ai_exposure.csv` scores industries by smart-factory tags and high-exposure sector flags. Table 13 tests whether `pilot_zone` associations differ by AI exposure (city + industry + year FE). Treat as exploratory given small city-industry cell counts.

## 10. What is not in this memo

- City economic controls (GDP, manufacturing share, etc.) — pipeline ready, data not supplied.
- Propensity-score matching or synthetic controls.
- Causal interpretation of pilot-zone designation.

See `paper/red_team_memo.md` and `docs/analysis_memo_v1.md`.
