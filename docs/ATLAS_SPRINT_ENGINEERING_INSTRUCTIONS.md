# Atlas Sprint Engineering Instructions

## Purpose

This sprint upgrades the project from a hub-centered smart-factory measurement paper into the full **China AI Diffusion Atlas** paper.

The current paper is scientifically honest but too narrow for the full vision. It measures:

- AI pilot zones;
- MIIT excellence-level smart-factory recognition;
- city-resolution evidence classes;
- hub concentration;
- appendix public-controls robustness.

The true paper must measure whether China’s AI diffusion architecture predicts industrial upgrading. The new target is a city-industry-year dataset that links policy, procurement, industrial AI patents, smart factories, robot/AI exposure, and export-relevant outcomes.

## Target paper thesis

China’s AI advantage may lie less in frontier model leadership than in a state-guided capacity to embed AI into production, logistics, procurement, industrial robotics, smart factories, and local development systems at national scale.

## New empirical object

Build:

```text
data/processed/china_ai_diffusion_atlas_city_industry_year.csv
```

Unit:

```text
city × industry × year
```

Target coverage:

```text
2015–2025
```

Minimum viable coverage:

```text
2018–2025
```

Industries:

```text
30–40 manufacturing / advanced-industrial sectors
```

The Atlas must support these core questions:

1. Do AI pilot zones predict industrial AI diffusion in AI-exposed industries?
2. Does industrial AI diffusion appear through procurement, patents, and smart-factory recognition?
3. Is diffusion concentrated where AI complements robotics, machine vision, quality control, logistics, and process optimization?
4. Are high-diffusion sectors more export-relevant or associated with export upgrading?

## Core design

Preferred model:

```text
Outcome_cit = beta * PostPilot_ct × AIExposure_i
            + city_industry_FE
            + province_year_FE
            + industry_year_FE
            + error_cit
```

Outcomes, in order:

```text
industrial_ai_patents_cit
industrial_ai_procurement_count_cit
industrial_ai_procurement_value_cit
smart_factory_count_cit
export_relevance_or_upgrading_it
```

Mechanism model:

```text
Outcome_cit = beta * PostPilot_ct × AIExposure_i × RobotCompatibility_i
            + fixed effects
            + error_cit
```

The paper should not claim that all pilot cities grow because of designation. It should test whether AI-exposed and robot-compatible industries inside pilot cities show stronger diffusion.

---

# Workstream 0 — Preserve current validated measurement backbone

## Owner

Engineering lead.

## Goal

Do not break the current paper backbone while building the Atlas.

## Current backbone to preserve

```text
AI pilot zones
MIIT excellence-level smart factories
city-resolution evidence classes
B1/B2 audit and external verification
hub-exclusion robustness
Table I appendix public controls
```

## Required branch discipline

Create a new branch locally:

```bash
git checkout main
git pull origin main
git checkout -b atlas-sprint-v02
```

Do not delete or weaken:

```text
paper/draft_v1.md
paper/main_tables/
paper/results_memo.md
paper/reviewer_results_snapshot.md
paper/red_team_memo.md
paper/claim_table_map.csv
```

## Acceptance gate

Before starting and after every major merge:

```bash
make validate-geo
make validate-audit
make public-fallback-controls
make main-tables
make production-check
make validate-sprint
python scripts/15_pcs_status.py
```

Expected:

```text
509/509 projects assigned
102 official-location exact
357 rule-based inference
50 external verified
70/70 audit decisions
Table I present
Strict Table 5 skipped by design
```

---

# Workstream A — Industrial AI patent layer

## Owner

Engineer A.

## Purpose

Create a long-run city-industry-year measure of applied industrial AI innovation. This is the highest-value addition because it creates time variation before and after pilot-zone designation.

## Output files

```text
data/raw/patents/
data/interim/industrial_ai_patents_long.csv
data/processed/industrial_ai_patents_city_industry_year.csv
outputs/tables/table_A1_patent_taxonomy_counts.csv
outputs/tables/table_A2_city_industry_patent_coverage.csv
docs/source_notes/industrial_ai_patents.md
```

