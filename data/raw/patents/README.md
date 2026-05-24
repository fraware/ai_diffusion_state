# Patent raw data (Workstream A)

Place China patent microdata here for the Atlas industrial AI patent layer.

## Control laptop vs production machine

Keep the repo laptop (~40 GB free) as **control / paper / repo only**. Do not run full IIDS SQL
downloads or production conversion on it.

Run heavy steps on an **external SSD (256 GB+)** or a **temporary cloud VM (300 GB disk)**.

Preflight (any machine): `make atlas-iids-preflight` → `outputs/tables/table_P8_iids_machine_readiness.json`

## IIDS — download only what Atlas needs

**Do not download:** `entity_fund_info.sql`, `entity_funds_re.zip`, `entity_paper.sql`,
`reference_citation_re.sql` (not used by the patent layer).

**Essential:** `base_patent_detail.sql` only (~136 GB).

**Optional (skip under disk pressure):** `base_patent_law_status.sql` — grant-year enrichment only;
script 61 works without it.

### External SSD (Strategy A)

```powershell
$env:OPENXLAB_IIDS_SOURCES_DIR="D:\iids_sources"
$env:OPENXLAB_AK="YOUR_NEW_KEY"
$env:OPENXLAB_SK="YOUR_NEW_SECRET"
$env:OPENXLAB_INSECURE_SSL="1"
$env:PYTHONUTF8="1"

python scripts/59_download_iids_patent_sources.py --detail-only --target-dir D:\iids_sources
python scripts/61_iids_sql_to_patent_csv.py --detail-sql D:\iids_sources\Gracie___IIDS\base_patent_detail.sql --production
python scripts/66_export_iids_patent_keys.py --production
```

After a successful convert, **delete or archive** the SQL dump; keep the filtered CSV.

Or orchestrate on the production machine:

```powershell
python scripts/64_run_atlas_iids_pipeline.py --download --target-dir D:\iids_sources --production
python scripts/64_run_atlas_iids_pipeline.py --target-dir D:\iids_sources --skip-geo --production
```

Script 64 supports `--target-dir`, `--production`, and defaults to `--detail-only` (not full IIDS).

### Cloud VM (Strategy B)

Run the same commands on a 300 GB VM, then copy back only:

- `data/raw/patents/opendatalab_iids_industrial_ai_patents_2015_2024_part1.csv`
- `data/raw/patents/cnipa_patent_geography_2015_2024.csv`
- `data/raw/patents/patent_source_manifest.csv`
- processed panels + `outputs/tables/table_F*.csv` + `paper/atlas_gate_report.json`

### Repo-only smoke (no evidence)

```powershell
make atlas-iids-smoke
```

Writes to `outputs/smoke/iids/` — does not touch the evidence path.

## Geography (critical path after IIDS convert)

IIDS has no city/province/address. Export keys first, then build geography **only for filtered patent IDs**:

1. `make atlas-iids-export-keys` → `outputs/tables/table_P9_iids_patent_keys_for_geography.csv`
2. Request CNIPA/Lens geography export for those publication numbers
3. `make atlas-iids-geo-build` (from CNIPA/Lens export with `公开号` + address fields)
2. `make atlas-iids-geo-validate`
3. `make atlas-iids-geo`

Schema guide: `data/raw/patents/cnipa_patent_geography_template.csv`

## Evidence chain (after geography + manifest)

```powershell
make atlas-patent-prep
make atlas-iids-manifest-merge
python scripts/64_run_atlas_iids_pipeline.py --full-chain --production
```

See `docs/ATLAS_PHASE2_PATENT_EXPORT_AND_MODEL_RUNBOOK.md`.

## Required for city-industry-year panel
