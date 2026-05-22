# Next Sprint Instructions — From Research Pipeline to Paper-Ready Evidence

**Current priorities:** [`docs/CURRENT_SPRINT_PRIORITIES.md`](CURRENT_SPRINT_PRIORITIES.md) — Workstream A closed (Table I appendix only); **B1 + B2 are critical path**.  
**Human-input blockers:** [`docs/HUMAN_INPUT_BLOCKERS_ACTION_PLAN.md`](HUMAN_INPUT_BLOCKERS_ACTION_PLAN.md). Do not bypass blockers with synthetic data.

## Sprint objective

Move the project from a strong prototype to a paper-ready empirical package.

The paper should now be framed as:

> China’s AI diffusion state operates through a hub-centered industrial adoption architecture. Pilot-zone designation marks part of this architecture, but the evidence does not establish a uniform average treatment effect across all treated cities.

The sprint has five mandatory outputs:

1. ~~Real EPS/NBS city controls~~ **Done for public path:** strict Table 5 skipped; Table I appendix robustness documented. EPS/NBS export only if it becomes available.
2. Completed city-resolution audit sample. **Critical path.**
3. At least 50 externally verified city-resolution rows.
4. Production-safe main tables under `paper/main_tables/`.
5. Paper-facing memos synchronized with current numbers and no CI-stub leakage.

## Global rule

No paper-facing result may be used unless the command that validates it exits with code 0.

The final command sequence for paper readiness is:

```powershell
cd c:\Users\mateo\ai_diffusion_state
make purge-stub-controls
make validate-controls-raw
make city-controls
make apply-geo-updates
make geo-audit
make validate-geo
make panel
make analysis
make recompute-audit
make validate-audit
make sync-paper-stats
make main-tables
make paper
make production-check
make validate-sprint
make test
python scripts/15_pcs_status.py
```

If `validate-controls-raw` cannot pass because EPS/NBS files are not available, run the geo and descriptive parts, but the paper must not cite Tables 5–8 as controlled evidence.

---

# Engineer A — Real city controls

## Mission

Deliver production city controls from EPS/NBS or another real city-statistics source.

## Inputs

Place raw controls locally in:

```text
data/raw/city_controls/
```

Allowed formats:

```text
.csv
.xlsx
.xls
```

Do not commit proprietary data.

## Required columns after aliases

```text
city
province
year
gdp
gdp_per_capita
secondary_value_added
industrial_output
population
employment
average_wage
fdi
fixed_asset_investment
education_proxy
telecom_or_internet_proxy
foreign_trade
source_name
source_file
```

## Required years

Target:

```text
2019-2024
```

If 2025 is unavailable, document this. Controlled models may need to be restricted to 2024 or use lagged controls explicitly.

## Commands

```powershell
make purge-stub-controls
python scripts/06a_validate_city_controls_raw.py
make city-controls
make panel
make analysis
make sync-paper-stats
make main-tables
make production-check
make validate-sprint
python scripts/15_pcs_status.py
```

## Deliverables

```text
data/processed/city_controls_year.csv
data/processed/city_controls_missingness.csv
outputs/tables/table_5_controlled_adoption_models.csv
outputs/tables/table_7_pilot_city_balance.csv
outputs/tables/table_8_matched_adoption_models.csv
docs/source_notes/city_controls.md
```

## Acceptance criteria

1. `python scripts/06a_validate_city_controls_raw.py` prints columns complete.
2. `source_name` does not contain `pipeline_ci_stub_not_for_paper`.
3. `make production-check` exits 0.
4. `python scripts/15_pcs_status.py` reports production controls.
5. Table 5 contains real controlled estimates or clearly documents sample restrictions.
6. Table 7 reports covariate balance.
7. Table 8 contains a matched estimate or a documented matching failure.

## Interpretation rule

If the pilot-zone coefficient survives production controls but attenuates under hub exclusions, the paper may say:

> The pilot-zone association is robust to baseline city controls but remains mediated by hub structure.

If the coefficient disappears after controls, the paper must say:

> Pilot-zone status primarily captures pre-existing city capacity; the contribution is the measurement of China’s hub-centered diffusion architecture.

---

# Engineer B — City-resolution evidence quality

## Mission

Make the city-resolution layer reviewer-safe.

This has two tasks:

1. Complete the stratified audit sample.
2. Externally verify at least 50 high-priority rule-based assignments.

## Task B1 — Complete audit sample

Edit:

```text
data/audit/city_resolution_sample_audit.csv
```

Fill:

```text
auditor_decision
audit_notes
auditor
audit_date
```

