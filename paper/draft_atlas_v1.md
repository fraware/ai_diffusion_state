# China AI Diffusion Atlas v0.2: Pilot Zones, AI Exposure, and Industrial AI Patents

**Draft atlas v1**  
**Status:** Atlas **software-ready** (`atlas_software_ready = true`); **not evidence-ready** (`atlas_evidence_ready = false`; `ready_for_evidence_chain = false`). See `paper/atlas_evidence_gate_report.json`. A real OpenXLab IIDS-derived patent export (4,014,104 filtered CN records) is on the control laptop; **geography merge is pending** (`cnipa_patent_geography_2015_2024.csv`). Do not report patent F1 coefficients until `ready_for_evidence_chain` is true.
**PCS guard:** `make pcs` must remain green (`paper/pcs_gate_report.json`).

## Abstract

This draft specifies the true-vision design: national AI pilot-zone designation, ex ante industry AI exposure, city-industry-year industrial AI patents (2015–2025), and MIIT excellence-level smart-factory recognition (2024–2025) as complementary outcome layers. The control laptop holds a filtered OpenXLab IIDS-derived CN industrial-AI patent layer with **4,014,104** publication-number keys and a 17-batch geography procurement plan; applicant geography is **not yet merged**, so patent interaction models are **not evidentiary** in this draft. Smart-factory descriptive patterns follow the PCS hub architecture (pilot and hub concentration). After geography passes coverage gates and the evidence chain runs, patent F1 results must be taken **only** from regenerated `outputs/tables/`—not from fixture or pre-geography runs.

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

## 4. Current results (pre-geography)

Rebuild status: `make atlas-iids-geography-preflight` then `python scripts/50_atlas_status.py --json`.

**Patent F1 (F1 models):** Not reported here. Geography merge and `make atlas-iids-control-evidence-chain` must complete with `ready_for_evidence_chain = true` before any pilot-zone × AI-exposure patent coefficient is cited. Pre-geography gate diagnostics in `paper/atlas_gate_report.json` are internal warnings only.

**Supported (descriptive):**

- Smart-factory recognition concentrates in pilot-zone and high-capacity cities (PCS Table C).
- Ex ante high-exposure industries differ from low-exposure industries in the taxonomy.

**Not yet testable on patents (geography pending):**

- Post-pilot industrial AI patenting in AI-exposed industries (await IIDS geography merge and evidence chain).
- Robot-complementarity amplification of a patent response (same).

## 5. Next empirical step

Deliver and normalize `data/raw/patents/cnipa_patent_geography_2015_2024.csv` per `docs/ATLAS_IIDS_GEO_VENDOR_HANDOFF.md` (batch exports → `make atlas-iids-geo-coverage-validate`). Then `make atlas-iids-control-evidence-chain`, `make atlas-v02`, `make atlas-models-v02`. Do not change exposure scores using smart-factory outcomes.

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
