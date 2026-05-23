### Table D

*Hub-exclusion robustness for pilot-zone association in city-year adoption models.*

**Claim tier:** `robust_association` | **Claim ID:** `hub_robustness` | **Placement:** main

                                   exclusion_rule     spec  n_cities  n_projects          model       term     coef  std_err      p_value                                       formula                                                              interpretation  coefficient_relative_to_full_sample  projects_remaining_share
                                      full_sample baseline       160         507 baseline_count pilot_zone 4.545660 0.877318 2.203282e-07 smart_factory_projects ~ pilot_zone + C(year)                                  baseline association (all resolved cities)                             1.000000                  1.000000
          drop_beijing_shanghai_shenzhen_hangzhou baseline       156         439 baseline_count pilot_zone 3.667832 0.768116 1.796138e-06 smart_factory_projects ~ pilot_zone + C(year)                           association weakens after dropping four mega-hubs                             0.806887                  0.865878
drop_beijing_shanghai_shenzhen_hangzhou_guangzhou baseline       155         431 baseline_count pilot_zone 3.731935 0.828425 6.641824e-06 smart_factory_projects ~ pilot_zone + C(year)                           association weakens after dropping five mega-hubs                             0.820988                  0.850099
                 drop_direct_admin_municipalities baseline       156         419 baseline_count pilot_zone 2.898601 0.514284 1.738514e-08 smart_factory_projects ~ pilot_zone + C(year) association weakens substantially when direct-admin municipalities excluded                             0.637663                  0.826430
                  drop_top_5_smart_factory_cities baseline       155         402 baseline_count pilot_zone 2.950704 0.511740 8.116544e-09 smart_factory_projects ~ pilot_zone + C(year)                       association weakens when top adoption cities excluded                             0.649126                  0.792899
                           drop_top_10_gdp_cities baseline       150         408 baseline_count pilot_zone 5.154349 1.293213 6.728357e-05 smart_factory_projects ~ pilot_zone + C(year)            association under top-GDP-city exclusion (requires GDP controls)                             1.133906                  0.804734

Source: `paper/main_tables/table_D_hub_exclusion.csv` (6 rows in repository).
