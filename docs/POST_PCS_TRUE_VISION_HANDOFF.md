# Post-PCS Handoff — Build the True Diffusion State Paper

## Verdict

The PCS measurement paper is engineering-complete and submission-ready. Do not spend additional engineering time on PCS packaging unless a paper owner requests journal-format edits.

The true Diffusion State paper is not yet built. It requires a city-industry-year China AI Diffusion Atlas with industrial AI patents, ex ante industry exposure, robot compatibility, smart-factory city-industry-year aggregation, and first Atlas models.

## Current PCS status

Run:

```powershell
make pcs
python scripts/15_pcs_status.py --json
```

Expected:

```text
ready = true
submission_ready = true
509/509 city resolution
102 official-location exact
357 rule-based inference
50 external evidence verified
70/70 audit decisions
Tables A-I present
Table I appendix-only controls
Strict Table 5 skipped by design
```

If this breaks, fix PCS immediately. Otherwise move to Atlas work.

---

# Engineering rule

From this point onward, a commit advances the true vision only if it creates or improves at least one of these artifacts:

```text
data/seed/industry_crosswalk_atlas.csv
data/processed/industry_ai_exposure_ex_ante_v2.csv
data/processed/industry_robot_compatibility.csv
data/processed/industrial_ai_patents_city_industry_year.csv
data/processed/smart_factory_city_industry_year.csv
data/processed/china_ai_diffusion_atlas_city_industry_year.csv
outputs/tables/table_F1_pilot_x_ai_exposure_patents.csv
outputs/tables/table_F2_robot_complementarity_patents.csv
outputs/tables/table_F3_pilot_x_ai_exposure_smart_factories.csv
paper/draft_atlas_v1.md
```

PCS-only commits should stop unless they are bug fixes.

---

# Immediate sprint: Atlas Phase 1

## Step 0 — Create branch

```powershell
git checkout main
git pull origin main
git checkout -b atlas-phase1
make pcs
```

## Step 1 — Industry taxonomy

Create:

```text
data/seed/industry_crosswalk_atlas.csv
```

Required columns:

```text
industry_code
industry
industry_group
smart_factory_keywords_zh
patent_keywords_zh
procurement_keywords_zh
hs6_prefixes_or_codes
mapping_notes
priority_tier
```

Minimum industries:

```text
semiconductors
electronics
ai_servers_and_computing_equipment
batteries
automotive_and_nev
industrial_machinery
robotics
precision_instruments
electrical_machinery
steel_and_metals
chemicals_and_petrochemicals
pharmaceuticals
shipbuilding
aerospace_components
solar_pv
logistics_equipment
textiles
food_processing
packaging
home_appliances
construction_machinery
rail_equipment
telecommunications_equipment
optical_fiber_and_photonics
power_equipment
```

Acceptance:

```text
25+ industries
all 509 smart-factory projects mappable or explicitly unmapped
patent keywords for at least 15 industries
HS6 placeholders for at least 15 industries
```

## Step 2 — Ex ante AI exposure and robot compatibility

Create scripts:

```text
scripts/40_build_industry_exposure_v2.py
scripts/41_validate_industry_exposure_v2.py
```

Create outputs:

```text
data/processed/industry_ai_exposure_ex_ante_v2.csv
data/processed/industry_robot_compatibility.csv
outputs/tables/table_C1_industry_exposure_scores.csv
```

Required exposure columns:

```text
industry_code
industry
machine_vision_exposure
robotics_exposure
predictive_maintenance_exposure
digital_twin_exposure
process_control_exposure
quality_inspection_exposure
smart_logistics_exposure
industrial_software_exposure
ai_exposure_ex_ante
classification_reason
classification_source
confidence
```

Score values:

```text
0 = low
1 = medium
2 = high
```

Rule:

```text
Do not derive exposure from smart-factory outcome counts.
```

Acceptance:

```text
25+ industries scored
15+ high/medium AI-exposure industries
15+ robot-compatible industries
validation passes
```

## Step 3 — Industrial AI patent layer

Create scripts:

```text
scripts/42_parse_industrial_ai_patents.py
scripts/43_build_industrial_ai_patents_city_industry_year.py
scripts/44_validate_industrial_ai_patents.py
```

Create raw file:

```text
data/raw/patents/industrial_ai_patent_records.csv
```

Required raw columns:

```text
patent_id
application_year
publication_year
grant_year
applicant_name
applicant_city
applicant_province
applicant_address
patent_title
abstract
claims_or_description
ipc_or_cpc
patent_type
source
source_url_or_file
search_keyword
```

Create processed file:

```text
data/processed/industrial_ai_patents_city_industry_year.csv
```

Minimum acceptance:

```text
2015-2024 or 2017-2024 coverage
50+ cities
10+ industries
5+ patent categories
no missing city/province/industry/year in processed main file
```

Strong target:

```text
100+ cities
20+ industries
10+ categories
sufficient city-industry-year variation for fixed-effect models
```

## Step 4 — Smart-factory Atlas layer

Create scripts:

```text
scripts/45_build_smart_factory_city_industry_year.py
scripts/46_validate_smart_factory_city_industry_year.py
```

Create:

```text
data/processed/smart_factory_city_industry_year.csv
```

Required columns:

```text
city
province
industry_code
industry
year
smart_factory_count
smart_factory_excellence_count
official_location_exact_count
rule_based_count
external_verified_count
industry_mapping_confidence
```

Acceptance:

