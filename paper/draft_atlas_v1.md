# China AI Diffusion Atlas v0.2: Pilot Zones, AI Exposure, and Industrial AI Patents

**Draft atlas v1**  
**Status:** Atlas **tiered robustness extension** operational (`atlas_tiered_extension_ready = true`; **65.4%** tiered city fill on 4,014,104 keys). **Not evidence-ready** (`atlas_evidence_ready = false`; `ready_for_evidence_chain = false`; `exact_geography_ready = false`). Applicant geography is a **tiered robustness layer** (HQ page, university, name-token tiers)—**not** exact publication-number address geocoding. Do **not** report publication-ready F1 or pilot-zone × patent causal results until `ready_for_evidence_chain` is true. See `paper/atlas_gate_report.json`, `outputs/tables/table_P14_*`, `table_P17_*`, and `docs/ATLAS_IIDS_TIERED_ROBUSTNESS_FROZEN.md`.
**PCS guard:** `make pcs` must remain green (`paper/pcs_gate_report.json`).

## Abstract

This draft specifies the true-vision design: national AI pilot-zone designation, ex ante industry AI exposure, city-industry-year industrial AI patents (2015–2025), and MIIT excellence-level smart-factory recognition (2024–2025) as complementary outcome layers. The control laptop holds a filtered OpenXLab IIDS-derived CN industrial-AI patent layer with **4,014,104** publication-number keys. Applicant geography is merged as a **tiered robustness extension** (~65% city fill; tier breakdown in table P14/P17)—suitable for appendix diagnostics, **not** for publication-ready patent identification until external CNIPA/Incopat batches raise coverage to the **80%** evidence-chain gate. Smart-factory descriptive patterns follow the PCS hub architecture (pilot and hub concentration). After `ready_for_evidence_chain = true`, patent F1 results must be taken **only** from regenerated `outputs/tables/`—not from fixture or pre-geography runs.

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

## 4. Current results (tiered robustness; evidence chain pending)

Rebuild status: `make atlas-iids-tiered-extension` then `python scripts/50_atlas_status.py --json --tiered-extension`.

**Patent F1 (F1 models):** Not reported here. `ready_for_evidence_chain` is false (~65% tiered fill; need ~80% via external geography). `make atlas-iids-control-evidence-chain` and `python scripts/50_atlas_status.py --json --require-evidence` run only after CNIPA/Incopat batch import. Gate diagnostics in `paper/atlas_gate_report.json` are internal warnings only.

**Supported (descriptive):**

- Smart-factory recognition concentrates in pilot-zone and high-capacity cities (PCS Table C).
- Ex ante high-exposure industries differ from low-exposure industries in the taxonomy.

**Not yet testable on patents (80% evidence gate):**

- Post-pilot industrial AI patenting in AI-exposed industries (await external geography import and evidence chain).
- Robot-complementarity amplification of a patent response (same).

## 5. Next empirical step

Place CNIPA/Incopat batch exports under `data/interim/iids_geo_exports/` per `docs/ATLAS_IIDS_GEO_VENDOR_HANDOFF.md`. Then `make atlas-iids-external-geo-pipeline`, `make atlas-iids-geo-coverage-validate`, `make atlas-iids-control-evidence-chain`, `make atlas-v02`, `make atlas-models-v02`. Target **+751k** additional keyed cities. Do not change exposure scores using smart-factory outcomes.

## 6. What this draft does not claim

- Causal average treatment effect of pilot-zone designation.
- Productivity or export-upgrading effects.
- EPS-equivalent controlled adoption (see PCS Table I appendix only).
- Full external audit of all 509 city assignments.
- Address-level geocoding of every publication number in the corpus (tiered layer only today).
- F1 or pilot-zone patent coefficients as publication-main results (blocked until `ready_for_evidence_chain`).

See `docs/model_interpretation_matrix_atlas.md` and `docs/POST_PCS_TRUE_VISION_HANDOFF.md`.

## Tables and figures (Atlas)

- `outputs/tables/table_F1_pilot_x_ai_exposure_patents.csv`
- `outputs/tables/table_F2_robot_complementarity_patents.csv`
- `outputs/tables/table_F3_pilot_x_ai_exposure_smart_factories.csv`
- `outputs/tables/table_F4_atlas_event_study_patents.csv`
- `outputs/tables/table_C1_industry_exposure_scores.csv`
