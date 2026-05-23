# Atlas Phase 2 — Real Evidence Instructions

## Verdict

The repo now has a working Atlas engineering scaffold, but the true-vision paper is not yet empirically achieved.

The current Atlas gate says ready because the software artifacts exist and validators pass. That is not the same as evidence readiness. The patent layer is currently fixture-backed. The current `paper/draft_atlas_v1.md` correctly states that the patent layer uses repository fixture microdata until CNIPA export is added.

Phase 2 has one purpose:

```text
Replace fixture-backed Atlas evidence with real patent/procurement/export evidence while preserving all PCS gates.
```

## Current state

### PCS measurement paper

Status: submission-ready.

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
50 external verified
70/70 audit decisions
Tables A-I present
Table I appendix only
Strict Table 5 skipped by design
```

### Atlas Phase 1

Status: engineering-ready but not evidence-ready.

Current Atlas status:

```text
atlas_ready = true
n_cities = 162
n_industries = 21
years = 2015-2025
```

But the current main result is not usable as the true paper result:

```text
Pilot-zone × AI-exposure -> industrial AI patents: coef negative, p-value unavailable.
```

Reasons:

1. Patent layer is fixture microdata.
2. Standard errors are undefined in the saturated FE model.
3. Poisson models fail or produce empty coefficients.
4. Smart-factory interaction results are null.

## Non-negotiable rule

Do not write the true Diffusion State paper from fixture patent data.

The current Atlas can be described only as:

```text
An operational software scaffold for the China AI Diffusion Atlas.
```

It cannot support claims about real patent diffusion until real patent exports are ingested.

---

# Phase 2 priority order

1. Add a no-fixture evidence gate.
2. Replace fixture patent file with real CNIPA/Lens/Google Patents/CNKI/CSMAR data.
3. Re-estimate Atlas models with valid standard errors.
4. Add diagnostic tables proving patent layer credibility.
5. Start targeted procurement only after real patents are working.
6. Update `paper/draft_atlas_v1.md` only after real evidence is ingested.

---

# Workstream 1 — Add no-fixture evidence gate

## Owner

Engineering lead.

## Purpose

Prevent the repo from claiming `atlas_ready = true` when the data are fixture-backed.

## Create

```text
scripts/55_validate_no_fixture_patents.py
src/diffusion_state/validate_no_fixture_patents.py
```

## The validator must fail if any of these are true

```text
patent_id matches CN2015*, CN2016*, ... sequential synthetic IDs
applicant_name contains 智造科技有限公司
source_url_or_file points to data/raw/patents/industrial_ai_patent_records.csv for all rows
source is cnipa_micro_export but no external source file is documented
patent_title contains systematic generated templates by year
abstract equals claims_or_description for most rows
```

## Add output

```text
paper/atlas_evidence_gate_report.json
```

Fields:

```text
fixture_patents_detected
real_patent_source_present
n_raw_patent_records
n_unique_patent_ids
n_source_files
source_files
patent_source_status
```

## Add Makefile target

```make
atlas-evidence-check:
	$(PYTHON) scripts/55_validate_no_fixture_patents.py
