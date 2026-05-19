# Data dictionary

## `pilot_zones.csv`

Canonical schema is defined in [DATA_CONTRACTS.md](DATA_CONTRACTS.md). Key fields:

| column | type | definition |
|---|---|---|
| pilot_unit_id | string | Stable primary key (slug). |
| city | string | Normalized city/county for joins. |
| province | string | Province-level unit. |
| admin_level | string | `city`, `municipality`, or `county`. |
| pilot_year | integer | First treatment year. |
| created_date / announced_date | date | ISO dates when known. |
| date_quality | string | `exact_date`, `exact_year`, `inferred_year`, or `uncertain`. |
| source_url / source_name | string | Provenance. |
| pilot_zone | integer | Always 1 in this table. |

## `smart_factories_clean.csv`

| column | type | definition |
|---|---|---|
| batch | string | 2024 first batch or 2025 batch. |
| year | integer | Recognition/publication year. |
| firm | string | Raw firm name. |
| firm_std | string | Standardized firm name. |
| project | string | Smart-factory project name. |
| province | string | Province-level unit. |
| city | string | City when recoverable from project/source/company registry. |
| city_std | string | Standardized city name for joins. |
| sector_raw | string | Raw sector or inferred industry. |
| sector_harmonized | string | Harmonized industry class. |
| detected_keywords | string | Matched AI/digital/industrial keywords. |
| has_industrial_ai_keyword | bool | Any industrial AI keyword present. |
| source_url | string | Evidence URL. |

## `panel_city_year.csv`

| column | type | definition |
|---|---|---|
| city_std | string | Standardized city. |
| year | integer | Year. |
| smart_factory_count | numeric | Number of smart factory projects in city-year. |
| pilot_year | numeric | Pilot-zone designation year if treated. |
| post_pilot | integer | 1 if city-year after pilot designation. |
| years_since_pilot | numeric | Event-time variable. |
| controls... | numeric | EPS/NBS variables. |