## Acceptable data sources

Use the best available source in this order:

1. CSMAR / CNRDS AI patent database if accessible.
2. CNIPA / PATSTAT / Lens / Google Patents exports.
3. DeepInnovationAI public patent dataset.
4. CSET AI patent dataset for historical validation.

If using public sources, document limitations explicitly.

## Required raw columns

At minimum, ingest records with:

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
```

If city is not provided, geocode from applicant address or registry fields. Keep a geocoding evidence column.

## Industrial AI taxonomy

Classify patents into these binary categories:

```text
machine_vision
robotics
predictive_maintenance
digital_twin
quality_inspection
industrial_scheduling
process_control
smart_logistics
industrial_software
industrial_foundation_model
semiconductor_manufacturing_ai
battery_manufacturing_ai
chemical_process_ai
```

Keyword seeds:

```text
机器视觉, 图像检测, 缺陷检测, 视觉识别
机器人, 机械臂, 运动控制
预测性维护, 故障诊断, 设备健康
数字孪生, 仿真, 虚实融合
智能质检, 质量检测, 良率
智能排产, 调度优化, 生产调度
过程控制, 参数优化, 闭环控制
智能仓储, 路径优化, 智能物流
工业软件, MES, SCADA, PLC, 工业互联网平台
工业大模型, 行业大模型, 垂直大模型
半导体, 晶圆, 光刻, 封装, 量测
电池, 锂电, 极片, 电芯, 化成, 分容
化工, 反应釜, 工艺参数, 催化, 配方优化
```

## Industry mapping

Map every patent to one Atlas industry using:

```text
data/seed/industry_crosswalk_atlas.csv
```

If no precise industry is available, map from keywords and applicant sector. Add:

```text
industry_mapping_confidence = high | medium | low
```

Low-confidence mappings must be excluded from main models and retained for appendix sensitivity.

## Processed output schema

```text
city
province
industry
industry_code
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
semiconductor_manufacturing_ai_patents
battery_manufacturing_ai_patents
chemical_process_ai_patents
invention_patents
utility_model_patents
granted_patents
citation_weighted_patents
pct_or_family_patents
source
coverage_note
```

## Quality checks

Create:

```text
scripts/30_build_industrial_ai_patents.py
scripts/31_validate_patent_layer.py
```

Validation must check:

1. Years are within target range.
2. City/province fields are non-empty for at least 80% of records.
3. Industry mapping confidence is reported.
4. No raw patent count is used without industrial AI category.
5. Main panel excludes low-confidence industry mappings.

## Acceptance criteria

Minimum acceptable first version:

```text
2015–2024 coverage
at least 50 cities
at least 10 industries
at least 5 industrial AI categories populated
```

Strong version:

```text
2015–2024 coverage
100+ cities
20+ industries
all major categories populated
city-industry-year panel ready for fixed effects
```

## Paper claim enabled

Allowed after validation:

```text
Industrial AI patenting provides a long-run applied-innovation layer for the China AI Diffusion Atlas.
```

Forbidden:

```text
Higher patent counts prove higher AI quality.
```

---

# Workstream B — Industrial AI procurement layer

## Owner

Engineer B.

## Purpose

Measure the state-demand and adoption channel. Procurement is the key mechanism that makes the diffusion state concept operational.

## Scope

Start targeted, not national.

Priority geographies:

```text
Jiangsu
Zhejiang
Guangdong
Shanghai
Beijing
Chongqing
Hubei
Sichuan
Anhui
Shaanxi
Hunan
```

Target years:

```text
2018–2025
```

Minimum viable years:

```text
2020–2025
```

## Sources

Use:

```text
China Government Procurement Network
China Tendering and Bidding Public Service Platform
provincial procurement portals
municipal procurement portals
SOE procurement portals where available
industrial park procurement pages
```

## Search taxonomy

### Industrial AI terms

```text
智能制造
工业互联网
机器视觉
智能质检
预测性维护
数字孪生
工业机器人
智能调度
智能排产
智能物流
工业软件
设备健康管理
工业大脑
```

### Compute/infrastructure terms

```text
智算中心
算力中心
算力券
GPU服务器
AI服务器
国产AI芯片
昇腾
寒武纪
沐曦
燧原
摩尔线程
```

### General AI terms

```text
人工智能
大模型
生成式人工智能
算法平台
深度学习
机器学习
```

### Surveillance/governance terms for exclusion or separate category

```text
人脸识别
智能安防
公安大数据
视频结构化
智慧城市
城市大脑
```

Do not mix industrial AI and surveillance AI in the main measure.

## Raw output schema

```text
data/raw/procurement/procurement_raw_<source>_<year>.csv
```

Fields:

```text
source
source_url
crawl_date
notice_date
award_date
province
city
buyer
buyer_type
supplier
project_title
project_description
contract_amount
currency
notice_type
keyword_query
keyword_category
industrial_ai_flag
compute_flag
surveillance_ai_flag
general_ai_flag
manufacturing_relevance
industry
industry_mapping_confidence
raw_text_path
```

Buyer type values:

```text
government
SOE
university
hospital
industrial_park
public_utility
public_security
other_public
private_or_unknown
```

## Processed output schema

```text
data/processed/industrial_ai_procurement_city_industry_year.csv
```

Fields:

```text
city
province
industry
industry_code
year
industrial_ai_procurement_count
industrial_ai_procurement_value
compute_procurement_count
compute_procurement_value
surveillance_ai_procurement_count
surveillance_ai_procurement_value
general_ai_procurement_count
general_ai_procurement_value
industrial_ai_procurement_share
procurement_diversity_index
buyer_type_diversity
source_coverage_note
```

## Quality rules

1. Main diffusion index uses industrial AI procurement only.
2. Surveillance/governance procurement is tracked but excluded from industrial diffusion.
3. Contract amount must be numeric or missing; never impute amount.
4. City must be buyer city, not supplier city, unless buyer city is missing and the project location is explicit.
5. Keep raw source URLs for every row.

## Scripts

Create:

```text
scripts/32_fetch_procurement_targeted.py
scripts/33_parse_procurement_records.py
scripts/34_build_procurement_city_industry_year.py
scripts/35_validate_procurement_layer.py
```

## Acceptance criteria

Minimum acceptable first version:

```text
500+ procurement notices or awards reviewed
100+ industrial AI-relevant records retained
5+ provinces/cities
2020–2025 coverage
all rows have source_url
```

Strong version:

```text
2,000+ records reviewed
500+ retained industrial AI records
10+ target geographies
industry-year aggregation ready
```

## Paper claim enabled

Allowed:

```text
Industrial AI procurement provides a state-demand mechanism for AI diffusion.
```

Forbidden:

```text
Procurement caused commercial AI success.
```

unless a separate firm-level design is built.

---

# Workstream C — AI exposure and robot compatibility

## Owner

Engineer C.

## Purpose

Build ex ante industry exposure variables for credible interaction designs.

## Outputs

```text
data/seed/industry_crosswalk_atlas.csv
data/processed/industry_ai_exposure_ex_ante_v2.csv
data/processed/industry_robot_compatibility.csv
outputs/tables/table_C1_industry_exposure_scores.csv
docs/source_notes/industry_exposure_robot_compatibility.md
```

## Atlas industry list

Create 30–40 sectors. Minimum list:

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

## Exposure dimensions

For each industry, assign 0–2 scores:

```text
machine_vision_exposure
robotics_exposure
predictive_maintenance_exposure
digital_twin_exposure
process_control_exposure
quality_inspection_exposure
smart_logistics_exposure
industrial_software_exposure
```

Composite:

```text
ai_exposure_ex_ante = mean of exposure dimensions
robot_compatibility = robotics_exposure or external robot-intensity proxy
```

## Evidence standards

Each score needs:

```text
classification_reason
classification_source
confidence = high | medium | low
```

Use sources in this order:

1. IFR industry robot categories if accessible.
2. Global patent intensity by industry.
3. O*NET / task-based AI exposure mapped to manufacturing tasks.
4. Engineering judgment with explicit notes.

## Acceptance criteria

1. No exposure score may be derived from the smart-factory outcome itself.
2. Main models use only high/medium-confidence industries.
3. Low-confidence industries are retained for appendix sensitivity.
4. The final file is stable and human-readable.

## Paper claim enabled

Allowed:

```text
We test whether pilot-zone effects are stronger in industries with ex ante technological compatibility with industrial AI.
```

---

# Workstream D — BACI and export upgrading layer

## Owner

Engineer D.

## Purpose

Move from descriptive export relevance to a credible export-upgrading module.

## Scope

BACI is country-product-year, not city-product-year. Use it carefully.

Main use:

```text
industry × year export outcomes
```

Optional city link only through industry exposure, not direct city exports unless China Customs or city customs data become available.

## Output files

```text
data/processed/baci_china_hs6_year.csv
data/processed/atlas_industry_export_year.csv
data/processed/industry_hs6_crosswalk_atlas.csv
outputs/tables/table_D1_export_outcomes_by_industry.csv
outputs/tables/table_D2_export_upgrade_models.csv
docs/source_notes/baci_export_upgrading.md
```

## Required BACI variables

```text
year
hs6
export_value
quantity
unit_value
world_export_value
china_market_share
num_destinations
```

Derived outcomes:

```text
log_export_value
log_unit_value
market_share
revealed_comparative_advantage
export_growth_1y
export_growth_3y
unit_value_growth_1y
unit_value_growth_3y
market_share_growth_1y
market_share_growth_3y
```

## Crosswalk

Map Atlas industries to HS6 product groups.

Fields:

```text
industry
industry_code
hs6
hs_description
mapping_confidence
mapping_reason
```

Main models use high/medium mapping only.

## Model

Sector-level first:

```text
ExportUpgrade_i,t+1 = beta * DiffusionIntensity_i,t
                      + industry_FE
                      + year_FE
                      + error_i,t
