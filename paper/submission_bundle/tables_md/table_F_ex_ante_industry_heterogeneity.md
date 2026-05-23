### Table F

*City-industry adoption models — key terms only (ex ante exposure interactions).*

**Claim tier:** `suggestive_mechanism` | **Claim ID:** `city_industry_exposure_ex_ante` | **Placement:** main

*Note: FE coefficients omitted; tag-derived spec is descriptive-only (not for main causal claims).*

                                         model                             term      coef  std_err      p_value  n_obs         exposure_source
        city_industry_pilot_x_exposure_ex_ante                        Intercept  0.831825 0.126274 4.474807e-11    385                 ex_ante
        city_industry_pilot_x_exposure_ex_ante                       pilot_zone -0.166057 0.098830 9.291295e-02    385                 ex_ante
        city_industry_pilot_x_exposure_ex_ante            high_exposure_ex_ante -0.062627 0.080093 4.342533e-01    385                 ex_ante
        city_industry_pilot_x_exposure_ex_ante pilot_zone:high_exposure_ex_ante  0.262465 0.078646 8.459407e-04    385                 ex_ante
           city_industry_pilot_x_score_ex_ante                        Intercept  0.780737 0.130601 2.258576e-09    385                 ex_ante
           city_industry_pilot_x_score_ex_ante                       pilot_zone -0.206648 0.109021 5.802915e-02    385                 ex_ante
           city_industry_pilot_x_score_ex_ante              ai_exposure_ex_ante  0.012957 0.040509 7.490779e-01    385                 ex_ante
           city_industry_pilot_x_score_ex_ante   pilot_zone:ai_exposure_ex_ante  0.158893 0.054376 3.476407e-03    385                 ex_ante
city_industry_pilot_x_exposure_tag_descriptive                        Intercept  0.831825 0.126274 4.474807e-11    385 descriptive_tag_derived
city_industry_pilot_x_exposure_tag_descriptive                       pilot_zone -0.166057 0.098830 9.291295e-02    385 descriptive_tag_derived
city_industry_pilot_x_exposure_tag_descriptive             high_exposure_sector -0.062627 0.080093 4.342533e-01    385 descriptive_tag_derived
city_industry_pilot_x_exposure_tag_descriptive  pilot_zone:high_exposure_sector  0.262465 0.078646 8.459407e-04    385 descriptive_tag_derived

Source: `paper/main_tables/table_F_ex_ante_industry_heterogeneity.csv` (903 rows in repository).
