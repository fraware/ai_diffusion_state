# Atlas IIDS geography vendor handoff (Engineer A)

Do not commit export CSVs to git (`data/interim/iids_geo_exports/` is gitignored).

## Primary path: Lens Patent API (in-repo)

Token: `LENS_API_TOKEN` in repo `.env` (never commit). Loader: `scripts/load_repo_env.ps1`.

| Step | Command |
|------|---------|
| Smoke keys | `python scripts/create_lens_smoke_keys.py` or `make atlas-iids-lens-smoke-keys` |
| 25-ID smoke | `.\scripts\engineer_a_lens_smoke.ps1` |
| Batch 001 | `.\scripts\engineer_a_lens_batch001.ps1` (after smoke passes) |
| All 17 | `.\scripts\engineer_a_lens_all_batches.ps1` |

Core exporter: `scripts/79_lens_geography_export.py` — queries Lens `ids` field by publication number, reads `biblio.parties.applicants[].extracted_address`, parses city/province locally, retries on HTTP 429, writes unmatched IDs with `geo_match_confidence=not_found`.

Inspect: `python scripts/82_inspect_lens_geography_export.py --smoke` or `--batch-001`.

**Smoke gate:** Do not run batch 001 if smoke shows all `not_found` or empty addresses.

**Windows SSL:** If `CERTIFICATE_VERIFY_FAILED`, set `LENS_INSECURE_SSL=1` in `.env` or pass `--insecure-ssl`.

**Diagnostic (Steps 1–2):**

```powershell
.\scripts\engineer_a_lens_debug.ps1
```

Writes `outputs/debug/lens_smoke_025_raw.jsonl`, `lens_smoke_025_party_field_audit.csv`, and `*_projection.*` for extended `include` test.

Inspect: `python scripts/84_inspect_lens_party_audit.py`

**Decision (2026-05-28 diagnostic):** Lens CN records lack applicant addresses on this API plan. **Stop Lens batch work.**

## Tiered geography pivot (active)

| Step | Command |
|------|---------|
| Applicant concentration | `make atlas-iids-applicant-concentration` → `outputs/tables/table_P12_top_iids_applicants.csv` |
| Name-token geography | `make atlas-iids-name-geography` |
| Coverage report | `make atlas-iids-name-geography-coverage` |
| Seed manual map | `make atlas-iids-top-applicant-map-seed` → `data/seed/top_applicant_city_map.csv` |
| Merge tiers | `make atlas-iids-tiered-geography-merge` |

Gate flags: `exact_geography_ready` (publication-number address only) vs `tiered_geography_ready` (name token + curated top applicants). **Do not call tiered geography exact publication-number geography.**

**Fallback:** External CNIPA/Incopat export (sections below) if Lens fill rates are insufficient.

## Key batch inputs (17 files, 4,014,104 rows)

Regenerate only if headers or counts are wrong: `make atlas-iids-geo-key-batches`.

- `data/interim/iids_geo_key_batches/iids_geo_keys_batch_001.csv`
- `data/interim/iids_geo_key_batches/iids_geo_keys_batch_002.csv`
- `data/interim/iids_geo_key_batches/iids_geo_keys_batch_003.csv`
- `data/interim/iids_geo_key_batches/iids_geo_keys_batch_004.csv`
- `data/interim/iids_geo_key_batches/iids_geo_keys_batch_005.csv`
- `data/interim/iids_geo_key_batches/iids_geo_keys_batch_006.csv`
- `data/interim/iids_geo_key_batches/iids_geo_keys_batch_007.csv`
- `data/interim/iids_geo_key_batches/iids_geo_keys_batch_008.csv`
- `data/interim/iids_geo_key_batches/iids_geo_keys_batch_009.csv`
- `data/interim/iids_geo_key_batches/iids_geo_keys_batch_010.csv`
- `data/interim/iids_geo_key_batches/iids_geo_keys_batch_011.csv`
- `data/interim/iids_geo_key_batches/iids_geo_keys_batch_012.csv`
- `data/interim/iids_geo_key_batches/iids_geo_keys_batch_013.csv`
- `data/interim/iids_geo_key_batches/iids_geo_keys_batch_014.csv`
- `data/interim/iids_geo_key_batches/iids_geo_keys_batch_015.csv`
- `data/interim/iids_geo_key_batches/iids_geo_keys_batch_016.csv`
- `data/interim/iids_geo_key_batches/iids_geo_keys_batch_017.csv`