```

Alternative:

```text
ExportUpgrade_i,t+1 = beta * SmartFactoryShare_i,t
                    + industry_FE
                    + year_FE
                    + error_i,t
```

For now, this is suggestive, not causal.

## Acceptance criteria

1. HS6 crosswalk is documented.
2. Unit values handle zero/missing quantity correctly.
3. Export models are labeled suggestive unless city-industry exposure is merged with credible city outcome data.
4. No causal export claim.

## Paper claim enabled

Allowed:

```text
High-diffusion industries overlap with export-relevant advanced manufacturing sectors and show suggestive export-upgrading patterns.
```

Forbidden:

```text
AI diffusion caused export upgrading.
```

---

# Workstream E — Atlas assembly

## Owner

Engineer E.

## Purpose

Merge all layers into the city-industry-year Atlas.

## Output

```text
data/processed/china_ai_diffusion_atlas_city_industry_year.csv
outputs/tables/table_E1_atlas_coverage.csv
outputs/tables/table_E2_atlas_missingness.csv
outputs/tables/table_E3_diffusion_index_components.csv
outputs/figures/fig_E1_diffusion_index_map.csv
outputs/figures/fig_E2_city_industry_heatmap.csv
docs/source_notes/china_ai_diffusion_atlas.md
```

## Required columns

```text
city
province
industry
industry_code
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
industrial_ai_procurement_count
industrial_ai_procurement_value
compute_procurement_count
surveillance_ai_procurement_count
foreign_trade_relevance
export_value
export_unit_value
export_market_share
source_coverage_flags
```

## Diffusion index

Create two versions:

### Equal-weighted index

```text
AID_equal = z(policy_layer)
          + z(procurement_layer)
          + z(smart_factory_layer)
          + z(industrial_ai_patent_layer)
          + z(robot_or_ai_exposure_layer)