```text
sum(smart_factory_count) = 509
2024 count = 235
2025 count = 274
external_verified_count = 50
80%+ high/medium industry mapping confidence
```

## Step 5 — Atlas v0.2 panel

Create scripts:

```text
scripts/47_build_atlas_v02.py
scripts/48_validate_atlas_v02.py
```

Create:

```text
data/processed/china_ai_diffusion_atlas_city_industry_year.csv
```

Required columns:

```text
city
province
industry_code
industry
year
pilot_zone
pilot_year
post_pilot
years_since_pilot
ai_exposure_ex_ante
robot_compatibility
smart_factory_count
smart_factory_excellence_count
industrial_ai_patents
machine_vision_patents
robotics_patents
predictive_maintenance_patents
digital_twin_patents
quality_inspection_patents
process_control_patents
industrial_ai_procurement_count
industrial_ai_procurement_value
aid_equal_index
source_coverage_flags
```

If procurement is not ready:

```text
procurement_layer_status = pending
```

Acceptance:

```text
50+ cities
20+ industries
2015-2024 or 2017-2025 coverage
unique city-industry-year rows
smart-factory total = 509
patent totals match patent layer
```

## Step 6 — First Atlas models

Create:

```text
scripts/49_run_atlas_models_v02.py
outputs/tables/table_F1_pilot_x_ai_exposure_patents.csv
outputs/tables/table_F2_robot_complementarity_patents.csv
outputs/tables/table_F3_pilot_x_ai_exposure_smart_factories.csv
outputs/tables/table_F4_atlas_event_study_patents.csv
docs/model_interpretation_matrix_atlas.md
```

Main model:

```text
industrial_ai_patents_cit = beta * post_pilot_ct × ai_exposure_i
                           + city_industry_FE
                           + province_year_FE
                           + industry_year_FE
                           + error_cit
```

Run variants:

```text
OLS count
OLS log1p count
Poisson count
```

Robot-complementarity model:

```text
industrial_ai_patents_cit = beta * post_pilot_ct × ai_exposure_i × robot_compatibility_i
                           + fixed effects
                           + error_cit
```

Smart-factory concentration model:

```text
smart_factory_count_cit = beta * post_pilot_ct × ai_exposure_i
                         + city_industry_FE
                         + industry_year_FE
                         + error_cit
```

Event study only for patents:

```text
industrial_ai_patents_cit = sum_k beta_k * 1[years_since_pilot = k] × ai_exposure_i
                           + city_industry_FE
                           + province_year_FE
                           + industry_year_FE
                           + error_cit
```

Window:

```text
k = -4 ... +4, omit -1
```

Every model output must include:

```text
model
term
coef
std_err
p_value
n_obs
n_cities
n_industries
years
fixed_effects
sample_rule
claim_tier
interpretation
not_supported_claims
```

---

# Makefile targets to add

```make
atlas-exposure:
	$(PYTHON) scripts/40_build_industry_exposure_v2.py
	$(PYTHON) scripts/41_validate_industry_exposure_v2.py

atlas-patents:
	$(PYTHON) scripts/42_parse_industrial_ai_patents.py
	$(PYTHON) scripts/43_build_industrial_ai_patents_city_industry_year.py
	$(PYTHON) scripts/44_validate_industrial_ai_patents.py

atlas-smartfactories:
	$(PYTHON) scripts/45_build_smart_factory_city_industry_year.py
	$(PYTHON) scripts/46_validate_smart_factory_city_industry_year.py

atlas-v02:
	$(PYTHON) scripts/47_build_atlas_v02.py
	$(PYTHON) scripts/48_validate_atlas_v02.py

atlas-models-v02:
	$(PYTHON) scripts/49_run_atlas_models_v02.py

atlas-phase1: atlas-exposure atlas-patents atlas-smartfactories atlas-v02 atlas-models-v02
```

---

# Phase 1 final status script

Create:

```text
scripts/50_atlas_status.py
```

It should report:

```text
pcs_ready
atlas_ready
exposure_layer_ready
patent_layer_ready
smart_factory_layer_ready
atlas_panel_ready
atlas_models_ready
n_cities
n_industries
years_min
years_max
main_result_summary
forbidden_claim_flags
```

Final command:

```powershell
make pcs
make atlas-phase1
python scripts/50_atlas_status.py --json
```

---

# Phase 1 paper integration

Create:

```text
paper/draft_atlas_v1.md
paper/atlas_results_memo.md
paper/atlas_red_team_memo.md
paper/atlas_claim_table_map.csv
paper/atlas_reviewer_snapshot.md
```

The current `paper/draft_v1.md` becomes the measurement module. It is not the final true-vision paper.

## Phase 1 paper claim if results are positive

```text
Pilot-zone designation is associated with stronger industrial AI patenting in AI-exposed industries, and this relationship is strongest in robot-compatible sectors. Smart-factory recognition is concentrated in the same hub-industrial systems.
```

## Phase 1 paper claim if results are null

```text
The smart-factory layer shows spatial and sectoral concentration, but the patent layer does not show a strong post-pilot response in AI-exposed industries.
```

Either result is useful. Do not force significance.

---

# Priority order

1. Industry taxonomy and exposure.
2. Industrial AI patent layer.
3. Smart-factory city-industry-year layer.
4. Atlas panel.
5. Patent and smart-factory Atlas models.
6. Procurement Phase 1B.
7. Export-upgrading module.

Procurement and exports are not abandoned. They are sequenced after the first Atlas panel and patent models.
