### Table A

*Dataset counts and coverage (pilot zones, smart-factory projects, geo evidence classes).*

**Claim tier:** `measured` | **Claim ID:** `measurement_pilot_zones` | **Placement:** main

| dataset                                   | unit          |   observations | years_covered                | source                                         |
|:------------------------------------------|:--------------|---------------:|:-----------------------------|:-----------------------------------------------|
| pilot_zones                               | city/county   |             17 | 2019-2021                    | data/processed/pilot_zones.csv                 |
| smart_factories_clean                     | project       |            509 | 2024, 2025                   | data/processed/smart_factories_clean.csv       |
| smart_factory_city_year                   | city-year     |            224 | 2024, 2025 (resolved cities) | data/processed/smart_factory_city_year.csv     |
| smart_factory_province_year               | province-year |             59 | 2024, 2025                   | data/processed/smart_factory_province_year.csv |
| smart_factories_city_unknown              | project       |              0 | 2024, 2025                   | province-only location in MIIT tables          |
| smart_factories_city_resolved             | project       |            509 | 2024, 2025                   | parser + audited geo overrides                 |
| geo_resolution_rule_based_text_inference  | project       |            357 | 2024, 2025                   | data/processed/city_resolution_register.csv    |
| geo_resolution_official_location_exact    | project       |            102 | 2024, 2025                   | data/processed/city_resolution_register.csv    |
| geo_resolution_external_evidence_verified | project       |             50 | 2024, 2025                   | data/processed/city_resolution_register.csv    |

Source: `paper/main_tables/table_A_dataset_counts.csv` (9 rows in repository).
