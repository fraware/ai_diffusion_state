# External geography drop zone (CNIPA / Incopat / vendor)

Gitignored directory: `data/interim/iids_geo_exports/`

## Required files (17 batches)

```
data/interim/iids_geo_exports/iids_geo_export_batch_001.csv
data/interim/iids_geo_exports/iids_geo_export_batch_002.csv
...
data/interim/iids_geo_exports/iids_geo_export_batch_017.csv
```

Schema and QA: `docs/ATLAS_IIDS_GEO_VENDOR_HANDOFF.md`

## Vendor subset (recommended first)

Do **not** send all 4,014,104 keys initially. Build the priority file on the control laptop:

```powershell
make atlas-iids-procurement-priority-unresolved
```

Output: `data/interim/iids_geo_procurement_priority_unresolved.csv` (~750k–900k high-yield unresolved patents).

Status JSON: `outputs/tables/table_P18_procurement_pack_status.json` (`make atlas-iids-procurement-pack-status`)

## After batches arrive

```powershell
make atlas-iids-external-geo-pipeline
make atlas-iids-geo-coverage-validate
make atlas-iids-control-evidence-chain
python scripts/50_atlas_status.py --json --require-evidence
```

Target: **+751k** additional keyed cities (~**80%** total) without weakening exact vs tiered gate logic.