```

Use average of available standardized components.

### PCA/factor index

```text
AID_pca = first principal component of available diffusion components
```

Only estimate PCA on rows with sufficient components. Record coverage.

## Component definitions

```text
policy_layer = post_pilot or local policy intensity if later added
procurement_layer = log1p(industrial_ai_procurement_count/value)
smart_factory_layer = log1p(smart_factory_count)
industrial_ai_patent_layer = log1p(industrial_ai_patents)
robot_or_ai_exposure_layer = robot_compatibility × ai_exposure_ex_ante
```

## Scripts

Create:

```text
scripts/36_build_atlas_city_industry_year.py
scripts/37_build_diffusion_index.py
scripts/38_validate_atlas.py
```

## Validation

`38_validate_atlas.py` must check:

1. Unique city-industry-year rows.
2. No missing city/province/year/industry in main sample.
3. Coverage by year and layer.
4. Diffusion index built only from valid components.
5. Claim-tier tags for each layer.

## Acceptance criteria

Minimum Atlas v0.2:

```text
100+ cities
20+ industries
2018–2025 or 2015–2024 coverage
smart factories + patents + procurement or patents + smart factories populated
```

Strong Atlas:

```text
150+ cities
30+ industries
2015–2025
smart factories + patents + procurement + export relevance populated
```

---

# Workstream F — Models and tables

## Owner

Econometrics engineer.

## Purpose

Produce the models that move the paper beyond descriptive hub concentration.

## Required outputs

```text
outputs/tables/table_F1_pilot_x_ai_exposure_patents.csv
outputs/tables/table_F2_pilot_x_ai_exposure_procurement.csv
outputs/tables/table_F3_pilot_x_ai_exposure_smart_factories.csv
outputs/tables/table_F4_robot_complementarity_models.csv
outputs/tables/table_F5_diffusion_index_export_upgrading.csv
outputs/figures/fig_F1_event_study_patents.png
outputs/figures/fig_F2_event_study_procurement.png
outputs/figures/fig_F3_robot_complementarity.png
docs/model_interpretation_matrix_atlas.md
```

## Main model 1 — patents

```text
industrial_ai_patents_cit = beta * post_pilot_ct × ai_exposure_i
                           + city_industry_FE
                           + province_year_FE
                           + industry_year_FE
                           + error_cit
