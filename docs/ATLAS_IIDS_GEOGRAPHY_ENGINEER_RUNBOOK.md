# Atlas IIDS geography engineer runbook

Control-laptop sequence from filtered IIDS export through publication-ready Atlas evidence.

## Current gate (run first)

```powershell
git pull origin main
make atlas-iids-geography-preflight
python scripts/50_atlas_status.py --json
```

Status table: `outputs/tables/table_P10_iids_geography_procurement_status.json`

## Engineer A — Geography file

**Input:** `data/raw/patents/iids_filtered_patent_ids_for_geography.csv` (4,014,104 keys)

**Output:** `data/raw/patents/cnipa_patent_geography_2015_2024.csv`

**Contract columns:**

```text
patent_id,applicant_city,applicant_province,applicant_address,geo_source,geo_match_confidence,geo_notes
```

**Batch export:**

```powershell
make atlas-iids-geo-key-batches
# export each batch from CNIPA/Lens → data/interim/iids_geo_exports/
make atlas-iids-geo-concat
make atlas-iids-geo-normalize
```

## Engineer B — Coverage validation

Thresholds on the **key list** (not just geography file row count):

| Metric | Minimum |
|--------|---------|
| City fill | 80% |
| Province fill | 80% |
| Key match | 95% |

```powershell
make atlas-iids-geo-coverage-validate
```

## Engineer C — Evidence chain

Only after coverage passes:

```powershell
make atlas-iids-control-evidence-chain
python scripts/50_atlas_status.py --json --require-evidence
```

Expected: `ready_for_evidence_chain: true`, `atlas_evidence_ready: true`.

## Engineer D — Paper claims

Allowed before geography: imported 4,014,104 filtered CN industrial-AI patents; ready for geography procurement.

Not allowed until `ready_for_evidence_chain`: pilot-zone patent associations, publication-ready F1, publication-ready evidence chain.

The repo flags premature patent claims in `draft_atlas_v1.md` via `premature_patent_claim_flags` in the Atlas status report.

## Engineer E — Do not commit

Large artifacts are gitignored: IIDS CSV, key files, geography CSV/raw, batch dirs, tarball, SQL dumps.

## Tests

```powershell
$env:PYTHONPATH="src"
python -m pytest tests/test_iids_geography_gate_atlas.py tests/test_iids_geo_stream.py tests/test_atlas_paper_claims.py -q
```
