# Atlas Sprint Phase 1 Execution Plan

## Why this plan exists

The PCS measurement paper is now gated, traceable, and submission-safe. That sprint does **not** yet achieve the full Diffusion State vision.

The full vision requires a city-industry-year China AI Diffusion Atlas that measures whether AI pilot zones predict industrial AI diffusion in AI-exposed industries, through patents, procurement, smart-factory recognition, and export-relevant sectors.

Phase 1 must therefore add the first true Atlas layers:

1. Atlas industry taxonomy and crosswalk.
2. Ex ante AI exposure and robot compatibility.
3. Industrial AI patent city-industry-year panel.
4. Atlas assembly v0.2.
5. First pilot-zone × AI-exposure models.

Procurement remains essential but should start after the patent layer and exposure layer are stable, because patents provide faster long-run pre/post variation.

---

# Phase 1 target

Deliver:

```text
data/processed/china_ai_diffusion_atlas_city_industry_year.csv
outputs/tables/table_F1_pilot_x_ai_exposure_patents.csv
outputs/tables/table_F3_pilot_x_ai_exposure_smart_factories.csv
outputs/tables/table_F4_robot_complementarity_models.csv
paper/draft_atlas_v1.md
```

Minimum empirical claim to unlock:

```text
Pilot-zone designation is associated with stronger industrial AI diffusion in AI-exposed industries, measured through industrial AI patenting and smart-factory recognition.
```

Strong empirical claim to target:

```text
The post-pilot increase is strongest in robot-compatible industries, supporting the view that AI diffusion depends on complementary production systems rather than generic AI enthusiasm.
```

Forbidden until later evidence:

```text
AI pilot zones caused productivity growth.
AI diffusion caused export upgrading.
Procurement caused commercial AI output.
The Atlas proves China has already experienced the next productivity shock.
```

---

# Branch and gate discipline

Create a new branch:

```bash
git checkout main
git pull origin main
git checkout -b atlas-phase1
```

Before starting:

```bash
make pcs
python scripts/15_pcs_status.py --json
```

Expected PCS state:

```text
ready: true
509/509 city resolution
102 official, 357 rule-based, 50 external
70/70 audit decisions
Tables A-I present
strict Table 5 skipped by design
```

Do not modify or weaken PCS files unless a pipeline change requires a synchronized update.

---

# Workstream 1 — Atlas industry taxonomy and crosswalk

## Owner

Engineer C first; Engineer E consumes this file.

## Purpose

Create a stable 30–40 industry taxonomy that every Atlas layer can use.

## Create

```text
data/seed/industry_crosswalk_atlas.csv
```

## Required columns

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

## Minimum industries

Use these as the first taxonomy:

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

Add more only if clearly needed by smart-factory or patent records.

## Quality rules

1. Industry labels must be stable and lowercase snake_case.
2. Do not create duplicate near-synonyms such as `auto`, `automotive`, and `nev` separately.
3. Every smart-factory project should map to one primary industry.
4. Every patent category should map to one primary industry when possible.
5. Use `priority_tier = core | secondary | appendix`.

## Acceptance criteria

```text
25+ industries
all current smart-factory industries mapped
HS6 placeholder mapping added for at least 15 industries
patent keywords added for at least 15 industries
```

---

# Workstream 2 — Ex ante AI exposure and robot compatibility

## Owner

Engineer C.

## Purpose

Build the interaction variables needed for the true design.

## Create

```text
data/processed/industry_ai_exposure_ex_ante_v2.csv
data/processed/industry_robot_compatibility.csv
outputs/tables/table_C1_industry_exposure_scores.csv
docs/source_notes/industry_exposure_robot_compatibility.md
```

## Required columns for exposure file

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

Scores:

```text
0 = low
1 = medium
2 = high
```

Composite:

```text
ai_exposure_ex_ante = row mean of non-missing exposure dimensions
```

## Required columns for robot compatibility file

```text
industry_code
industry
robot_compatibility
robot_compatibility_reason
robot_compatibility_source
confidence
```

