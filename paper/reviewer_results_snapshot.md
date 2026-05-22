# Reviewer results snapshot (committed, no pipeline required)

**Build date reference:** 2026-05-20 sprint. Regenerate tables with `make analysis`. Generated CSVs under `outputs/` are gitignored; this file is the compact empirical state for remote review.

## Dataset counts

| Item | Count |
|------|------:|
| AI pilot-zone units | 17 |
| Smart-factory projects (2024–2025 lists) | 509 |
| Projects with resolved city | **509** (baseline 193) |
| Projects without city | **0** |
<!-- PCS:REVIEWER_SEED -->
| City-resolution override rows (seed) | **414** inference overrides; **50** external-verification overrides |
<!-- /PCS:REVIEWER_SEED -->
| Cities with listed projects (resolved) | **158** |
<!-- PCS:ADOPTION_CITIES -->
| Cities in adoption panel | **160** (pilot + smart-factory universe) |
<!-- /PCS:ADOPTION_CITIES -->

## Descriptive overlap (resolved cities)

<!-- PCS:REVIEWER_OVERLAP -->
| Sample | Cities | Projects | Mean/city |
|--------|-------:|---------:|----------:|
| Pilot-zone | 16 | 192 | 12.00 |
| Non-pilot | 143 | 317 | 2.22 |
<!-- /PCS:REVIEWER_OVERLAP -->

## Hub-exclusion (Table 6, baseline)

<!-- PCS:REVIEWER_HUB -->
| Rule | coef | p-value | Note |
|------|-----:|--------:|------|
| Full sample | 4.55 | <0.001 | Baseline |
| Drop BJ/SH/SZ/HZ | 3.67 | <0.001 | Weakens (~81% of coef) |
| Drop direct-admin | 2.90 | <0.001 | Weakens (~64% of coef) |
| Drop top-5 SF cities | 2.95 | <0.001 | Weakens (~65% of coef) |
<!-- /PCS:REVIEWER_HUB -->

**Story:** Hub-centered diffusion capacity, not average pilot treatment.

## Controlled models (Table 5)

**Skipped** until EPS/NBS city controls are in `data/raw/city_controls/` and `make city-controls` succeeds. Synthetic controls are not used in this pipeline.

## Balance / matching (Tables 7–8)

**Skipped** without controls. Matched-sample code **fixed** to include matched pilot **and** control cities (metadata columns on Table 8).

## City typology (Table 14)

Central descriptive table: `frontier_municipality_hub`, `pilot_industrial_hub`, `pilot_non_hub`, `nonpilot_industrial_hub`, `nonpilot_low_adoption`. Figure: `fig_city_typology_smart_factory_counts.png`.

## City resolution evidence (Tables 9, 16, 17)

509 resolved; **0** unknown. **Table 16** (`make geo-audit`):

<!-- PCS:REVIEWER_GEO_TABLE -->
| `resolution_class` | Projects |
|--------------------|--------:|
| `official_location_exact` | 102 |
| `rule_based_text_inference` | 357 |
| `external_evidence_verified` | 50 |
<!-- /PCS:REVIEWER_GEO_TABLE -->

Registry plant-city matches use `firm_registry_match` + **rule-based** class (not external annual-report claims).

<!-- PCS:AUDIT_STATUS -->
**City-resolution audit:** **70/70** sample decisions (Table 17). Official-location sample: **20/20** confirmed. Rule-based sample (n=50): **20** confirmed, **30** insufficient_evidence.
<!-- /PCS:AUDIT_STATUS -->

External verification queue: **50/50** rows with non-list `external_evidence_url` (synced from verified seed overrides).

## Ex ante typology (Table 18)

Capacity typology without `top_5_smart_factory_city`. Column `typology_control_source` records whether GDP ranks are used (`real_city_controls` only); with stub or missing controls, typology uses pilot/direct-admin/mega-hub flags only.

## Province-year robustness (Table 19)

**Coarse descriptive check only** (claim tier: `coarse_robustness`). Uses all 509 projects; pilot-province bucket includes many non-pilot cities, so it cannot isolate pilot-city effects.

## City-industry (Table 13)

Preferred: **ex ante** exposure (`industry_ai_exposure_ex_ante.csv`). Tag-derived specs labeled descriptive only.

## Export

- **Table 15** (descriptive relevance by sector): strategic overlap with export basket.
- **Not claimed:** causal export effects (Tables 4/12 underpowered).

## Claim tiers (summary)

| Tier | Claim |
|------|-------|
| Measured | Pilot zones + smart-factory lists reproducibly coded |
| Validated descriptive | Pilot overlap; hub typology; export relevance |
| Robust association | Hub exclusion attenuation (baseline); typology |
| Blocked (paper) | Controlled adoption (Table 5), balance, matched models until EPS/NBS |
| Not supported | Causal pilot effect; average treatment across treated cities |

Full map: `paper/claim_table_map.csv`. Identification limits: `paper/red_team_memo.md`. Narrative: `paper/results_memo.md`.
