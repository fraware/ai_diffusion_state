# Atlas Real Patent Data Acquisition Decision

## Verdict

The remaining blocker cannot be solved by more repo engineering. It requires obtaining a real patent export from one of the acceptable patent data sources.

The repo is ready to ingest real files. The evidence path is intentionally empty until real exports are added.

Current correct status:

```text
atlas_software_ready = true
atlas_evidence_ready = false
atlas_phase1_ready = false
fixture_patents_detected = true
patent_source_status = missing_real_exports
n_raw_patent_records = 0
source_files = []
```

## What was checked

### DeepInnovationAI / DeepPatentAI

The arXiv page for DeepInnovationAI links to `DeepPatentAI.csv`, `DeepDiveAI.csv`, and `DeepCosineAI.csv`, and states that DeepPatentAI contains 2,356,204 patent records with 8 field-specific attributes. However, the exposed arXiv `this http URL` links resolve to malformed/broken URLs such as `https://deeppatentai.csv/` when opened directly. This is not a usable direct download path.

The DeepInnovationAI paper says the patent corpus comes from the Intelligent Innovation Dataset (IIDS), which contains nearly 100 million patent records and is publicly available on OpenDataLab at:

```text
https://opendatalab.com/Gracie/IIDS
```

This is the best public dataset lead, but it still requires platform access/download. The repo cannot ingest it until an operator downloads the relevant patent files.

### Google Patents

Google Patents indexes patents and applications from major patent offices, including CNIPA. This makes it useful for targeted patent discovery. However, Google Patents is not, by itself, a clean bulk city-level export path for the Atlas unless the operator can export applicant location/city/address fields or join patent IDs to an address source.

### Lens / PATENTSCOPE / Espacenet

These are plausible public search/export sources. They should be used only if the export includes, or can be joined to, applicant address/city/province fields. Patent ID, title, abstract, and applicant country alone are insufficient for the Atlas city-industry-year panel.

## Source decision tree

### Best path if institutional access exists

Use one of:

```text
CNIPA
CNKI patent database
CNRDS patent database
CSMAR patent database
PATSTAT with applicant geolocation
```

Required export fields:

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

### Best public path

Use OpenDataLab IIDS if the platform export includes applicant information and patent metadata.

Operator task:

1. Open `https://opendatalab.com/Gracie/IIDS`.
2. Log in if required.
3. Download patent-details files covering 2015-2024.
4. Check whether the files include applicant address/city/province.
5. Normalize to the repo schema.
6. Save as:

```text
data/raw/patents/opendatalab_iids_industrial_ai_patents_2015_2024_part1.csv
```

If IIDS only provides patent IDs, titles, abstracts, IPC/CPC, and applicant names without city/address, it is insufficient alone. It can still classify AI patents, but it must be joined to an address source.

### Practical fallback

Use Lens, Google Patents, or PATENTSCOPE to export targeted query results, but only if location fields are available.

Allowed filenames:

```text
data/raw/patents/lens_industrial_ai_patents_2015_2024_part1.csv
data/raw/patents/google_patents_industrial_ai_patents_2015_2024_part1.csv
data/raw/patents/patentscope_industrial_ai_patents_2015_2024_part1.csv
```

If the filename pattern is not currently accepted by `patent_raw_sources.py`, add the pattern deliberately and update tests.

## Minimum viable real export

```text
2,000+ raw records
500+ retained industrial AI records
50+ cities
10+ industries
5+ industrial AI categories
2015-2024 coverage
```

## Strong target

```text
20,000+ raw records
5,000+ retained industrial AI records
100+ cities
20+ industries
10+ industrial AI categories
2015-2024 coverage
```

## Query groups

Use separate exports by query group:

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

Use industry modifiers:

```text
半导体 OR 集成电路 OR 晶圆 OR 光刻 OR 封装 OR 量测
锂电 OR 电池 OR 电芯 OR 极片 OR 化成 OR 分容
汽车 OR 新能源汽车 OR 整车 OR 零部件
化工 OR 石化 OR 反应釜 OR 工艺参数
制药 OR 生物药 OR GMP OR 药品包装
钢铁 OR 冶金 OR 炼钢 OR 轧钢
智能仓储 OR AGV OR 分拣 OR 物流机器人
光伏 OR 组件 OR 硅片 OR 电池片
船舶 OR 船厂 OR 船体 OR 船舶制造
```

## After real files are downloaded

Run:

```powershell
python scripts/58_prepare_patent_source_manifest.py
```

Inspect:

```text
outputs/tables/table_P0_patent_export_schema_diagnostics.csv
```

Then fill and append:

```text
data/raw/patents/patent_source_manifest_draft.csv
```

to:

```text
data/raw/patents/patent_source_manifest.csv
```

Then run:

```powershell
make atlas-patents
make atlas-evidence-check
make atlas-v02
make atlas-models-v02
python scripts/50_atlas_status.py --json
```

Success requires:

```text
fixture_patents_detected = false
real_patent_source_present = true
patent_layer_ready = true
atlas_evidence_ready = true
atlas_models_ready = true
```

## Hard boundary

Do not claim real industrial AI patent diffusion until a real export is present and the evidence gate passes.
