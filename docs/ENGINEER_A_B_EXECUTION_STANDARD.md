# Engineer A/B Execution Standard — Production Controls and City-Resolution Evidence

This document is the operating standard for completing the two remaining evidence-quality workstreams before paper drafting.

The goal is to make the empirical pipeline paper-safe. No CI stub controls may enter paper claims. No city-resolution assignment may be described as externally verified unless it has a real non-list evidence URL.

## Shared principles

1. Work from repo root: `c:\Users\mateo\ai_diffusion_state`.
2. Never commit proprietary EPS/NBS downloads.
3. Preserve source provenance for every production input.
4. Treat generated outputs as disposable and reproducible.
5. Paper claims are allowed only after the relevant validation command exits with code 0.
6. Do not use the word “audited” loosely. Use “official-location exact,” “rule-based inference,” or “externally verified.”
7. Keep export claims descriptive unless a separate identification design is added.

## Preflight for both engineers

Run before starting work:

```powershell
cd c:\Users\mateo\ai_diffusion_state
make preflight
python scripts/15_pcs_status.py
```

Expected state before production work:

- Stub controls purged or absent.
- Geo evidence hygiene passes or gives explicit issues to fix.
- `data/processed/smart_factories_clean.csv` exists after build.
- `outputs/tables/table_16_geo_evidence_quality.csv` exists after `make analysis`.

If `make preflight` fails, fix the reported issue before editing data files.

---

# Engineer A — Real EPS/NBS city controls

## Mission

Supply real city-year controls so the pipeline can generate `data/processed/city_controls_year.csv`, merge controls into `analysis_city_year_panel.csv`, and produce paper-valid Tables 5–8.

This workstream is the only way to move from baseline association to controlled association. CI stub controls are forbidden for paper claims.

## Step A1 — Acquire EPS/NBS city-year controls

Preferred sources:

- EPS China City Statistics: `https://epschinastats.com/db_city.html`
- NBS yearbooks / city tables: `https://www.stats.gov.cn/sj/ndsj/`

Export data for all cities appearing in:

```text
data/processed/pilot_zones.csv
data/processed/smart_factory_city_year.csv
```

Target years:

```text
2019, 2020, 2021, 2022, 2023, 2024
```

If 2025 is unavailable, leave 2025 missing and document it. The adoption models need 2024–2025, but if controls stop at 2024, the paper must either restrict controlled models to 2024 or carry controls forward only with an explicit caveat.

## Step A2 — Place raw files locally

Put files only here:

```text
data/raw/city_controls/
```

Allowed formats:

```text
.csv
.xlsx
.xls
```

Good filenames:

```text
eps_china_city_stats_2019_2024.csv
nbs_city_controls_2019_2024.xlsx
```

Forbidden files:

```text
city_controls_ci_stub.csv
city_controls_ingest_template.csv as the only input
```

The raw directory is gitignored. Do not change `.gitignore` to commit proprietary files.

## Step A3 — Column contract

Every production raw file, or the combined set of files, must provide these fields after aliases are applied:

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

Critical details:

- `city` must match repo spelling, for example `Beijing`, `Shanghai`, `Hangzhou`, `Wuhan`.
- `year` must be integer.
- GDP and money variables must document units in `source_name` or `docs/source_notes/city_controls.md`.
- State whether values are nominal or deflated.
- Do not fill missing fields with zeros unless the true value is zero.
- Do not use the ingest template as evidence.

## Step A4 — Validate raw controls before build

Run:

```powershell
python scripts/06a_validate_city_controls_raw.py
```

Expected success:

```text
OK N raw file(s); M city-year rows; columns complete.
```

If validation fails:

- Missing columns: add/rename columns or add a second export file.
- Read error: save as CSV UTF-8 or clean the workbook sheet.
- Stub warning: run `make purge-stub-controls` and remove local stub files.

## Step A5 — Build production controls

Run:

```powershell
make purge-stub-controls
make city-controls
make panel
make analysis
make sync-paper-stats
make main-tables
make production-check
make validate-sprint
python scripts/15_pcs_status.py
```

Expected success checks:

1. `data/processed/city_controls_year.csv` exists.
2. `source_name` does not contain `pipeline_ci_stub_not_for_paper`.
3. `python scripts/15_pcs_status.py` reports production controls merged.
4. `outputs/tables/table_5_controlled_adoption_models.csv` contains real estimates, not only `term = skipped`.
5. `outputs/tables/table_7_pilot_city_balance.csv` contains covariate balance.
6. `outputs/tables/table_8_matched_adoption_models.csv` either contains a real matched estimate or a documented matching failure.
7. `make production-check` exits 0.

## Step A6 — Paper-use rule

Table 5 is citable only when:

```powershell
make production-check
make validate-sprint
```

both exit 0 and `source_name` confirms EPS/NBS or another real city-statistics source.

If real controls cannot be obtained, paper language must say:

```text
Controlled adoption, balance, and matching specifications remain blocked pending EPS/NBS city controls. The paper reports baseline and hub-exclusion associations only.
```

---

# Engineer B — City-resolution audit and external verification

## Mission

Strengthen city-resolution credibility in two ways:

1. Complete the stratified sample audit.
2. Convert at least 50 high-priority rule-based city assignments into externally verified assignments using real non-list URLs.

## Part B1 — Stratified audit sample

Edit:

```text
data/audit/city_resolution_sample_audit.csv
```

This file contains approximately 70 rows. Fill the blank audit fields.

## B1.1 Audit decision values

Use exactly one of:

```text
confirmed
incorrect
uncertain
insufficient_evidence
```

Definitions:

