# Atlas IIDS geography procurement brief

Generated: 2026-05-28 19:37 UTC

Source keys file: `data/raw/patents/iids_filtered_patent_ids_for_geography.csv`

## Request

Export **address metadata only** for the publication numbers in the keys file. Do not download a full patent universe.

| Metric | Value |
|--------|-------|
| Unique patent IDs | 4,014,104 |
| Application years | 2015–2022 |
| Pre-chunked batch files | 17 (`data/interim/iids_geo_key_batches/`) |

## Required output file

Place on the control laptop:

```text
data/raw/patents/cnipa_patent_geography_2015_2024.csv
```

Intermediate concatenated export (do not treat as final until normalized):

```text
data/raw/patents/cnipa_patent_geography_2015_2024_raw.csv
```

## Required columns (normalized contract)

```text
patent_id
applicant_city
applicant_province
applicant_address
geo_source
geo_match_confidence
geo_notes
```

Minimum raw-source columns from Chinese exports:

```text
公开公告号 / 公开号 / 申请公布号 / patent_id
申请人城市 / applicant_city
申请人省份 / applicant_province
申请人地址 / applicant_address
```

## Minimum acceptance (Atlas gate)

Measured **on the IIDS key list** after join by publication number:

- City fill rate >= 80%
- Province fill rate >= 80%
- Key match rate >= 95% (geography row for each filtered patent ID)
- >= 50 unique cities

## Preferred sources (in order)

1. CNIPA / Incopat / Patsnap / CNRDS / CSMAR keyed by publication number
2. Lens / Google Patents bulk export with applicant address fields
3. Applicant-address parsing from bibliographic records
4. Applicant-name registry matching (flag separately; lower confidence)

## After delivery

```powershell
make atlas-iids-geo-key-batches          # if batches not yet built
# place batch exports -> data/interim/iids_geo_exports/
make atlas-iids-geo-concat               # -> cnipa_patent_geography_2015_2024_raw.csv
make atlas-iids-geo-normalize            # -> cnipa_patent_geography_2015_2024.csv
make atlas-iids-geo-coverage-validate
make atlas-iids-geo-validate
make atlas-iids-geo
make atlas-iids-control-evidence-chain
python scripts/50_atlas_status.py --json
```

Do not weaken `atlas_evidence_ready` gates.