Allowed `auditor_decision` values:

```text
confirmed
incorrect
uncertain
insufficient_evidence
```

For incorrect rows, fill:

```text
corrected_city
corrected_province
```

Minimum completion:

```text
50 rule_based_text_inference rows
20 official_location_exact rows
```

Commands:

```powershell
make apply-geo-updates
make recompute-audit
make validate-audit
make sync-paper-stats
python scripts/15_pcs_status.py
```

Deliverables:

```text
outputs/tables/table_17_geo_audit_error_rate.csv
```

Acceptance criteria:

1. `make validate-audit` exits 0.
2. Table 17 reports confirmation, incorrect, uncertain, and insufficient-evidence counts by resolution class.
3. Any incorrect rows are propagated into `data/seed/smart_factory_city_overrides.csv` through `make apply-geo-updates`.

## Task B2 — External verification

Generate the queue if needed:

```powershell
make external-verification-queue
```

Edit:

```text
data/interim/external_verification_queue.csv
```

For at least 50 rows, fill:

```text
external_evidence_url
external_evidence_type
audit_notes
```

Accepted `external_evidence_type` values:

```text
company_annual_report
company_site_registry
industrial_park_page
project_registry
```

Accepted evidence:

- company production-base page naming city;
- annual report or ESG report naming facility location;
- local-government or industrial-park notice;
- subsidiary or registry page with plant address.

Rejected evidence:

- Solarbe list page;
- JLTS list page;
- empty URL;
- generic homepage without facility location;
- headquarters page unless the project is explicitly at headquarters.

Commands:

```powershell
make apply-geo-updates
make geo-audit
make validate-geo
make panel
make analysis
make sync-paper-stats
make main-tables
make validate-sprint
python scripts/15_pcs_status.py
```

Deliverables:

```text
outputs/tables/table_16_geo_evidence_quality.csv
data/seed/smart_factory_city_overrides.csv
```

Acceptance criteria:

1. `make apply-geo-updates` reports at least 50 external verification rows applied.
2. Table 16 reports `external_evidence_verified >= 50`.
3. `make validate-geo` exits 0.
4. `data/seed/smart_factory_city_overrides.csv` contains real non-list `external_evidence_url` values.

---

# Engineer C — Export relevance and sector mapping

## Mission

Keep the export section descriptive and make it clean enough for the paper.

The export section must not claim causal export effects. It should support this sentence:

> Listed smart-factory recognition is concentrated in sectors that are strategically relevant to China’s advanced manufacturing export basket.

## Steps

1. Confirm that `outputs/tables/table_15_export_relevance_by_sector.csv` uses log level growth from 2017 to 2024, not growth-rate differences.
2. Audit sector mappings in:

```text
data/processed/hs_to_smart_factory_sector_bridge.csv
```

3. Flag low-confidence mappings and exclude them from main text.
4. Build a short export relevance memo.

## Commands

```powershell
make baci
make analysis
make main-tables
```

If BACI raw files are unavailable, document export outputs as optional and do not block the main paper.

## Deliverables

```text
outputs/tables/table_15_export_relevance_by_sector.csv
paper/main_tables/table_G_export_relevance.csv
docs/export_relevance_memo.md
```

## Acceptance criteria

1. Table 15 includes:

```text
export_value_2017
export_value_2024
log_export_growth_2017_2024
unit_value_index_2017
unit_value_index_2024
log_unit_value_growth_2017_2024
growth_method
```

2. The memo states clearly:

```text
This table is descriptive strategic relevance, not a causal estimate.
```

3. Low-confidence HS mappings are excluded from main-text claims.

---

# Engineer D — Model discipline and robustness

## Mission

Keep the econometric layer honest and interpretable.

## Tasks

### D1 — Re-run model stack after A/B updates

After Engineer A and B finish:

```powershell
make panel
make analysis
make sync-paper-stats
make main-tables
make production-check
make validate-sprint
```

### D2 — Update model interpretation table

Create or update:

```text
docs/model_interpretation_matrix.md
```

For each model table, list:

```text
table
model
identifying variation
main coefficient
what it supports
what it does not support
paper status
```

Minimum rows:

```text
Table 3 baseline adoption
Table 5 controlled adoption
Table 6 hub exclusion
Table 7 balance
Table 8 matched adoption
Table 13 city-industry ex ante heterogeneity
Table 19 province-year robustness
```

### D3 — Guard interpretation of Table 19

Table 19 is coarse robustness only. It cannot isolate pilot-city effects because pilot provinces contain non-pilot cities.