```

## Main model 2 — procurement

```text
industrial_ai_procurement_count_cit = beta * post_pilot_ct × ai_exposure_i
                                     + city_industry_FE
                                     + province_year_FE
                                     + industry_year_FE
                                     + error_cit
```

## Main model 3 — smart factories

```text
smart_factory_count_cit = beta * post_pilot_ct × ai_exposure_i
                         + city_industry_FE
                         + province_year_FE
                         + industry_year_FE
                         + error_cit
```

Because smart factories are mostly 2024–2025, treat this as adoption-outcome evidence, not long-run event-study evidence.

## Main model 4 — robot complementarity

```text
Outcome_cit = beta * post_pilot_ct × ai_exposure_i × robot_compatibility_i
            + fixed effects
            + error_cit
```

Run for patents and procurement first, smart factories second.

## Main model 5 — export upgrading

```text
ExportUpgrade_i,t+1 = beta * AID_i,t
                    + industry_FE
                    + year_FE
                    + error_it
```

Label suggestive unless a stronger design exists.

## Event studies

Only run event studies for outcomes with pre-treatment time variation:

```text
industrial_ai_patents
industrial_ai_procurement
```

Do not run smart-factory event studies as pre-trend validation unless pre-2024 smart-factory lists are added.

## Acceptance criteria

1. Every table has `claim_tier` column.
2. Every table has `sample_rule` and `fixed_effects` columns.
3. Models with sparse outcomes include count/log/Poisson variants.
4. Event studies report pre-trend diagnostics only for outcomes with pre-treatment variation.
5. No table claims causal treatment effect without pre-trend and identification support.

---

# Workstream G — Paper integration

## Owner

Paper owner.

## Purpose

Convert the current draft into the true vision paper.

## Current draft status

`paper/draft_v1.md` is the measurement module. It is not the final paper.

Rename or preserve as:

```text
paper/draft_measurement_module.md
```

Create:

```text
paper/draft_atlas_v1.md
```

## New paper structure

1. Introduction: frontier-diffusion puzzle.
2. Conceptual framework: the diffusion state.
3. Institutional background: AI+, pilot zones, smart factories, industrial internet, procurement.
4. China AI Diffusion Atlas: data construction and evidence classes.
5. Stylized facts: spatial, sectoral, institutional concentration.
6. Empirical strategy: pilot zones × AI-exposed industries.
7. Results: patents, procurement, smart factories.
8. Mechanisms: procurement, robot complementarity, industrial AI taxonomy.
9. Export relevance and upgrading.
10. Comparison with frontier-model metrics.
11. Limitations and identification boundaries.
12. Conclusion.

## Required contribution statement

Use:

```text
This paper makes three contributions. First, it distinguishes frontier-model advantage from diffusion-system advantage and argues that the economics of AI requires measuring both. Second, it introduces the diffusion state as a political-economic system that converts general-purpose AI capabilities into sector-specific production capabilities through procurement, pilots, standards, industrial platforms, and complementary capital formation. Third, it constructs a city-industry-year dataset on AI diffusion in China and uses policy pilots, industrial AI exposure, procurement, patents, smart-factory recognition, and trade outcomes to study whether state-guided diffusion predicts industrial upgrading.
```

## Acceptance criteria

The paper becomes journal/submission-grade only when it has:

1. A new dataset beyond smart factories alone.
2. At least one long-run diffusion outcome with pre-treatment time variation.
3. A pilot-zone × AI-exposure interaction result.
4. A mechanism layer: procurement or industrial AI patents.
5. A sectoral or export-upgrading outcome, even if suggestive.
6. Clear claim tiers separating descriptive, associational, suggestive, and unsupported claims.

---

# Final sprint success criteria

## Minimum viable true-vision paper

The sprint succeeds if we can report:

```text
We build China AI Diffusion Atlas v0.2, a city-industry-year panel linking AI pilot zones, smart-factory recognition, industrial AI patents, and targeted industrial AI procurement. Pilot-zone cities show stronger post-designation increases in industrial AI patenting and/or procurement in AI-exposed industries, while smart-factory recognition and export relevance concentrate in the same hub-industrial systems.
```

## Strong version

The sprint is excellent if we can report:

```text
The post-pilot increase is strongest in robot-compatible industries, supporting the view that AI diffusion depends on complementary production systems rather than generic AI enthusiasm.
```

## Forbidden claims unless proven

```text
AI pilot zones caused productivity growth.
AI diffusion caused export upgrading.
China has already experienced the next productivity shock.
Pilot designation is randomly assigned.
Procurement contracts causally increased commercial AI output.
Patent counts prove innovation quality.
```

## Immediate command targets

Add Makefile targets after scripts exist:

```make
patents:
	$(PYTHON) scripts/30_build_industrial_ai_patents.py
	$(PYTHON) scripts/31_validate_patent_layer.py

procurement:
	$(PYTHON) scripts/32_fetch_procurement_targeted.py
	$(PYTHON) scripts/33_parse_procurement_records.py
	$(PYTHON) scripts/34_build_procurement_city_industry_year.py
	$(PYTHON) scripts/35_validate_procurement_layer.py

atlas:
	$(PYTHON) scripts/36_build_atlas_city_industry_year.py
	$(PYTHON) scripts/37_build_diffusion_index.py
	$(PYTHON) scripts/38_validate_atlas.py

atlas-models:
	$(PYTHON) scripts/39_run_atlas_models.py
```

# Priority order

1. Industrial AI patents.
2. Ex ante AI exposure and robot compatibility.
3. Atlas assembly.
4. Targeted procurement.
5. Atlas models.
6. Export upgrading.
7. Paper integration.

The first serious empirical upgrade should be patents, because patents provide long-run pre/post variation and can be built faster than a clean national procurement layer.
