# Atlas IIDS geography engineer runbook

Rigorous control-laptop playbook for geography procurement through Atlas evidence readiness.  
**Program status:** [ATLAS_IIDS_GEO_PROGRAM_STATUS.md](ATLAS_IIDS_GEO_PROGRAM_STATUS.md)

## Priority 0 — freeze extraction

Do not reopen Hetzner / OpenXLab SQL work unless the imported IIDS CSV is corrupted. Extraction is complete: **4,014,104** filtered patents and keys. The only blocker is `data/raw/patents/cnipa_patent_geography_2015_2024.csv`.

## Current gate (every engineer, first)

```powershell
cd C:\Users\mateo\ai_diffusion_state
git pull origin main
make atlas-iids-geography-preflight
python scripts/50_atlas_status.py --json
```

Status table: `outputs/tables/table_P10_iids_geography_procurement_status.json`

---

## Engineer A — geography export (Lens API or external vendor)

**Preferred:** Lens in-repo exporter (`scripts/79_lens_geography_export.py`, token in `.env` as `LENS_API_TOKEN`).

```powershell
.\scripts\engineer_a_lens_smoke.ps1          # 25 IDs — must pass before batch 001
.\scripts\engineer_a_lens_batch001.ps1       # 250k IDs pilot
.\scripts\engineer_a_lens_all_batches.ps1    # 001–017 after batch 001 QA
```

**Fallback:** External CNIPA/Incopat export keyed by publication number (vendor handoff doc).

### A1 — Inputs

For each `N` in `001` … `017`:

```text
data/interim/iids_geo_key_batches/iids_geo_keys_batch_NNN.csv
```

Each batch lists publication numbers (and `patent_id` where present). Row counts: **250,000** per batch 001–016; **14,104** in batch 017 (**4,014,104** total).

Regenerate key batches only if headers or counts are wrong:

```powershell
make atlas-iids-geo-key-batches
```

### A2 — Outputs

Place one CSV per batch under `data/interim/iids_geo_exports/` (directory is gitignored):

```text
data/interim/iids_geo_exports/iids_geo_export_batch_001.csv
…
data/interim/iids_geo_exports/iids_geo_export_batch_017.csv
```

### A3 — Required columns (minimum)

At least one publication identifier plus address fields:

| Role | English | Accepted Chinese (repo aliases) |
|------|---------|----------------------------------|
| Publication id | `publication_number`, `patent_id` | `公开号`, `公开公告号`, `公开(公告)号`, `申请号` |
| City | `applicant_city` | `申请人城市` |
| Province | `applicant_province` | `申请人省份` |
| Address | `applicant_address` | `申请人地址` |

Optional but recommended on export: `geo_source`, `geo_match_confidence`, `geo_notes`.  
Contract template (do not commit as evidence): `data/raw/patents/cnipa_patent_geography_template.csv`.

The normalizer maps aliases in `src/diffusion_state/iids_geo_join.py` and `iids_geography_batch.py`.

### A4 — Export rules

1. **Prefer exact publication-number matching** on the keys in each batch file.
2. Set `geo_match_confidence=exact_publication_number` for those rows.
3. **Do not infer city from applicant name** unless necessary. If name/registry fallback is used, label explicitly: `geo_match_confidence=applicant_registry_match`.
4. Do not mix confidence labels on the same match method within a batch.

### A5 — Quality target (full program, not per-file only)

After all 17 batches are concatenated and normalized, the **combined** geography must meet thresholds evaluated against the **full IIDS key list** (`iids_filtered_patent_ids_for_geography.csv`):

| Metric | Minimum |
|--------|---------|
| City fill (on matched keys) | 80% |
| Province fill (on matched keys) | 80% |
| Key match rate | 95% |

Per-batch exports should be internally consistent; Engineer B runs `make atlas-iids-geo-coverage-validate` for the authoritative gate.

### A — Handoff to Engineer B

Deliver batch **001** first. Notify B when `iids_geo_export_batch_001.csv` exists so B can run the **pilot** before A completes 002–017.

---

## Engineer B — after batch 001 (pilot only)

Do **not** run the full evidence chain. Validate schema and normalizer on one batch.

### B1 — Confirm export exists

```powershell
cd C:\Users\mateo\ai_diffusion_state
Get-ChildItem data\interim\iids_geo_exports\iids_geo_export_batch_001.csv
```

### B2 — Concatenate and normalize (pilot)

```powershell
make atlas-iids-geo-concat
```

Creates: `data/raw/patents/cnipa_patent_geography_2015_2024_raw.csv`

```powershell
make atlas-iids-geo-normalize
```

Creates: `data/raw/patents/cnipa_patent_geography_2015_2024.csv` (contract columns from normalizer).

Alternative (4M-safe, skips monolithic raw if preferred):

```powershell
make atlas-iids-geo-validate-batches
python scripts/74_normalize_patent_geography_export.py --from-exports-dir data/interim/iids_geo_exports
```

### B3 — Inspect pilot quality manually

```powershell
python scripts/80_inspect_normalized_geography.py
```

**Pilot success criteria:**

- `patent_id` column exists and is populated
- `applicant_city` / `applicant_province` fill rates high on present rows
- `applicant_address` non-trivial
- `geo_match_confidence` present or defaults to `exact_publication_number` in normalizer

**Expected failure (OK at pilot stage):**