```

## Update atlas status

Modify `scripts/50_atlas_status.py` / `src/diffusion_state/atlas_status.py` so it reports both:

```text
atlas_software_ready
atlas_evidence_ready
```

Do not set `atlas_phase1_ready = true` unless both are true.

## Acceptance criteria

Current repo should fail this new gate until fixture patents are replaced.

Expected current status:

```text
atlas_software_ready = true
atlas_evidence_ready = false
fixture_patents_detected = true
```

After real patents:

```text
atlas_software_ready = true
atlas_evidence_ready = true
fixture_patents_detected = false
```

---

# Workstream 2 — Replace fixture patent data with real patents

## Owner

Engineer A.

## Purpose

Create a real industrial AI patent layer with city-industry-year variation.

## Acceptable source options

Use the best accessible source. Recommended order:

1. CNIPA / CNKI / CNRDS / CSMAR export if institutional access exists.
2. Lens export or API if available.
3. Google Patents export/search, with documented limitations.
4. DeepInnovationAI / CSET as validation or supplemental layer, not as a full city-level replacement unless applicant location is available.

Google Patents indexes patents and applications from many patent offices, including CNIPA, so it can be a practical public fallback for targeted exports if institutional sources are unavailable. The Lens is also a free/nonprofit patent and scholarly search platform. DeepInnovationAI is a recent large AI patent dataset, but it must be checked for fields needed for city-level applicant location before it can serve as the Atlas patent layer.

## Raw file format

Replace the fixture file with one or more real raw files under:

```text
data/raw/patents/
```

Allowed filenames:

```text
cnipa_industrial_ai_patents_2015_2024_part*.csv
lens_industrial_ai_patents_2015_2024_part*.csv
google_patents_industrial_ai_patents_2015_2024_part*.csv
```

Do not name the real file only `industrial_ai_patent_records.csv` unless it is built from documented exports. Keep the original export filenames.

## Required raw columns

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

If a source lacks `applicant_city`, derive it from applicant address, but preserve:

```text
city_mapping_confidence
geocode_evidence
```

## Search strategy

Use query groups rather than one giant AI query.

### Industrial AI core

```text
机器视觉 OR 图像检测 OR 缺陷检测 OR 视觉识别
工业机器人 OR 机械臂 OR 运动控制
预测性维护 OR 故障诊断 OR 设备健康
数字孪生 OR 仿真 OR 虚实融合
智能质检 OR 质量检测 OR 良率
智能排产 OR 调度优化 OR 生产调度
过程控制 OR 参数优化 OR 闭环控制
智能仓储 OR 路径优化 OR 智能物流
工业软件 OR MES OR SCADA OR PLC OR 工业互联网平台
工业大模型 OR 行业大模型 OR 垂直大模型
```

### Industry-specific groups

```text
semiconductors: 半导体 OR 集成电路 OR 晶圆 OR 光刻 OR 封装 OR 量测
batteries: 锂电 OR 电池 OR 电芯 OR 极片 OR 化成 OR 分容
automotive: 汽车 OR 新能源汽车 OR 整车 OR 零部件
chemicals: 化工 OR 石化 OR 反应釜 OR 工艺参数
pharmaceuticals: 制药 OR GMP OR 药品包装 OR 生物药
steel: 钢铁 OR 冶金 OR 炼钢 OR 轧钢
robotics: 工业机器人 OR 协作机器人 OR 机械臂
logistics: 智能仓储 OR AGV OR 分拣 OR 物流机器人
```

## Search filters

```text
country/publication authority: CN
application year: 2015-2024
patent/application type: invention + utility model, record separately
applicant location: China
```

## Minimum export target

The first real export should target:

```text
2015-2024
50+ cities
10+ industries
5+ industrial AI categories
at least 2,000 raw patent records before filtering
at least 500 industrial AI records after filtering
```

Strong target:

```text
20,000+ raw patent records
5,000+ industrial AI records
100+ cities
20+ industries
10+ categories
```

## Processing command

After files are placed:

```powershell
make atlas-patents
python scripts/55_validate_no_fixture_patents.py
python scripts/50_atlas_status.py --json
```

## Acceptance criteria

```text
fixture_patents_detected = false
patent_layer_ready = true
n_unique_patent_ids >= 500
n_cities >= 50
n_industries >= 10
years_min <= 2017
years_max >= 2024
```

---

# Workstream 3 — Fix Atlas model estimation

## Owner

Econometrics engineer.

## Current issue

The current F1/F2 models have coefficients but no standard errors or p-values. Poisson fails in several places. That means the model table is not publication-ready even after real patents arrive.

## Required changes

### Add pre-model diagnostics

Create:

```text
outputs/tables/table_F0_atlas_model_diagnostics.csv
```

Fields:

```text
model_name
n_obs
n_nonzero_outcome
n_cities
n_industries
n_years
n_city_industry_cells
n_singleton_fe_cells
interaction_mean
interaction_sd
interaction_nonzero_share
outcome_mean
outcome_nonzero_share
can_estimate
failure_reason
```

### Add robust fallback model hierarchy

For patent outcomes, estimate in this order:

1. OLS log1p patents with city FE, industry FE, year FE.
2. OLS log1p patents with city-industry FE and year FE.
3. OLS log1p patents with city-industry FE and province-year FE.
4. Saturated FE model only if standard errors are defined.
5. Poisson only if convergence and covariance are valid.

Do not make the saturated model the only main estimate.

### Required model outputs

```text
outputs/tables/table_F1a_pilot_x_ai_exposure_patents_baseline.csv
outputs/tables/table_F1b_pilot_x_ai_exposure_patents_fe_ladder.csv
outputs/tables/table_F1c_pilot_x_ai_exposure_patents_saturated.csv
outputs/tables/table_F2_robot_complementarity_patents.csv
outputs/tables/table_F4_atlas_event_study_patents.csv
```

## Required metadata columns

Every model row must include:

```text
model
term
coef
std_err
p_value
n_obs
n_nonzero_outcome
n_cities
n_industries
years
fixed_effects
sample_rule
estimator_status
claim_tier
interpretation
not_supported_claims
```

## Failure rule

If `std_err` or `p_value` is missing, set:

```text
estimator_status = failed_covariance
claim_tier = not_supported
```

Do not let `atlas_ready = true` depend on failed-covariance models.

## Acceptance criteria

At least one F1 model must have:

```text
std_err non-missing
p_value non-missing
n_nonzero_outcome >= 100
n_cities >= 50
n_industries >= 10
```

---

# Workstream 4 — Validate and harden exposure scores

## Owner

Engineer C.

## Current status

Exposure and robot compatibility seeds exist. They are useful but currently rely heavily on engineering judgment and broad source labels.

## Required improvements

1. Add `source_url_or_citation` column.
2. Add `not_outcome_derived = true` column for every row.
3. Add a separate `exposure_version = v2_ex_ante_manual` column.
4. Add sensitivity versions:

```text
ai_exposure_binary_high
ai_exposure_rank
ai_exposure_leave_out_machine_vision
ai_exposure_leave_out_robotics
```

## Output

```text
data/processed/industry_ai_exposure_ex_ante_v2.csv
outputs/tables/table_C2_exposure_sensitivity_versions.csv
```

## Acceptance criteria

```text
All rows have source_url_or_citation
All rows have classification_reason
All rows have not_outcome_derived = true
Sensitivity exposure versions built
```

---

# Workstream 5 — Smart-factory Atlas layer red-team

## Owner

Engineer E.

## Current status

The smart-factory city-industry-year builder exists. It should be red-teamed.

## Required checks

Add:

```text
outputs/tables/table_SF1_smart_factory_industry_mapping_audit.csv
outputs/tables/table_SF2_smart_factory_city_industry_top_cells.csv
```

Check:

1. All 509 projects map to Atlas industries or explicit `unmapped`.
2. Legacy-to-Atlas mapping is documented for every legacy code.
3. External verified rows remain 50 after aggregation.
4. Project-level industry confidence is preserved.
5. No project is double-counted across industries.

## Acceptance criteria

```text
sum(smart_factory_count) = 509
unique project_id count = 509 before aggregation
external_verified_count = 50
high/medium industry mapping confidence >= 80%
```

---

# Workstream 6 — Procurement Phase 1B starts only after real patents

## Owner

Engineer B.

## Trigger

Start only after:

```text
fixture_patents_detected = false
patent_layer_ready = true
at least one F1 model has valid standard errors
```

## Scope

First three provinces:

```text
Jiangsu
Zhejiang
Guangdong
```

Years:

```text
2020-2025
```

Search terms:

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

## Minimum acceptance

```text
500 notices reviewed
100 retained industrial AI or compute records
all retained rows have source_url
5+ city-year observations with nonzero industrial AI procurement
```

---

# Workstream 7 — Paper updates

## Owner

Paper owner.

## Current draft status

`paper/draft_atlas_v1.md` is correct to say the Atlas is fixture-backed. Do not promote it.

## After real patents are ingested

Update:

```text
paper/draft_atlas_v1.md
paper/atlas_results_memo.md
paper/atlas_red_team_memo.md
paper/atlas_claim_table_map.csv
paper/atlas_reviewer_snapshot.md
```

## Allowed claim if real F1 is positive and valid

```text
Pilot-zone designation is associated with stronger subsequent industrial AI patenting in AI-exposed industries.
```

## Allowed claim if robot complementarity is positive and valid

```text
The association is stronger in robot-compatible industries, suggesting that AI diffusion depends on complementary production systems.
```

## Allowed claim if results stay negative/null

```text
The Atlas provides a validated measurement infrastructure, but the real patent layer does not support a post-pilot increase in AI-exposed industrial patenting.
```

## Forbidden claims

```text
Pilot zones caused productivity growth.
AI diffusion caused export upgrading.
China has already experienced the next productivity shock.
Patent counts prove innovation quality.
The fixture-backed Atlas results are empirical evidence.
```

---

# Final Phase 2 gates

Run:

```powershell
make pcs
make atlas-phase1
make atlas-evidence-check
python scripts/50_atlas_status.py --json
```

Evidence-ready status requires:

```text
pcs_ready = true
atlas_software_ready = true
atlas_evidence_ready = true
fixture_patents_detected = false
patent_layer_ready = true
atlas_models_ready = true
at least one F1 model has valid std_err and p_value
forbidden_claim_flags = []
```

Until this passes, the true-vision paper is not ready for submission.
