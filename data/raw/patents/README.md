# Patent raw data (Workstream A)

Place China patent microdata here for the Atlas industrial AI patent layer.

## Required for city-industry-year panel

Drop one or more files matching:

- `cnipa_*.csv` or `cnipa_*.csv.gz` (CNIPA / national patent database export)
- `patents_normalized*.csv` (repo standard schema)

Minimum columns (Chinese CNIPA names are auto-mapped):

- Application ID (`申请号`)
- Application year (`申请年份` or `申请日`)
- Applicant city (`申请人城市`)
- Applicant province (`申请人省份`)
- Patent title (`专利名称`)
- Abstract (`摘要文本`)
- IPC (`IPC分类号` or `IPC主分类号`)

## Optional validation source

The build script can download CSET 1790 AI patent index (~5 MB) for taxonomy validation tables. CSET rows do not include applicant city and are excluded from the main city-industry-year panel.

## Build

```bash
make patents
```

## Data sources (priority)

1. CSMAR / CNRDS AI patent database (institutional)
2. CNIPA / PATSTAT / Lens / Google Patents exports
3. DeepInnovationAI (Figshare; no applicant city in base file)
4. CSET 1790 (validation only; downloaded automatically if no CNIPA files)

See `docs/source_notes/industrial_ai_patents.md`.