## Evidence standard

Exposure scores may use engineering judgment, but every score must have a reason. No score may be inferred from observed smart-factory outcomes.

Good evidence:

```text
IFR or public robot-industry categories
known automation intensity
machine vision relevance
process-control dependence
quality-inspection intensity
industrial software / MES / SCADA relevance
```

Bad evidence:

```text
This industry has many smart factories in our data, so it is high exposure.
```

## Create scripts

```text
scripts/40_build_industry_exposure_v2.py
scripts/41_validate_industry_exposure_v2.py
```

Validation must fail if:

1. Any industry lacks an exposure score.
2. Any main-sample industry has `confidence` missing.
3. Any `classification_reason` is blank.
4. Any exposure source mentions smart-factory outcome counts.

## Acceptance criteria

```text
25+ industries scored
15+ high/medium AI-exposure industries
15+ robot-compatible industries
validation passes
```

---

# Workstream 3 — Industrial AI patent layer

## Owner

Engineer A.

## Purpose

Build the first long-run outcome layer with pre/post pilot-zone variation.

## Recommended source order

1. Use CSMAR/CNRDS/PATSTAT if already accessible.
2. If unavailable, use public patent sources with explicit limitations.
3. For a first version, use targeted Chinese patent search exports for priority industries and cities if full patent universe is too large.

## Minimum raw source strategy

Start with 25 Atlas industries × core industrial AI keywords × 2015–2024.

Keyword groups:

```text
machine_vision: 机器视觉, 图像检测, 缺陷检测, 视觉识别
robotics: 机器人, 机械臂, 运动控制
predictive_maintenance: 预测性维护, 故障诊断, 设备健康
digital_twin: 数字孪生, 仿真, 虚实融合
quality_inspection: 智能质检, 质量检测, 良率
industrial_scheduling: 智能排产, 调度优化, 生产调度
process_control: 过程控制, 参数优化, 闭环控制
smart_logistics: 智能仓储, 路径优化, 智能物流
industrial_software: 工业软件, MES, SCADA, PLC, 工业互联网平台
industrial_foundation_model: 工业大模型, 行业大模型, 垂直大模型
```

## Raw output

```text
data/raw/patents/industrial_ai_patent_records.csv
```

Required columns:

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

## Processing scripts

Create:

```text
scripts/42_parse_industrial_ai_patents.py
scripts/43_build_industrial_ai_patents_city_industry_year.py
scripts/44_validate_industrial_ai_patents.py
```

## Processed long file

```text
data/interim/industrial_ai_patents_long.csv
```

Columns:

```text
patent_id
year
city
province
applicant_name
industry_code
industry
category
industrial_ai_flag
industry_mapping_confidence
city_mapping_confidence
patent_type
source
source_url_or_file
```

## Aggregated file

```text
data/processed/industrial_ai_patents_city_industry_year.csv
```

Columns:

```text
city
province
industry_code
industry
year
ai_patents
industrial_ai_patents
machine_vision_patents
robotics_patents
predictive_maintenance_patents
digital_twin_patents
quality_inspection_patents
industrial_scheduling_patents
process_control_patents
smart_logistics_patents
industrial_software_patents
industrial_foundation_model_patents
invention_patents
utility_model_patents
granted_patents
source_coverage_note
```

## Validation

`44_validate_industrial_ai_patents.py` must check:

1. `year` covers at least 2015–2024 or documents shorter coverage.
2. At least 50 cities have nonzero patents.
3. At least 10 industries have nonzero patents.
4. At least 5 industrial AI categories have nonzero patents.
5. No row is missing city/province/industry/year in the processed main file.
6. Low-confidence mappings are excluded from the main aggregation unless explicitly requested.

## Diagnostic outputs

```text
outputs/tables/table_A1_patent_taxonomy_counts.csv
outputs/tables/table_A2_city_industry_patent_coverage.csv
outputs/tables/table_A3_top_cities_industrial_ai_patents.csv
outputs/tables/table_A4_top_industries_industrial_ai_patents.csv
```