- `confirmed`: assigned city is correct.
- `incorrect`: assigned city is wrong. Fill `corrected_city` and `corrected_province`.
- `uncertain`: evidence is ambiguous after reasonable review.
- `insufficient_evidence`: no usable evidence supports the assignment.

Required fields for every audited row:

```text
auditor_decision
audit_notes
auditor
audit_date
```

Date format:

```text
YYYY-MM-DD
```

For `incorrect` rows, also fill:

```text
corrected_city
corrected_province
```

## B1.2 Minimum audit completion

Before the paper reports audit rates, the file must contain at least:

```text
50 rule_based_text_inference rows with non-empty auditor_decision
20 official_location_exact rows with non-empty auditor_decision
```

There are currently no `external_evidence_verified` rows unless Part B2 is completed.

## B1.3 Commands after editing audit sample

Run:

```powershell
make apply-geo-updates
make recompute-audit
make sync-paper-stats
make validate-audit
make validate-geo
python scripts/15_pcs_status.py
```

Expected outputs:

```text
outputs/tables/table_17_geo_audit_error_rate.csv
paper/reviewer_results_snapshot.md updated by sync-paper-stats
```

Expected validation:

```text
make validate-audit exits 0
```

If `validate-audit` fails, fix every listed row-level issue before using Table 17 in the paper.

## B1.4 Paper-use rule

If audit is incomplete, paper must say:

```text
The city-resolution audit is pending; city-level results should be interpreted with rule-based geocoding caveats.
```

If audit is complete, paper may report confirmation and error rates from Table 17.

---

## Part B2 — External verification of high-priority projects

## B2.1 Generate or open the queue

Run, if the queue needs to be rebuilt:

```powershell
make external-verification-queue
```

Edit:

```text
data/interim/external_verification_queue.csv
```

The queue prioritizes rule-based rows by top smart-factory cities, pilot-zone cities, registry matches, and advanced export sectors.

## B2.2 External URL rules

Accepted external evidence:

- Company production-base page naming the city.
- Company annual report or ESG report naming the facility or production base.
- Local government or industrial-park notice naming the plant/project city.
- Subsidiary registry page with plant address.

Rejected evidence:

- Solarbe list page.
- JLTS list page.
- Empty URL.
- URL identical to the list-page URL.
- Generic company homepage that does not show city/facility information.
- Headquarters page unless the smart-factory project is explicitly at headquarters.

Accepted `external_evidence_type` values:

```text
company_annual_report
company_site_registry
industrial_park_page
project_registry
```

For each verified row, fill:

```text
external_evidence_url
external_evidence_type
audit_notes
```

Recommended optional fields if present:

```text
reviewer
review_date
```

## B2.3 Minimum target

Externally verify at least:

```text
50 rows
```

Priority order:

1. `priority_rank` 1–20.
2. Pilot-zone cities.
3. Top smart-factory cities.
4. `firm_registry_match` rows.
5. Advanced export sectors: semiconductors, batteries, AI servers, NEV, shipbuilding, steel, chemicals.

## B2.4 Apply external verification

After filling at least 50 rows with valid non-list URLs, run:

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

Expected success checks:

1. `make apply-geo-updates` prints `external verification rows applied: 50` or higher.
2. `outputs/tables/table_16_geo_evidence_quality.csv` reports `external_evidence_verified >= 50`.
3. `python scripts/15_pcs_status.py` reports external count >= 50.
4. `make validate-geo` exits 0.
5. `data/seed/smart_factory_city_overrides.csv` contains `resolution_class = external_evidence_verified` and non-empty `external_evidence_url` for those rows.

## B2.5 Paper-use rule

Do not call a row externally verified unless `resolution_class = external_evidence_verified` and it has a real non-list `external_evidence_url`.

Registry/list inference remains rule-based until a non-list external URL is added.

---

# Final production run

After Engineer A and Engineer B complete their workstreams, run:

```powershell
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

Paper is ready to cite Tables 5–8, 16, and 17 only if all commands exit 0 and `pcs_status` shows:

```text
City controls: production
Panel controls merged: yes
Geo evidence hygiene: OK
Audit validation: OK
External evidence verified: >= 50
```

# Failure modes and fixes

## `validate-controls-raw` fails missing columns

Fix the raw EPS/NBS export or add another file with the missing fields. Do not patch processed files manually.

## `production-check` fails stub leakage

Run:

```powershell
make purge-stub-controls
make city-controls
make panel
make analysis
make sync-paper-stats
make main-tables
make production-check
```

Then remove stale stub mentions from paper-facing files unless they are explicitly marked as development-only.

## `validate-geo` fails

Likely causes:

- External rows use Solarbe/JLTS list URLs.
- `resolution_class` missing.
- Legacy evidence labels are used as if externally verified.

Fix the relevant rows in `data/seed/smart_factory_city_overrides.csv` or `data/interim/external_verification_queue.csv`.

## `validate-audit` fails

Likely causes:

- Too few audited rows.
- Invalid `auditor_decision` value.
- Incorrect row without `corrected_city` or `corrected_province`.

Fix `data/audit/city_resolution_sample_audit.csv`.

# Paper language after successful completion

Allowed language:

```text
We merge 509 MIIT excellence-level smart-factory projects with China’s national AI pilot-zone map and city-year controls. All projects are assigned to cities, with assignments classified as official-location exact, rule-based inference, or externally verified. A stratified audit reports the observed error rate by resolution class. Baseline pilot-zone associations remain positive in the resolved-city universe but attenuate when direct-admin municipalities and major hubs are removed, supporting a hub-centered diffusion architecture rather than a uniform treatment effect.
```

Forbidden language:

```text
Pilot zones caused smart-factory adoption.
Smart-factory recognition proves productivity growth.
Registry matches are externally verified.
Stub-controlled models are paper results.
Event-study pre-trends validate the design.
```
