### Table D

*Hub-exclusion robustness for pilot-zone association in city-year adoption models.*

**Claim tier:** `robust_association` | **Claim ID:** `hub_robustness` | **Placement:** main

| exclusion_rule                                    | spec     |   n_cities |   n_projects | model          | term       |    coef |   std_err |     p_value | formula                                       | interpretation                                                              |   coefficient_relative_to_full_sample |   projects_remaining_share |
|:--------------------------------------------------|:---------|-----------:|-------------:|:---------------|:-----------|--------:|----------:|------------:|:----------------------------------------------|:----------------------------------------------------------------------------|--------------------------------------:|---------------------------:|
| full_sample                                       | baseline |        160 |          507 | baseline_count | pilot_zone | 4.54566 |  0.877318 | 2.20328e-07 | smart_factory_projects ~ pilot_zone + C(year) | baseline association (all resolved cities)                                  |                              1        |                   1        |
| drop_beijing_shanghai_shenzhen_hangzhou           | baseline |        156 |          439 | baseline_count | pilot_zone | 3.66783 |  0.768116 | 1.79614e-06 | smart_factory_projects ~ pilot_zone + C(year) | association weakens after dropping four mega-hubs                           |                              0.806887 |                   0.865878 |
| drop_beijing_shanghai_shenzhen_hangzhou_guangzhou | baseline |        155 |          431 | baseline_count | pilot_zone | 3.73193 |  0.828425 | 6.64182e-06 | smart_factory_projects ~ pilot_zone + C(year) | association weakens after dropping five mega-hubs                           |                              0.820988 |                   0.850099 |
| drop_direct_admin_municipalities                  | baseline |        156 |          419 | baseline_count | pilot_zone | 2.8986  |  0.514284 | 1.73851e-08 | smart_factory_projects ~ pilot_zone + C(year) | association weakens substantially when direct-admin municipalities excluded |                              0.637663 |                   0.82643  |
| drop_top_5_smart_factory_cities                   | baseline |        155 |          402 | baseline_count | pilot_zone | 2.9507  |  0.51174  | 8.11654e-09 | smart_factory_projects ~ pilot_zone + C(year) | association weakens when top adoption cities excluded                       |                              0.649126 |                   0.792899 |
| drop_top_10_gdp_cities                            | baseline |        150 |          408 | baseline_count | pilot_zone | 5.15435 |  1.29321  | 6.72836e-05 | smart_factory_projects ~ pilot_zone + C(year) | association under top-GDP-city exclusion (requires GDP controls)            |                              1.13391  |                   0.804734 |

Source: `paper/main_tables/table_D_hub_exclusion.csv` (6 rows in repository).
