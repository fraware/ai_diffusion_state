# Atlas Phase 2 Patent Export and Model Runbook

## Purpose

This runbook is the next execution plan after the no-fixture evidence gate was implemented. The Atlas software pipeline is operational, but the true paper remains blocked until real patent exports replace fixture patent files.

## Current verified state

The correct current status is:

```text
atlas_software_ready = true
atlas_evidence_ready = false
atlas_phase1_ready = false
fixture_patents_detected = true
patent_layer_ready = false
atlas_models_ready = false
```

This is expected and correct. Do not weaken this gate.

## Goal of this sprint

Replace fixture-backed patent evidence with documented real patent exports and produce at least one valid Atlas patent model with non-missing standard errors and p-values.

The sprint is complete only when:

```text
fixture_patents_detected = false
real_patent_source_present = true
patent_layer_ready = true
atlas_evidence_ready = true
atlas_models_ready = true
at least one F1 model has valid std_err and p_value
```

---

# 1. Freeze PCS and Atlas software scaffolding

Before touching patent data:

```powershell
cd c:\Users\mateo\ai_diffusion_state
make pcs
make atlas-phase1
make atlas-evidence-check
python scripts/50_atlas_status.py --json
```

Expected right now:

```text
PCS passes.
Atlas software passes.
Atlas evidence fails because fixture patents are detected.
```

If PCS breaks, fix PCS first. If Atlas software breaks, fix software before data ingestion.

---

# 2. Remove or quarantine fixture patent files from evidence path

Current fixture files are useful for tests but must not feed the evidence pipeline.

Do not delete them if tests depend on them. Instead, move them or make the loader ignore them for evidence builds.

Preferred structure:

```text
data/raw/patents/fixtures/industrial_ai_patent_records.csv
data/raw/patents/fixtures/cnipa_micro.csv
data/raw/patents/fixtures/patent_database.csv
```

Real exports must live directly under:

```text
data/raw/patents/
```

with names such as:

```text
cnipa_industrial_ai_patents_2015_2024_part1.csv
lens_industrial_ai_patents_2015_2024_part1.csv
google_patents_industrial_ai_patents_2015_2024_part1.csv
```

Update the patent loader so it excludes:

```text
*/fixtures/*
*_fixture*.csv
industrial_ai_patent_records.csv if source status is fixture
cnipa_micro.csv
patent_database.csv when used as generated fixture
```

The no-fixture gate must continue to fail if fixture files enter the processed patent layer.

---

# 3. Create patent source manifest

Create:

```text
data/raw/patents/patent_source_manifest.csv
```

Required columns:

```text
source_file
source_platform
export_date
export_owner
query_group
query_string
year_min
year_max
jurisdiction_filter
record_count
contains_applicant_address
contains_city
contains_abstract
contains_claims
license_or_access_note
proprietary_or_public
notes
```

Rules:

1. Every raw patent CSV must have one manifest row.
2. `record_count` must match the file row count.
3. If a file is proprietary, do not commit it unless cleared. Commit a schema sample instead.
4. If the export is public, preserve source URLs or source query documentation.

---

# 4. Real patent export scope

Target years:

```text
2015-2024
```

Optional if available:

```text
2025 partial
```

Jurisdiction:

```text
CN publications/applications or China applicant location
```

Minimum viable export:

```text
2,000+ raw records
500+ retained industrial AI records
50+ cities
10+ industries
5+ industrial AI categories
```

Strong export:

```text
20,000+ raw records
5,000+ retained industrial AI records
100+ cities
20+ industries
10+ categories
```

---

# 5. Query groups

Use query groups, not a single broad AI search.

## Core industrial AI groups

```text
machine_vision: 机器视觉 OR 图像检测 OR 缺陷检测 OR 视觉识别
robotics: 工业机器人 OR 机械臂 OR 运动控制
predictive_maintenance: 预测性维护 OR 故障诊断 OR 设备健康
digital_twin: 数字孪生 OR 仿真 OR 虚实融合
quality_inspection: 智能质检 OR 质量检测 OR 良率
industrial_scheduling: 智能排产 OR 调度优化 OR 生产调度
process_control: 过程控制 OR 参数优化 OR 闭环控制
smart_logistics: 智能仓储 OR 路径优化 OR 智能物流
industrial_software: 工业软件 OR MES OR SCADA OR PLC OR 工业互联网平台
industrial_foundation_model: 工业大模型 OR 行业大模型 OR 垂直大模型
```

## Industry-specific modifiers

Combine core groups with priority industries:

```text
semiconductors: 半导体 OR 集成电路 OR 晶圆 OR 光刻 OR 封装 OR 量测
batteries: 锂电 OR 电池 OR 电芯 OR 极片 OR 化成 OR 分容
automotive: 汽车 OR 新能源汽车 OR 整车 OR 零部件
chemicals: 化工 OR 石化 OR 反应釜 OR 工艺参数
pharmaceuticals: 制药 OR 生物药 OR GMP OR 药品包装
steel: 钢铁 OR 冶金 OR 炼钢 OR 轧钢
logistics: 智能仓储 OR AGV OR 分拣 OR 物流机器人
solar_pv: 光伏 OR 组件 OR 硅片 OR 电池片
shipbuilding: 船舶 OR 船厂 OR 船体 OR 船舶制造
```