Paper language:

```text
Province-level results provide a coarser check using all projects, but cannot identify pilot-city effects because pilot provinces contain many non-pilot cities.
```

## Acceptance criteria

1. Controlled specifications are labeled controlled only if production controls are present.
2. Stub-controlled results never appear in paper tables.
3. Table 19 is labeled descriptive/coarse robustness.
4. City-industry exposure uses ex ante classification in main text.
5. Tag-derived exposure appears only in appendix or exploratory notes.

---

# Engineer E / Paper owner — Drafting and claim control

## Mission

Begin drafting from paper-safe tables only.

## Draft only from

```text
paper/main_tables/table_A_dataset_counts.csv
paper/main_tables/table_B_city_resolution_quality.csv
paper/main_tables/table_C_pilot_overlap.csv
paper/main_tables/table_D_hub_exclusion.csv
paper/main_tables/table_E_city_typology.csv
paper/main_tables/table_E_ex_ante_city_typology.csv
paper/main_tables/table_F_ex_ante_industry_heterogeneity.csv
paper/main_tables/table_G_export_relevance.csv
```

Do not use exploratory tables unless they are explicitly caveated.

## Required paper structure

1. Introduction: frontier-model advantage vs diffusion architecture.
2. Institutional background: AI pilot zones and MIIT smart-factory recognition.
3. Measurement: pilot zones, smart-factory projects, city resolution, evidence classes.
4. Geography of diffusion: overlap, hub typology, hub exclusion.
5. Industry and export relevance: ex ante industry exposure and export basket overlap.
6. Empirical caution: controls, balance, matching, audit, and hub-selection limits.
7. Conclusion: China’s diffusion state as hub-centered infrastructure.

## Core thesis language

Use:

```text
The evidence reveals a hub-centered diffusion architecture rather than a uniform pilot-zone treatment effect.
```

Avoid:

```text
Pilot zones caused adoption.
China’s AI policy caused productivity growth.
Smart-factory recognition proves export upgrading.
```

## Required claim tiers

Every major empirical claim must be marked internally as one of:

```text
measured
validated_descriptive
baseline_association
controlled_association
robust_association
suggestive_mechanism
not_supported
```

Update:

```text
paper/claim_table_map.csv
paper/results_memo.md
paper/red_team_memo.md
paper/reviewer_results_snapshot.md
```

## Acceptance criteria

1. No stale numbers remain.
2. No stub-control language appears except as an explicitly rejected development artifact.
3. Every empirical paragraph cites a table, figure, or limitation.
4. The abstract avoids causal language.
5. The red-team memo and results memo tell the same story.

---

# Paper-ready decision gates

## Gate 1 — Descriptive paper only

Allowed if:

```text
make validate-geo passes
make main-tables passes
make production-check passes or controlled claims are removed
```

Paper claim:

```text
We measure the geography and sectoral structure of China’s listed industrial AI adoption.
```

## Gate 2 — Strong descriptive + audited geocoding paper

Allowed if:

```text
make validate-audit passes
external_evidence_verified >= 50
```

Paper claim:

```text
City-resolution quality is assessed through evidence classes and a stratified audit.
```

## Gate 3 — Controlled association paper

Allowed if:

```text
real EPS/NBS controls are ingested
make production-check passes
Tables 5, 7, 8 are valid
```

Paper claim:

```text
The pilot-zone association is evaluated against city economic controls, balance diagnostics, and matched samples.
```

## Gate 4 — Causal paper

Not currently allowed.

Do not write a causal treatment-effect paper unless a new identification strategy is added.

# Immediate order of execution

1. Engineer A completes real city controls.
2. Engineer B completes audit decisions.
3. Engineer B externally verifies 50 priority rows.
4. Engineer D reruns analysis and updates model interpretation matrix.
5. Engineer C finalizes export relevance memo.
6. Paper owner drafts from `paper/main_tables/` only.
7. Everyone runs the final production sequence.

# Final production sequence

```powershell
cd c:\Users\mateo\ai_diffusion_state
make purge-stub-controls
make validate-controls-raw
make city-controls
make apply-geo-updates
make geo-audit
make validate-geo
make panel
make analysis
make recompute-audit
make validate-audit
make sync-paper-stats
make main-tables
make paper
make production-check
make validate-sprint
make test
python scripts/15_pcs_status.py
```

Expected final status:

```text
City controls: production
Panel controls merged: yes
Geo evidence hygiene: OK
Audit validation: OK
External evidence verified: >= 50
No stub leakage
No stale paper numbers
```
