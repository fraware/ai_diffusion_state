# Results memo (pipeline v1)

**Generated from:** `make analysis` on the current processed data. Numbers below are taken from `outputs/tables/*.csv` in this repository build. This memo is descriptive and associational, not causal.

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

## 5. Event study (pilot cities only)

From `table_event_study_coefficients.csv` and `fig_event_study_pilot_zones.png`:

- Reference bin: year −1 relative to `pilot_year` (omitted).
- Pre-2024 bins (`m2`, `m3`, `m4`, `le_m4`) are dominated by zeros because the outcome did not exist in source lists.
- Post bins (`p0`–`p3`) are positive but imprecise (e.g. `p0` coef ≈ 8.08, p ≈ 0.24).

**Do not** interpret pre-2024 coefficients as parallel pre-trends in adoption.

## 6. Export upgrading (descriptive)

From `table_4_export_upgrading_models.csv` (requires `make baci`):

- `mean_province_sf_share` on `export_value_growth`: coef = 0.11, p = 0.82, N = 9 sector-years.
- Insufficient sector-year variation for strong inference; labeled non-causal in the table `note` column.

## 7. What is not in this memo

- City economic controls (GDP, manufacturing share, etc.) — pipeline ready, data not supplied.
- Propensity-score matching or synthetic controls.
- Causal interpretation of pilot-zone designation.

See `paper/red_team_memo.md` and `docs/analysis_memo_v1.md`.