## Acceptance criteria

Minimum:

```text
2015–2024 or 2017–2024 coverage
50+ cities
10+ industries
5+ categories
validation passes
```

Strong:

```text
100+ cities
20+ industries
10+ categories
sufficient city-industry-year variation for FE models
```

---

# Workstream 4 — Smart-factory city-industry-year layer

## Owner

Engineer E.

## Purpose

Convert the existing smart-factory project file into the Atlas city-industry-year format.

## Create

```text
data/processed/smart_factory_city_industry_year.csv
```

## Columns

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

## Script

```text
scripts/45_build_smart_factory_city_industry_year.py
```

## Validation

```text
scripts/46_validate_smart_factory_city_industry_year.py
```

Checks:

1. Total `smart_factory_count` equals 509 across all years.
2. 2024 count equals 235.
3. 2025 count equals 274.
4. External verified count equals 50.
5. Every project maps to one Atlas industry or is marked `unmapped` with reason.

## Acceptance criteria

```text
509 projects assigned to city-industry-year
80%+ high/medium industry mapping confidence
```

---

# Workstream 5 — Atlas v0.2 assembly

## Owner

Engineer E.

## Purpose

Merge pilot zones, exposure, patents, and smart factories into a city-industry-year panel.

## Create

```text
data/processed/china_ai_diffusion_atlas_city_industry_year.csv
outputs/tables/table_E1_atlas_coverage.csv
outputs/tables/table_E2_atlas_missingness.csv
outputs/tables/table_E3_diffusion_index_components.csv
```

## Script

```text
scripts/47_build_atlas_v02.py
scripts/48_validate_atlas_v02.py
```

## Required columns

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

If procurement is not ready, include columns with zeros/missing and set source flag:

```text
procurement_layer_status = pending
```

## Index v0.2

Create a provisional equal-weighted index:

```text
aid_equal_index = mean(z(smart_factory_count), z(industrial_ai_patents), z(post_pilot × ai_exposure_ex_ante), z(robot_compatibility × ai_exposure_ex_ante))
```

Do not include procurement until procurement layer validates.

## Validation

`48_validate_atlas_v02.py` must check:

1. Unique city-industry-year rows.
2. Coverage by year.
3. Coverage by layer.
4. Number of cities, industries, and years.
5. No duplicate city-industry-year keys.
6. No missing exposure for main industries.
7. Smart-factory total matches 509.
8. Patent totals match patent layer.

## Acceptance criteria

Minimum:

```text
50+ cities
20+ industries
2015–2024 or 2017–2025 coverage
patent layer + smart-factory layer merged
```

Strong:

```text
100+ cities
25+ industries
2015–2025 panel
```

---

# Workstream 6 — First Atlas models

## Owner

Econometrics engineer.

## Purpose

Produce the first models that make the true paper more than descriptive.

## Create

```text
scripts/49_run_atlas_models_v02.py
outputs/tables/table_F1_pilot_x_ai_exposure_patents.csv
outputs/tables/table_F2_robot_complementarity_patents.csv
outputs/tables/table_F3_pilot_x_ai_exposure_smart_factories.csv
outputs/tables/table_F4_atlas_event_study_patents.csv
outputs/figures/fig_F1_patent_event_study.png
docs/model_interpretation_matrix_atlas.md
```

## Model 1 — patent diffusion

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

## Model 2 — robot complementarity

```text
industrial_ai_patents_cit = beta * post_pilot_ct × ai_exposure_i × robot_compatibility_i
                           + fixed effects
                           + error_cit
```

## Model 3 — smart-factory adoption

```text
smart_factory_count_cit = beta * post_pilot_ct × ai_exposure_i
                         + city_industry_FE
                         + industry_year_FE
                         + error_cit
```

Because smart factories are 2024–2025 only, label this as adoption concentration, not pre/post causal evidence.

## Model 4 — event study for patents only