Export each query group separately when possible. Preserve `search_keyword` or `query_group` in the raw data.

---

# 6. Required raw schema

Every real export must be normalized to:

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

Additional useful columns:

```text
applicant_country
inventor_city
legal_status
assignee_type
family_id
citation_count
forward_citations
original_language
```

If the source lacks city/province, create:

```text
applicant_city_raw
applicant_province_raw
city_mapping_confidence
geocode_evidence
```

Never silently infer city from firm name unless documented.

---

# 7. Patent ingestion rules

Update or verify:

```text
src/diffusion_state/ingest_patents.py
src/diffusion_state/build_industrial_ai_patents.py
scripts/42_parse_industrial_ai_patents.py
scripts/43_build_industrial_ai_patents_city_industry_year.py
scripts/44_validate_industrial_ai_patents.py
```

The ingestion layer must:

1. Read all real export files listed in `patent_source_manifest.csv`.
2. Exclude fixture paths by default.
3. Deduplicate by `patent_id` and, if available, `family_id`.
4. Prefer application year for timing.
5. Preserve publication/grant year separately.
6. Classify patent categories using title, abstract, claims, IPC/CPC, and query group.
7. Map industry using `industry_crosswalk_atlas.csv`.
8. Mark `industry_mapping_confidence` and `city_mapping_confidence`.
9. Exclude low-confidence rows from main aggregation unless explicitly requested.

---

# 8. Patent validation rules

The validator must pass only if:

```text
n_unique_patent_ids >= 500
n_cities >= 50
n_industries >= 10
years_min <= 2017
years_max >= 2024
fixture_patents_detected = false
real_patent_source_present = true
```

Create diagnostic outputs:

```text
outputs/tables/table_P0_patent_source_manifest_check.csv
outputs/tables/table_P1_patent_category_counts.csv
outputs/tables/table_P2_patent_city_coverage.csv
outputs/tables/table_P3_patent_industry_coverage.csv
outputs/tables/table_P4_patent_year_coverage.csv
outputs/tables/table_P5_patent_mapping_confidence.csv
```

These are required before any paper claim.

---

# 9. Re-run Atlas after real patents

Run:

```powershell
make atlas-patents
make atlas-evidence-check
make atlas-v02
make atlas-models-v02
python scripts/50_atlas_status.py --json
```

Expected before models are interpreted:

```text
fixture_patents_detected = false
real_patent_source_present = true
patent_layer_ready = true
atlas_evidence_ready = true
```

---

# 10. Model interpretation rules

At least one model in the F1 ladder must have:

```text
std_err non-missing
p_value non-missing
n_nonzero_outcome >= 100
n_cities >= 50
n_industries >= 10
estimator_status = ok
```

If not, `atlas_models_ready = false`.

The preferred first-paper result is the baseline FE ladder, not the saturated model:

```text
F1a: city FE + industry FE + year FE
F1b: city-industry FE + year FE
F1c: city-industry FE + province-year FE
F1d: saturated FE only if covariance valid
```

Use saturated FE as robustness, not the only main result.

---

# 11. What to do depending on results

## If F1 is positive and valid

Allowed claim:

```text
Pilot-zone designation is associated with stronger subsequent industrial AI patenting in AI-exposed industries.
```

If F2 is also positive and valid:

```text
The association is stronger in robot-compatible industries, suggesting that AI diffusion depends on complementary production systems.
```

## If F1 is null or negative

Allowed claim:

```text
The Atlas provides a validated measurement infrastructure, but the real patent layer does not support a post-pilot increase in AI-exposed industrial patenting.
```

Then pivot the paper to:

```text
smart-factory adoption is spatially concentrated, while patenting does not show the same post-pilot response.
```

This is still a valuable and honest finding.

## If model inference fails

Allowed claim:

```text
The current patent layer is insufficient for fixed-effect inference; more complete patent coverage or a simpler design is required.
```

Do not report coefficient signs as substantive evidence.

---

# 12. Procurement trigger

Do not start procurement until:

```text
fixture_patents_detected = false
patent_layer_ready = true
at least one F1 model has valid std_err and p_value
```

After that, start procurement Phase 1B:

```text
Jiangsu, Zhejiang, Guangdong
2020-2025
500 notices reviewed
100 retained industrial AI / compute records
all retained rows have source_url
```

---

# 13. Final commands

Evidence sprint final gate:

```powershell
make pcs
make atlas-phase1
make atlas-evidence-check
python scripts/50_atlas_status.py --json
```

Required final status:

```text
pcs_ready = true
atlas_software_ready = true
atlas_evidence_ready = true
atlas_phase1_ready = true
fixture_patents_detected = false
patent_layer_ready = true
atlas_models_ready = true
forbidden_claim_flags = []
```

Only then can `paper/draft_atlas_v1.md` become a true empirical paper draft rather than a software-pipeline draft.
