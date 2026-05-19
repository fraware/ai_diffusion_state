# Data Contracts

This file defines the canonical schemas for the project. Engineers should treat these as contracts. If a contract must change, update this file in the same PR as the code change.

## Naming conventions

- Use lowercase snake_case for all columns.
- Use UTF-8 for all files.
- Preserve original Chinese text in `_zh` fields.
- Use `_en` fields only for translations.
- Use ISO date strings when exact dates are available.
- Use integer years when only year-level timing is available.
- Use `unknown` rather than blank strings for categorical unknowns.
- Use missing values for genuinely unavailable numeric values.

## Canonical geographic fields

```text
province
city
county_or_district
admin_level
city_code
province_code
geo_confidence
```

`geo_confidence` values:

```text
exact
high
medium
low
unknown
```

## pilot_zones.csv

Purpose: policy treatment table.

Primary key:

```text
pilot_unit_id
```

Required columns:

```text
pilot_unit_id
city
province
admin_level
pilot_zone
pilot_year
created_date
announced_date
specialization_zh
specialization_en
source_url
source_name
date_quality
notes
```

Allowed values:

```text
pilot_zone: 0, 1
date_quality: exact_date, exact_year, inferred_year, uncertain
```

Validation tests:

1. Exactly one row per pilot unit.
2. At least 17 treated units in the canonical 2021 table.
3. Beijing, Shanghai, Hangzhou, Hefei, Shenzhen, Tianjin, and Deqing must have 2019 pilot years.
4. Chengdu, Chongqing, Jinan, and Xi'an must have 2020 pilot years.
5. Every treated row must have a source URL.

## smart_factories_clean.csv

Purpose: project-level adoption measure.

Primary key:

```text
project_id
```

Required columns:

```text
project_id
list_year
batch
firm_name_zh
firm_name_en
project_name_zh
project_name_en
province
city
city_confidence
industry_code
industry_label
industry_confidence
ai_scenario_tags
technology_tags
source_url
source_file
row_number_original
parse_method
manual_override_flag
notes
```

Allowed confidence values:

```text
exact
high
medium
low
unknown
```

Allowed parse methods:

```text
html_table
pdf_table
xlsx
manual_seed
ocr
manual_override
```

Validation tests:

1. `project_id` is unique.
2. `firm_name_zh`, `project_name_zh`, `province`, `list_year`, and `source_url` are non-null.
3. `city_confidence` and `industry_confidence` use allowed values.
4. Aggregated project counts reconcile to city-year and city-industry-year tables.
5. `manual_override_flag = 1` rows have notes.

## smart_factory_city_year.csv

Purpose: city-year adoption panel.

Primary key:

```text
city, year
```

Required columns:

```text
city
province
year
smart_factory_projects
smart_factory_projects_ai_tagged
smart_factory_projects_industrial_ai
num_distinct_firms
num_distinct_industries
source_rows
unknown_city_rows_excluded
```

Validation tests:

1. No duplicate city-year rows.
2. Counts are non-negative integers.
3. Sum of `source_rows` plus excluded unknown-city rows reconciles to project-level total.

## smart_factory_city_industry_year.csv

Purpose: city-industry-year adoption panel.

Primary key:

```text
city, industry_code, year
```

Required columns:

```text
city
province
industry_code
industry_label
year
smart_factory_projects
smart_factory_projects_ai_tagged
num_distinct_firms
source_rows
```

Validation tests:

1. No duplicate city-industry-year rows.
2. Industry labels are non-null.
3. Aggregation to city-year reconciles with `smart_factory_city_year.csv`.

## export_outcomes_hs6_year.csv

Purpose: product-level export outcomes from BACI.

Primary key:

```text
year, hs6
```

Required columns:

```text
year
hs6
export_value_usd
quantity
unit
unit_value
export_value_growth
quantity_growth
unit_value_growth
num_destinations
world_export_value_usd
china_world_market_share
```

Validation tests:

1. No duplicate year-HS6 rows.
2. Export values and quantities are non-negative.
3. Unit value is missing when quantity is zero or missing.
4. Market share is between 0 and 1 when defined.

## hs_to_smart_factory_sector_bridge.csv

Purpose: connect smart-factory sectors to trade products.

Primary key:

```text
bridge_id
```

Required columns:

```text
bridge_id
smart_factory_industry_code
smart_factory_industry_label
hs_level
hs_code
hs_description
mapping_confidence
mapping_reason
source_or_method
```

Allowed `hs_level` values:

```text
HS2
HS4
HS6
```

Allowed `mapping_confidence` values:

```text
high
medium
low
```

Validation tests:

1. Every smart-factory industry used in analysis has at least one bridge row.
2. No HS code appears with invalid length for its HS level.
3. Low-confidence mappings are excluded from primary specifications or separately flagged.

## city_controls_year.csv

Purpose: city-level controls.

Primary key:

```text
city, year
```

Required columns:

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

Validation tests:

1. No duplicate city-year rows.
2. City names match canonical city dictionary.
3. Missingness report is generated for every variable.
4. Currency units and nominal/real status are documented.

## analysis_city_year_panel.csv

Purpose: final city-year panel for adoption models.

Primary key:

```text
city, year
```

Required columns:

```text
city
province
year
pilot_zone
pilot_year
post_pilot
years_since_pilot
smart_factory_projects
smart_factory_projects_ai_tagged
gdp
gdp_per_capita
industrial_output
secondary_value_added
population
average_wage
fdi
fixed_asset_investment
telecom_or_internet_proxy
foreign_trade
```

Validation tests:

1. No duplicate city-year rows.
2. `post_pilot` equals 1 only when `year >= pilot_year` for treated cities.
3. Never-treated cities have missing `pilot_year`, `post_pilot = 0`, and missing `years_since_pilot`.
4. Smart-factory missing counts are filled as zero only for city-years in the analysis universe.

## analysis_city_industry_year_panel.csv

Purpose: final city-industry-year panel for interaction models and export linkage.

Primary key:

```text
city, industry_code, year
```

Required columns:

```text
city
province
industry_code
industry_label
year
pilot_zone
pilot_year
post_pilot
years_since_pilot
smart_factory_projects
smart_factory_projects_ai_tagged
ai_exposure_industry
export_value_growth
unit_value_growth
mapping_confidence
controls_available
```

Validation tests:

1. No duplicate city-industry-year rows.
2. AI exposure is time-invariant unless explicitly documented.
3. Export outcomes only appear when mapping confidence is medium or high in primary data.
4. All model samples are reproducible from filtering scripts.

## Output contracts

Tables must be exported to:

```text
outputs/tables/
```

Figures must be exported to:

```text
outputs/figures/
```

Every table used in the paper must have a script that creates it. Every figure used in the paper must have a script that creates it. Notebooks may be used for exploration, but paper outputs must come from scripts.
