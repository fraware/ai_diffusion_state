# Real industrial AI patent exports (Atlas Phase 2)

The Atlas **software** pipeline accepts patent microdata here. The **evidence gate** (`make atlas-evidence-check`) fails until fixture files are replaced or supplemented with documented real exports.

## Required filenames (examples)

- `cnipa_industrial_ai_patents_2015_2024_part1.csv`
- `lens_industrial_ai_patents_2015_2024_part1.csv`
- `google_patents_industrial_ai_patents_2015_2024_part1.csv`

## Required columns

`patent_id`, `application_year`, `publication_year`, `grant_year`, `applicant_name`, `applicant_city`, `applicant_province`, `applicant_address`, `patent_title`, `abstract`, `claims_or_description`, `ipc_or_cpc`, `patent_type`, `source`, `source_url_or_file`, `search_keyword`

## Minimum acceptable export

- Years 2015–2024
- 2,000+ raw records before filtering; 500+ industrial AI records after filtering
- 50+ cities, 10+ industries, 5+ industrial AI categories

## Priority query groups (CNIPA / Lens / Google Patents)

- 机器视觉 OR 图像检测 OR 缺陷检测 OR 视觉识别
- 工业机器人 OR 机械臂 OR 运动控制
- 预测性维护 OR 故障诊断 OR 设备健康
- 数字孪生 OR 仿真 OR 虚实融合
- 智能质检 OR 质量检测 OR 良率
- 智能排产 OR 调度优化 OR 生产调度
- 过程控制 OR 参数优化 OR 闭环控制
- 智能仓储 OR 路径优化 OR 智能物流
- 工业软件 OR MES OR SCADA OR PLC OR 工业互联网平台
- 工业大模型 OR 行业大模型 OR 垂直大模型

## After placing files

```powershell
make atlas-patent-prep
# Review outputs/tables/table_P0_patent_export_schema_diagnostics.csv
# Complete data/raw/patents/patent_source_manifest_draft.csv -> patent_source_manifest.csv
make atlas-patents
make atlas-evidence-check
make atlas-v02
make atlas-models-v02
python scripts/50_atlas_status.py --json
```

Expected when evidence-ready: `fixture_patents_detected = false`, `atlas_evidence_ready = true`.

## Current fixture files (do not use for paper claims)

- `industrial_ai_patent_records.csv` — repository micro-fixture
- `cnipa_micro.csv` — test fixture

Remove or supersede these with real exports before claiming empirical patent diffusion results.

See `docs/ATLAS_PHASE2_REAL_EVIDENCE_INSTRUCTIONS.md`.
