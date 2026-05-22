# Human Input Blockers — Action Plan

**Sprint decision (2026-05-22):** Workstream A is **closed** on the public ChinaUTC path. Strict Table 5 stays skipped. Use `paper/main_tables/table_I_appendix_public_fallback_controls.csv` for appendix robustness only. **Critical path is now B1 + B2.** See [`docs/CURRENT_SPRINT_PRIORITIES.md`](CURRENT_SPRINT_PRIORITIES.md).

## Current status

The pipeline is correctly blocked where human input is still missing. Failures are expected and desirable because they prevent fabricated data from entering the paper.

Current blockers:

1. **Strict EPS/NBS Table 5** remains skipped (no FDI / fixed-asset in public bundle). **Table I / 5b** is the valid public appendix result — do not keep expanding ChinaUTC without FDI or fixed-asset tables.
2. Tables 7 and 8 remain skipped when strict production controls are unavailable for the adoption-year gate.
4. `validate-audit` fails because `data/audit/city_resolution_sample_audit.csv` has 0/70 `auditor_decision` values filled.
5. External verification count is 0 because `data/interim/external_verification_queue.csv` has 0/50 non-list `external_evidence_url` values filled.

These should not be bypassed with synthetic data, guessed audit labels, or generic web URLs.

## Non-negotiable rule

Do not invent:

- EPS/NBS city controls;
- audit decisions;
- external evidence URLs;
- production-control estimates;
- externally verified city assignments.

If the relevant field is not backed by a real source or a human audit decision, it must remain blank and the paper must describe the limitation.

---

# Workstream A — Real city controls

## Status: closed on public path; EPS/NBS only if export appears

The ChinaUTC public fallback is complete (`chinautc_city_controls_public_fallback.csv`, Table I). **No further ChinaUTC engineering** unless new files contain FDI or fixed-asset investment.

## Required human input (strict EPS/NBS only)

A researcher with EPS/NBS access must export real city-year data.

Place at least one real file here:

```text
data/raw/city_controls/
```

Example filename:

```text
data/raw/city_controls/eps_china_city_stats_2019_2024.csv
```

Do not commit proprietary EPS/NBS downloads.

## Required columns

The file or combination of files must include:

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

Target years:

```text
2019, 2020, 2021, 2022, 2023, 2024
```

If 2025 is unavailable, document that explicitly in `docs/source_notes/city_controls.md`.

## Commands after file placement

```powershell
cd c:\Users\mateo\ai_diffusion_state
make purge-stub-controls
python scripts/06a_validate_city_controls_raw.py
make city-controls
make panel
make analysis
make sync-paper-stats
make main-tables
make production-check
python scripts/15_pcs_status.py
```

## Success condition

`python scripts/15_pcs_status.py` must report:

```text
City controls: production
Panel controls merged: yes
```

Table 5 must contain real controlled estimates, and Tables 7–8 must no longer be skipped solely because controls are absent.

## If this cannot be completed

The paper must use only baseline/hub-exclusion descriptive evidence and state:

```text
Controlled adoption, balance, and matching specifications remain blocked pending EPS/NBS city controls.
```

---

# Workstream B1 — City-resolution audit decisions

## Required human input

A human auditor must fill:

```text
data/audit/city_resolution_sample_audit.csv
```

Minimum required decisions:

```text
50 rule_based_text_inference rows
20 official_location_exact rows
```

Allowed values:

```text
confirmed
incorrect
uncertain
insufficient_evidence
```

For every audited row, fill:

```text
auditor_decision
audit_notes
auditor
audit_date
```

For incorrect rows, also fill:

```text
corrected_city
corrected_province
```

## Commands after editing

```powershell
make apply-geo-updates
make recompute-audit
make validate-audit
make sync-paper-stats
python scripts/15_pcs_status.py
```

## Success condition

`make validate-audit` exits 0 and `outputs/tables/table_17_geo_audit_error_rate.csv` reports confirmation/error/uncertainty rates by resolution class.

## If this cannot be completed

The paper must say:

```text
The city-resolution audit is pending; city-level results should be interpreted with rule-based geocoding caveats.
```

---

# Workstream B2 — External verification URLs

## Required human input

Fill at least 50 rows in:

```text
data/interim/external_verification_queue.csv
```

Required fields:

```text
external_evidence_url
external_evidence_type
audit_notes
```

Accepted external evidence types:

```text
company_annual_report
company_site_registry
industrial_park_page
project_registry
```

Accepted evidence URLs:

- company production-base page naming the city;
- annual report or ESG report naming the facility or production base;
- local-government or industrial-park notice naming the project/factory city;
- subsidiary or registry page with plant address.

Rejected evidence URLs:

- `cn.solarbe.com` list page;
- `jlts.com.cn` list page;
- generic homepage without facility location;
- headquarters page unless the project is explicitly at headquarters;
- empty URL.

## Commands after editing

```powershell
make apply-geo-updates
make geo-audit
make validate-geo
make panel
make analysis
make sync-paper-stats
make main-tables
python scripts/15_pcs_status.py
```

## Success condition

`python scripts/15_pcs_status.py` must report:

```text
External evidence verified: >= 50
```

and `outputs/tables/table_16_geo_evidence_quality.csv` must include at least 50 `external_evidence_verified` projects.

## If this cannot be completed

The paper may still use city assignments, but must describe them as:

```text
official-location exact or rule-based city assignments, with external verification pending.
```

---

# What can proceed immediately without human input

The team can proceed with a descriptive paper package using existing outputs only if the paper avoids controlled-association claims and avoids externally verified geocoding claims.

Allowed current claim:

```text
The project constructs a reproducible measurement pipeline linking national AI pilot zones and MIIT excellence-level smart-factory recognition, and shows that listed projects are concentrated in pilot-zone and hub cities.
```

Disallowed current claims:

```text
Pilot zones caused adoption.
Controlled models support the association.
City assignments have been externally verified.
The audit confirms a low error rate.
```

# Recommended immediate action

1. Assign one person with EPS/NBS access to Workstream A.
2. Assign one person with Chinese-language source-checking ability to Workstream B1.
3. Assign two people to Workstream B2, splitting 25 external-verification rows each.
4. Do not modify model language until these three workstreams pass validation.

# Final unlock command sequence

After all human-input files are filled:

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

Paper-ready status requires:

```text
City controls: production
Panel controls merged: yes
Sample audit: completed
External evidence verified: >= 50
Geo evidence hygiene: OK
No stub leakage
No stale paper numbers
```