```text
industrial_ai_patents_cit = sum_k beta_k * 1[years_since_pilot = k] × ai_exposure_i
                           + city_industry_FE
                           + province_year_FE
                           + industry_year_FE
                           + error_cit
```

Window:

```text
k = -4, -3, -2, -1, 0, 1, 2, 3, 4
```

Omit `k = -1`.

Only run for cities with valid pilot timing and sufficient pre-period patent data.

## Required metadata columns in every output table

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

## Claim tiers

Use:

```text
baseline_association
suggestive_mechanism
robust_association
not_supported
```

Do not label any Atlas Phase 1 model as causal unless pre-trends are acceptable and identification assumptions are documented.

## Acceptance criteria

The first Atlas model sprint succeeds if at least one model shows interpretable variation and all model tables pass validation.

Success result:

```text
Pilot-zone × AI-exposure is positive for industrial AI patenting after pilot designation.
```

Excellent result:

```text
Pilot-zone × AI-exposure × robot-compatibility is positive, suggesting diffusion is strongest where AI has complementary production capital.
```

If coefficients are null:

Write the paper honestly:

```text
Smart-factory adoption is spatially concentrated, but the patent layer does not show a strong post-pilot response in AI-exposed industries.
```

---

# Workstream 7 — Procurement Layer Phase 1B

## Owner

Engineer B.

## Timing

Start after patent and exposure layers are stable. Procurement is high-value but slower and noisier.

## Narrow scope first

Use three provinces first:

```text
Jiangsu
Zhejiang
Guangdong
```

Years:

```text
2020–2025
```

Search only industrial AI and compute terms first:

```text
智能制造
工业互联网
机器视觉
智能质检
预测性维护
数字孪生
工业机器人
智能调度
智能物流
工业软件
智算中心
AI服务器
GPU服务器
```

## Create

```text
data/raw/procurement/procurement_raw_targeted_phase1.csv
data/processed/industrial_ai_procurement_city_industry_year.csv
```

## Minimum acceptance

```text
500 notices reviewed
100 retained industrial AI or compute records
all retained rows have source_url
5+ city-year observations with nonzero industrial AI procurement
```

## Strong acceptance

```text
2,000 notices reviewed
500 retained records
10+ cities
2018–2025 or 2020–2025 coverage
```

---

# Makefile targets to add

After scripts are implemented, add:

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

# Paper integration after Phase 1

Create:

```text
paper/draft_atlas_v1.md
paper/atlas_results_memo.md
paper/atlas_red_team_memo.md
paper/atlas_claim_table_map.csv
paper/atlas_reviewer_snapshot.md
```

The current `paper/draft_v1.md` becomes the measurement module.

New paper structure:

1. Frontier-diffusion puzzle.
2. Conceptual framework: diffusion state.
3. Institutional background: AI+, pilot zones, smart factories, industrial internet, procurement.
4. China AI Diffusion Atlas.
5. Stylized facts: spatial, sectoral, institutional concentration.
6. Pilot zones × AI-exposed industries.
7. Industrial AI patents as diffusion outcome.
8. Smart-factory recognition as adoption outcome.
9. Robot complementarity.
10. Procurement mechanism if ready.
11. Export relevance/upgrading if ready.
12. Limits and claim tiers.

---

# Phase 1 final gate

Run:

```bash
make pcs
make atlas-phase1
python scripts/50_atlas_status.py --json
```

Create `scripts/50_atlas_status.py` to report:

```text
pcs_ready
atlas_ready
n_cities
n_industries
years_min
years_max
patent_layer_ready
smart_factory_layer_ready
exposure_layer_ready
procurement_layer_ready
atlas_models_ready
main_result_summary
forbidden_claim_flags
```

The Atlas sprint is ready for paper integration only when:

```text
exposure_layer_ready = true
patent_layer_ready = true
smart_factory_layer_ready = true
atlas_models_ready = true
pcs_ready = true
```

Procurement can be `pending` for Phase 1, but it must be clearly marked as the next mechanism layer.
