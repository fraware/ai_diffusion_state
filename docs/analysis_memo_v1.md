# Analysis memo v1

**Scope:** Descriptive overlap and baseline adoption models linking AI pilot zones to excellence-level smart-factory counts. Not a causal design.

## Data used

| Artifact | Role |
|---|---|
| `pilot_zones.csv` | 17 pilot units, `pilot_year` 2019–2021 |
| `smart_factories_clean.csv` | 509 MIIT projects (235 in 2024, 274 in 2025) |
| `smart_factory_city_year.csv` | 188 city-year cells with resolved city |
| `analysis_city_year_panel.csv` | Pilot cities + factory cities, 2019–2025 |

## Key measurement limits

1. Smart-factory lists exist only for **2024 and 2025**; earlier years in the panel are **zero-filled** (no pre-2024 excellence list).
2. **316 of 509** projects lack a resolved city (`city_confidence = unknown`); city-level models use **193** resolved projects (102 exact + 91 high). Province-only locations in the official lists are not imputed to a city.
3. **2024 HTML parser** was corrected so project names containing `AI` (e.g. `AI 大模型驱动的…`) are not split incorrectly.
4. City controls (EPS/NBS) are **not yet merged**; place files in `data/raw/city_controls/` and run `make city-controls`. Coefficients are without economic controls until then.

## Descriptive findings (see tables)

- `outputs/tables/table_1_dataset_summary.csv` — observation counts by dataset.
- `outputs/tables/table_2_top_smart_factory_cities.csv` — cities with the most projects, with pilot-zone flag.
- `outputs/tables/table_pilot_zone_overlap.csv` — mean projects per city, pilot vs non-pilot (resolved cities only).

## Baseline models (see `table_3_pilot_zone_adoption_models.csv`)

- **Model 1:** `smart_factory_projects` on `pilot_zone` with year effects (2024–2025 sample).
- **Model 2:** `post_pilot` with city and year fixed effects.
- **Model 3:** `log(1 + projects)` specification for skewness.

Standard errors clustered by city. Positive `post_pilot` coefficients indicate higher **listed** smart-factory adoption in post-designation years, not causal policy effects.

## Event study (see `table_event_study_coefficients.csv`, `fig_event_study_pilot_zones.png`)

Estimated on **pilot cities only**, binning `year - pilot_year`, omitting $t=-1$. Pre-2024 bins are dominated by zeros because the outcome did not exist; they do **not** validate parallel pre-trends in adoption.

## What we do not claim

- Pilot zones did not randomly assign cities.
- Smart-factory lists measure official recognition, not total AI investment.
- Export upgrading Table 4 is descriptive only; not a causal test of diffusion (`docs/source_notes/baci.md`).

## Export outcomes (BACI HS17 202601)

Built via `make baci` when raw CEPII files are present:

- `export_outcomes_hs6_year.csv`: China exporter HS6-year, 2017–2024 (42,650 rows).
- `hs_to_smart_factory_sector_bridge.csv`: documented HS2/HS4 mappings to smart-factory industries.
- `export_outcomes_sector_year.csv`: sector-level aggregates and growth rates.
- `table_4_export_upgrading_models.csv`: descriptive sector-year regression (exposure insignificant in current build).

## Paper integration (Phase 6)

- Narrative: `paper/outline.md`, `paper/data_appendix.md`, `paper/results_memo.md`, `paper/red_team_memo.md`.
- Manifest: `make paper` → `paper/artifact_manifest.json`, `paper/claim_table_map.csv`.

## Next empirical steps

1. Add audited rows to `data/seed/smart_factory_city_overrides.csv` where external evidence exists (no bulk imputation).
2. Add EPS/NBS `city_controls_year.csv` and re-estimate adoption models with controls.
3. City-industry panel with export linkage: `analysis_city_industry_year_panel.csv`.