| Batch | Rows |
|-------|------|
| 001 | 250,000 |
| 002 | 250,000 |
| 003 | 250,000 |
| 004 | 250,000 |
| 005 | 250,000 |
| 006 | 250,000 |
| 007 | 250,000 |
| 008 | 250,000 |
| 009 | 250,000 |
| 010 | 250,000 |
| 011 | 250,000 |
| 012 | 250,000 |
| 013 | 250,000 |
| 014 | 250,000 |
| 015 | 250,000 |
| 016 | 250,000 |
| 017 | 14,104 |
| **Total** | **4,014,104** |

## Deliverables

One CSV per batch under `data/interim/iids_geo_exports/`:

- `data/interim/iids_geo_exports/iids_geo_export_batch_001.csv`
- `data/interim/iids_geo_exports/iids_geo_export_batch_002.csv`
- `data/interim/iids_geo_exports/iids_geo_export_batch_003.csv`
- `data/interim/iids_geo_exports/iids_geo_export_batch_004.csv`
- `data/interim/iids_geo_exports/iids_geo_export_batch_005.csv`
- `data/interim/iids_geo_exports/iids_geo_export_batch_006.csv`
- `data/interim/iids_geo_exports/iids_geo_export_batch_007.csv`
- `data/interim/iids_geo_exports/iids_geo_export_batch_008.csv`
- `data/interim/iids_geo_exports/iids_geo_export_batch_009.csv`
- `data/interim/iids_geo_exports/iids_geo_export_batch_010.csv`
- `data/interim/iids_geo_exports/iids_geo_export_batch_011.csv`
- `data/interim/iids_geo_exports/iids_geo_export_batch_012.csv`
- `data/interim/iids_geo_exports/iids_geo_export_batch_013.csv`
- `data/interim/iids_geo_exports/iids_geo_export_batch_014.csv`
- `data/interim/iids_geo_exports/iids_geo_export_batch_015.csv`
- `data/interim/iids_geo_exports/iids_geo_export_batch_016.csv`
- `data/interim/iids_geo_exports/iids_geo_export_batch_017.csv`

**Deliver batch 001 first.** Notify Engineer B when `iids_geo_export_batch_001.csv` exists so B can run the pilot before batches 002-017.

## Required columns (minimum)

| Role | English | Accepted Chinese (repo aliases) |
|------|---------|----------------------------------|
| Publication id | `publication_number`, `patent_id` | `公开号`, `公开公告号`, `公开(公告)号`, `申请号` |
| City | `applicant_city` | `申请人城市` |
| Province | `applicant_province` | `申请人省份` |
| Address | `applicant_address` | `申请人地址` |

Optional but recommended: `geo_source`, `geo_match_confidence`, `geo_notes`.

Contract template (reference only; do not commit as evidence): `data/raw/patents/cnipa_patent_geography_template.csv`.

Normalizer aliases: `src/diffusion_state/iids_geo_join.py`, `src/diffusion_state/iids_geography_batch.py`.

## geo_match_confidence rules

1. Prefer **exact publication-number matching** on keys in each batch file.
2. Set `geo_match_confidence=exact_publication_number` for those rows.
3. Do **not** infer city from applicant name unless necessary. If name/registry fallback is used, label explicitly: `geo_match_confidence=applicant_registry_match`.
4. Do not mix confidence labels for the same match method within a batch.

## Combined program quality thresholds

Evaluated after all 17 batches are concatenated and normalized against `data/raw/patents/iids_filtered_patent_ids_for_geography.csv`:

| Metric | Minimum |
|--------|---------|
| City fill (on matched keys) | 80% |
| Province fill (on matched keys) | 80% |
| Key match rate | 95% |

Engineer B runs `make atlas-iids-geo-coverage-validate` for the authoritative gate.

## Example header row (template)

```csv
patent_id,applicant_city,applicant_province,applicant_address,geo_source,geo_match_confidence,geo_notes
```

## Related docs

- Engineer runbook: [ATLAS_IIDS_GEOGRAPHY_ENGINEER_RUNBOOK.md](ATLAS_IIDS_GEOGRAPHY_ENGINEER_RUNBOOK.md)
- Program status: [ATLAS_IIDS_GEO_PROGRAM_STATUS.md](ATLAS_IIDS_GEO_PROGRAM_STATUS.md)
