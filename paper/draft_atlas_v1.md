# China AI Diffusion Atlas v0.2: Pilot Zones, AI Exposure, and Industrial AI Patents

**Draft atlas v1**  
**Status:** Atlas **software-ready** (`atlas_software_ready = true`); **not evidence-ready** (`atlas_evidence_ready = false`; `fixture_patents_detected = true`). See `paper/atlas_evidence_gate_report.json`. Patent layer uses repository fixture microdata until real CNIPA/Lens exports are placed in `data/raw/patents/` (see `README_REAL_EXPORTS.md`).
**PCS guard:** `make pcs` must remain green (`paper/pcs_gate_report.json`).

## Abstract

This draft tests the true-vision design: whether national AI pilot-zone designation is associated with stronger industrial AI diffusion in industries classified ex ante as AI-exposed, using industrial AI patenting and MIIT excellence-level smart-factory recognition as complementary outcome layers. The Atlas v0.2 panel merges 17 pilot-zone units, 29-industry ex ante exposure scores, city-industry-year industrial AI patents (2015–2025), and smart-factory counts (2024–2025). On the current fixture-backed patent sample with saturated fixed effects, the pilot-zone × AI-exposure interaction for industrial AI patents is negative and imprecisely estimated. Smart-factory recognition remains concentrated in pilot and hub cities. The honest Phase 1 conclusion is methodological: the Atlas pipeline is operational; the empirical sign and precision of the patent interaction must be re-estimated on full CNIPA microdata before any policy claim.

## 1. Design

The measurement paper (PCS) documents hub-centered smart-factory recognition. The Atlas extends that architecture to a city × industry × year panel suitable for heterogeneity models:

```text
industrial_ai_patents_cit =
    β post_pilot_ct × ai_exposure_i
  + city_industry_FE + province_year_FE + industry_year_FE + ε_cit
```

Exposure scores are assigned ex ante from sector reviews (IFR, MIIT, process-automation literature). They are not calibrated on smart-factory counts. Robot compatibility is a separate industry-level index for complementarity models.

Procurement is not yet merged (`procurement_layer_status = pending`).

## 2. Data layers

| Layer | File | Role |
|-------|------|------|
| Industry crosswalk | `data/seed/industry_crosswalk_atlas.csv` | 29 Atlas industries |
| AI exposure | `data/processed/industry_ai_exposure_ex_ante_v2.csv` | Eight dimension scores + composite |
| Robot compatibility | `data/processed/industry_robot_compatibility.csv` | Complementarity index |
| Patents | `data/processed/industrial_ai_patents_city_industry_year.csv` | Long-run variation |
| Smart factories | `data/processed/smart_factory_city_industry_year.csv` | 509 projects → city-industry-year |
| Atlas panel | `data/processed/china_ai_diffusion_atlas_city_industry_year.csv` | Merged analysis file |

Smart-factory validation: 235 (2024) + 274 (2025) = 509; 50 external-verified geo assignments roll up to `external_verified_count`.

## 3. Phase 1 models (associational)

Models are reported in `outputs/tables/table_F1`–`F4` with claim tier `associational_exploratory`.

**Patents (F1):** OLS count, OLS log1p, and Poisson for `post_pilot × ai_exposure_ex_ante` with city×industry, province×year, and industry×year fixed effects.

**Robot complementarity (F2):** `post_pilot × ai_exposure × robot_compatibility`.

**Smart factories (F3):** `post_pilot × ai_exposure` on `smart_factory_count` (2024–2025 years in panel).

**Event study (F4):** `years_since_pilot × ai_exposure` for k ∈ {-4,…,4}, k = -1 omitted (pilot cities only).

## 4. Current results (fixture patent sample)

Rebuild: `make atlas-phase1` then `python scripts/50_atlas_status.py --json`.

On the committed fixture build, F1 OLS count gives a small **negative** `post_x_exposure` coefficient with undefined clustered standard errors under dense fixed effects. This is **not** evidence against pilot zones; it reflects fixture sample size, FE saturation, and the absence of full CNIPA coverage.

**Supported (descriptive):**

- Smart-factory recognition concentrates in pilot-zone and high-capacity cities (PCS Table C).
- Ex ante high-exposure industries differ from low-exposure industries in the taxonomy.

**Not supported (Phase 1 fixture):**

- Post-pilot increase in industrial AI patenting in AI-exposed industries.
- Robot-complementarity amplification of a positive patent response.

## 5. Next empirical step

Replace `data/raw/patents/industrial_ai_patent_records.csv` with a full 2015–2024 CNIPA search export for priority industries and cities. Re-run `make atlas-patents atlas-v02 atlas-models-v02`. Do not change exposure scores using smart-factory outcomes.

## 6. What this draft does not claim

- Causal average treatment effect of pilot-zone designation.
- Productivity or export-upgrading effects.
- EPS-equivalent controlled adoption (see PCS Table I appendix only).
- Full external audit of all 509 city assignments.

See `docs/model_interpretation_matrix_atlas.md` and `docs/POST_PCS_TRUE_VISION_HANDOFF.md`.

## Tables and figures (Atlas)

- `outputs/tables/table_F1_pilot_x_ai_exposure_patents.csv`
- `outputs/tables/table_F2_robot_complementarity_patents.csv`
- `outputs/tables/table_F3_pilot_x_ai_exposure_smart_factories.csv`
- `outputs/tables/table_F4_atlas_event_study_patents.csv`
- `outputs/tables/table_C1_industry_exposure_scores.csv`
