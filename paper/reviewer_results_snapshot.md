# Reviewer results snapshot (committed, no pipeline required)

**Build date reference:** 2026-05-20 sprint. Regenerate tables with `make analysis`. Generated CSVs under `outputs/` are gitignored; this file is the compact empirical state for remote review.

## Dataset counts

| Item | Count |
|------|------:|
| AI pilot-zone units | 17 |
| Smart-factory projects (2024–2025 lists) | 509 |
| Projects with resolved city | **509** (baseline 193) |
| Projects without city | **0** |
| Audited override rows (seed) | **450+** |
| Cities with listed projects (resolved) | **158** |
| Cities in adoption panel | **125** (pilot + smart-factory universe) |

## Descriptive overlap (resolved cities)

| Sample | Cities | Projects | Mean/city |
|--------|-------:|---------:|----------:|
| Pilot-zone | 16 | 192 | 12.00 |
| Non-pilot | 143 | 317 | 2.22 |

## Hub-exclusion (Table 6, baseline)

| Rule | coef | p-value | Interpretation |
|------|-----:|--------:|----------------|
| Full sample | 3.92 | <0.001 | Baseline (125 cities) |
| Drop BJ/SH/SZ/HZ | 2.97 | 0.0002 | Weakens (~76% of coef) |
| Drop direct-admin | 2.04 | <0.001 | Substantially weakens (~52% of coef) |
| Drop top-5 SF cities | 2.11 | <0.001 | Weakens (~54% of coef) |

**Story:** Hub-centered diffusion capacity, not average pilot treatment.

## Controlled models (Table 5)

**CI stub run:** With `make city-controls-stub`, Model 4 `pilot_zone` ≈ 1.86 (p ≈ 0.035) on stub controls — **not for paper** (synthetic controls). Production requires EPS/NBS in `data/raw/city_controls/`.

## Balance / matching (Tables 7–8)

**Skipped** without controls. Matched-sample code **fixed** to include matched pilot **and** control cities (metadata columns on Table 8).

## City typology (Table 14)

Central descriptive table: `frontier_municipality_hub`, `pilot_industrial_hub`, `pilot_non_hub`, `nonpilot_industrial_hub`, `nonpilot_low_adoption`. Figure: `fig_city_typology_smart_factory_counts.png`.

## City resolution evidence (Tables 9, 16, 17)

509 resolved; **0** unknown. **Table 16** (regenerate with `make geo-audit`):

| `resolution_class` | Projects (typical build) |
|--------------------|-------------------------:|
| `official_location_exact` | 102 |
| `rule_based_text_inference` | 407 |
| `external_evidence_verified` | 0 until registry rows include real external URLs |

Registry plant-city matches use `firm_registry_match` + **rule-based** class (not external annual-report claims). **Table 17**: stratified sample in `data/audit/city_resolution_sample_audit.csv` — audit pending until `auditor_decision` filled.

## Ex ante typology (Table 18)

Capacity typology without `top_5_smart_factory_city` (pilot hub / non-pilot hub / low capacity).

## Province-year robustness (Table 19)

Coarse check using all 509 projects; pilot-province bucket includes non-pilot cities (caveat in red-team memo).

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
| CI-only | Stub-controlled adoption (not for claims) |
| Blocked (paper) | Real-controls adoption, balance, matched models |
| Not supported | Causal pilot effect; average treatment across treated cities |

Full map: `paper/claim_table_map.csv`. Identification limits: `paper/red_team_memo.md`. Narrative: `paper/results_memo.md`.
