# City resolution sample audit

## Purpose

Independent review of stratified city assignments before paper claims cite error rates.

## Files

| File | Role |
|------|------|
| `city_resolution_sample_audit.csv` | Stratified sample (50 rule-based + 20 official; +30 external when present; regenerate with `make geo-audit`) |
| `../outputs/tables/table_17_geo_audit_error_rate.csv` | Aggregated rates after audit is filled |

## Auditor workflow

1. Open `city_resolution_sample_audit.csv`.
2. For each row, verify `assigned_city` using `evidence_url` and firm/project text.
3. Set `auditor_decision`:
   - `confirmed` — city is correct
   - `incorrect` — wrong city (fill `corrected_city`, `corrected_province`)
   - `uncertain` — cannot verify from materials provided
   - `insufficient_evidence` — no usable evidence
4. Add `audit_notes`, `auditor`, `audit_date` (YYYY-MM-DD).
5. Re-run:

```bash
py -3 -c "import sys; sys.path.insert(0,'src'); from diffusion_state.build_geo_evidence_quality import build_table_geo_audit_error_rate; build_table_geo_audit_error_rate()"
```

## Evidence classes (do not confuse)

| `resolution_class` | What to check |
|--------------------|---------------|
| `official_location_exact` | City named in MIIT location field |
| `rule_based_text_inference` | City inferred from list text or plant-city registry (list URL is OK) |
| `external_evidence_verified` | Separate external URL required; list page alone is insufficient |
