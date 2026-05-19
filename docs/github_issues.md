# GitHub issue backlog

## Milestone 0 — Repository activation

### Issue 1 — Initialize repo and CI
**Labels:** engineering, infrastructure  
**Owner:** engineering lead  
**Acceptance criteria:** repo installs with `pip install -e .[dev]`; `make test` passes; GitHub Actions runs tests on PRs.

### Issue 2 — Protect data/raw from accidental commits
**Labels:** engineering, data-governance  
**Acceptance criteria:** `.gitignore` excludes large raw files; README tells engineers how to store large files locally or in object storage.

## Milestone 1 — Treatment data

### Issue 3 — Finalize AI pilot-zone treatment table
**Labels:** data, policy  
**Acceptance criteria:** `data/processed/pilot_zones.csv` has 17 rows matching Xinhua Dec 2021 list; first 11 include CSET dates; source URL present for every row.

### Issue 4 — Validate pilot years from MOST letters
**Labels:** data-validation, policy  
**Acceptance criteria:** each post-2020 city has a source-backed year; uncertain dates are marked with `date_quality = inferred`.

## Milestone 2 — Smart-factory adoption data

### Issue 5 — Parse 2024 first-batch excellence smart-factory list
**Labels:** data, scraping, core  
**Acceptance criteria:** `smart_factories_2024.csv` contains exactly 235 rows; firm/project/province non-null; source saved in `data/raw`.

### Issue 6 — Parse 2025 excellence smart-factory list
**Labels:** data, scraping, core  
**Acceptance criteria:** `smart_factories_2025.csv` contains exactly 274 rows; firm/project/province non-null; source saved in `data/raw`.

### Issue 7 — Standardize firm, province, and city names
**Labels:** data-cleaning, core  
**Acceptance criteria:** all province names harmonized; city recovered for at least 85% of projects using project text, firm registry, local news, or manual validation.

### Issue 8 — Classify smart-factory projects by industrial AI scenario
**Labels:** nlp, data-cleaning  
**Acceptance criteria:** each project tagged with at least one scenario where applicable: machine vision, predictive maintenance, scheduling, digital twin, logistics, robotics, quality inspection, AI server, semiconductor, battery, vehicle, steel, petrochemical.

### Issue 9 — Build smart-factory city-year and city-industry-year tables
**Labels:** data, core  
**Acceptance criteria:** `smart_factory_city_year.csv` and `smart_factory_city_industry_year.csv` generated; row counts reconcile with raw 235 + 274 total.

## Milestone 3 — Outcomes

### Issue 10 — Build BACI China export panel
**Labels:** data, trade  
**Acceptance criteria:** China HS6 exports available for 2017-2024 using HS17; export values, quantities, unit values, growth rates computed.

### Issue 11 — Create HS-to-industry bridge
**Labels:** data, trade, mapping  
**Acceptance criteria:** smart-factory sectors mapped to HS2/HS4/HS6 families with explicit mapping confidence.

### Issue 12 — Import EPS/NBS city controls
**Labels:** data, controls  
**Acceptance criteria:** city-year controls created for GDP, industrial output, population, wages, FDI, education, telecom/internet, fixed-asset investment, foreign trade.

## Milestone 4 — Analysis

### Issue 13 — Produce descriptive adoption maps
**Labels:** analysis, visualization  
**Acceptance criteria:** maps or tables show smart-factory counts by province/city and overlap with pilot zones.

### Issue 14 — Baseline pilot-zone event study
**Labels:** econometrics, core  
**Acceptance criteria:** event-study table/figure with pre-trends and post-treatment coefficients for smart-factory adoption.

### Issue 15 — Industry exposure interaction
**Labels:** econometrics, core  
**Acceptance criteria:** estimates for `post_pilot × AI_exposure_industry`; exposure measure documented.

### Issue 16 — Export-upgrading module
**Labels:** econometrics, trade  
**Acceptance criteria:** sector-level smart-factory exposure linked to export growth and unit-value growth.

## Milestone 5 — Paper production

### Issue 17 — Generate summary tables for paper
**Labels:** paper, tables  
**Acceptance criteria:** Table 1 dataset summary, Table 2 top smart-factory cities, Table 3 baseline regressions exported to `/outputs/tables`.

### Issue 18 — Write data appendix
**Labels:** paper, documentation  
**Acceptance criteria:** appendix explains every source, construction step, exclusion rule, and validation check.

### Issue 19 — Write reproducibility note
**Labels:** paper, reproducibility  
**Acceptance criteria:** instructions allow a new engineer to rebuild all processed data from raw inputs.

### Issue 20 — Internal red-team memo
**Labels:** research, quality  
**Acceptance criteria:** memo identifies all threats to identification and what the paper can honestly claim.
