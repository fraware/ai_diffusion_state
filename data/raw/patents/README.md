# Patent raw data (Workstream A)

Place China patent microdata here for the Atlas industrial AI patent layer.

## IIDS + geography path (Atlas Phase 2)

1. Download IIDS sources: `python scripts/59_download_iids_patent_sources.py --include-sql`
2. Convert filtered export: `make atlas-iids-convert`
3. Build geography supplement from CNIPA/Lens (schema guide):
   `data/raw/patents/cnipa_patent_geography_template.csv`
4. Validate supplement: `make atlas-iids-geo-validate`
5. Build from CNIPA/Lens export: `make atlas-iids-geo-build`
6. Join geography: `make atlas-iids-geo`
7. Orchestrated run: `make atlas-iids-pipeline` (or `--full-chain` after manifest)
8. Complete manifest and run evidence chain per `docs/ATLAS_PHASE2_PATENT_EXPORT_AND_MODEL_RUNBOOK.md`

Target evidence file:

- `opendatalab_iids_industrial_ai_patents_2015_2024_part1.csv`

Target geography supplement (real data, not the template):

- `cnipa_patent_geography_2015_2024.csv`

Minimum geography acceptance after join: city fill >= 80%, 50+ cities, 500+ records.

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