```powershell
make atlas-iids-geo-coverage-validate
```

Should **fail** key-match coverage: one batch covers only ~6% of the 4M key list.

### B4 — If pilot schema is wrong

**Stop.** Do not proceed to 17 exports. Report to Engineer A exactly which contract columns are missing.

| Symptom | Likely fix |
|---------|------------|
| Missing `patent_id` | Map `公开号` / `公开公告号` → `publication_number` or `patent_id` |
| Missing city | Map `申请人城市` → `applicant_city` |
| Missing province | Map `申请人省份` → `applicant_province` |
| Missing address | Map `申请人地址` → `applicant_address` |
| Province only, no city | **Source insufficient** — change vendor export, not normalizer |

---

## Engineer B — after all 17 exports exist

### B5 — Verify count

```powershell
(Get-ChildItem data\interim\iids_geo_exports\iids_geo_export_batch_*.csv).Count
```

Expected: **17**

```powershell
make atlas-iids-geo-validate-batches
```

### B6 — Full concat / normalize / coverage

Normalizer refuses to overwrite existing outputs. Remove stale files first:

```powershell
Remove-Item data\raw\patents\cnipa_patent_geography_2015_2024_raw.csv -ErrorAction SilentlyContinue
Remove-Item data\raw\patents\cnipa_patent_geography_2015_2024.csv -ErrorAction SilentlyContinue
make atlas-iids-geo-concat
make atlas-iids-geo-normalize
make atlas-iids-geo-coverage-validate
make atlas-iids-geo-validate
```

**Passing state:** city fill ≥ 80%, province fill ≥ 80%, key match ≥ 95% on the full key list.

---

## Engineer C — after coverage passes

```powershell
make atlas-iids-control-evidence-chain
python scripts/50_atlas_status.py --json --require-evidence
```

**Expected final flags:**

```text
iids_patent_export_ready: true
iids_geography_ready: true
ready_for_evidence_chain: true
patent_layer_ready: true
atlas_evidence_ready: true
atlas_ready: true
atlas_models_ready: true
```

The chain starts with `atlas-iids-geography-preflight` and `atlas-iids-require-geography` — it fails fast until geography is ready.

**If the chain fails, inspect:**

- `outputs/tables/table_P10_iids_geography_procurement_status.json`
- `paper/atlas_gate_report.json`
- `paper/atlas_evidence_gate_report.json`

---

## Engineer D — paper language

### Allowed before geography passes

- Imported a real OpenXLab IIDS-derived patent layer with **4,014,104** filtered CN industrial-AI patent records
- Generated a publication-number key list for geography procurement

### Forbidden before `ready_for_evidence_chain`

- Publication-ready F1
- Pilot-zone × AI-exposure result
- “Pilot zones are associated with stronger industrial AI patenting”
- “Atlas patent evidence chain is publication-ready”
- Any stale coefficient (e.g. `coef=-0.0207`) not regenerated from current tables

The repo flags premature patent claims in `draft_atlas_v1.md` via `premature_patent_claim_flags` / `forbidden_claim_flags` in Atlas status.

### After chain passes

```powershell
make atlas-v02
make atlas-models-v02
python scripts/50_atlas_status.py --json
```

Use **only** coefficients from regenerated `outputs/tables/` — do not reuse old model outputs.

---

## Engineer E — do not commit

Before any push:

```powershell
git status --short
```

**Never commit** (gitignored; if staged, unstage and fix `.gitignore`):

- `data/raw/patents/opendatalab_iids_industrial_ai_patents_2015_2024_part1.csv`
- `data/raw/patents/iids_filtered_patent_ids_for_geography.csv`
- `outputs/tables/table_P9_iids_patent_keys_for_geography.csv`
- `data/raw/patents/cnipa_patent_geography_2015_2024.csv`
- `data/raw/patents/cnipa_patent_geography_2015_2024_raw.csv`
- `data/interim/iids_geo_key_batches/`
- `data/interim/iids_geo_exports/`
- `atlas_iids_filtered_outputs.tar.gz`
- `base_patent_detail.sql`

---

## Tests

```powershell
$env:PYTHONPATH="src"
python -m pytest tests/test_iids_geography_gate_atlas.py tests/test_iids_geo_stream.py tests/test_atlas_paper_claims.py -q
```

## Helper scripts (parallel launch)

| Engineer | Script |
|----------|--------|
| A Lens smoke | `scripts/engineer_a_lens_smoke.ps1` |
| A Lens batch 001 | `scripts/engineer_a_lens_batch001.ps1` |
| A Lens all batches | `scripts/engineer_a_lens_all_batches.ps1` |
| A vendor fallback | [ATLAS_IIDS_GEO_VENDOR_HANDOFF.md](ATLAS_IIDS_GEO_VENDOR_HANDOFF.md) |
| B pilot | `scripts/engineer_b_pilot.ps1` |
| B full | `scripts/engineer_b_full.ps1` |
| B inspect | `make atlas-iids-geo-inspect` |
| E pre-push | `scripts/engineer_e_pre_push.ps1` |

## Reference

- Procurement brief: [ATLAS_IIDS_GEOGRAPHY_PROCUREMENT_BRIEF.md](ATLAS_IIDS_GEOGRAPHY_PROCUREMENT_BRIEF.md)
- `make atlas-iids-geography-brief` regenerates the brief
