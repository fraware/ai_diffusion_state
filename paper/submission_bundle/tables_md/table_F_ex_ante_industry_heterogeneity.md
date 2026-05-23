### Table F

*City-industry adoption models — key terms only (ex ante exposure interactions).*

**Claim tier:** `suggestive_mechanism` | **Claim ID:** `city_industry_exposure_ex_ante` | **Placement:** main

*Note: FE coefficients omitted; tag-derived spec is descriptive-only (not for main causal claims).*

| model                                          | term                             |       coef |   std_err |     p_value |   n_obs | exposure_source         |
|:-----------------------------------------------|:---------------------------------|-----------:|----------:|------------:|--------:|:------------------------|
| city_industry_pilot_x_exposure_ex_ante         | Intercept                        |  0.831825  | 0.126274  | 4.47481e-11 |     385 | ex_ante                 |
| city_industry_pilot_x_exposure_ex_ante         | pilot_zone                       | -0.166057  | 0.0988302 | 0.0929129   |     385 | ex_ante                 |
| city_industry_pilot_x_exposure_ex_ante         | high_exposure_ex_ante            | -0.0626271 | 0.0800926 | 0.434253    |     385 | ex_ante                 |
| city_industry_pilot_x_exposure_ex_ante         | pilot_zone:high_exposure_ex_ante |  0.262465  | 0.0786456 | 0.000845941 |     385 | ex_ante                 |
| city_industry_pilot_x_score_ex_ante            | Intercept                        |  0.780737  | 0.130601  | 2.25858e-09 |     385 | ex_ante                 |
| city_industry_pilot_x_score_ex_ante            | pilot_zone                       | -0.206648  | 0.109021  | 0.0580291   |     385 | ex_ante                 |
| city_industry_pilot_x_score_ex_ante            | ai_exposure_ex_ante              |  0.0129569 | 0.0405087 | 0.749078    |     385 | ex_ante                 |
| city_industry_pilot_x_score_ex_ante            | pilot_zone:ai_exposure_ex_ante   |  0.158893  | 0.0543758 | 0.00347641  |     385 | ex_ante                 |
| city_industry_pilot_x_exposure_tag_descriptive | Intercept                        |  0.831825  | 0.126274  | 4.47481e-11 |     385 | descriptive_tag_derived |
| city_industry_pilot_x_exposure_tag_descriptive | pilot_zone                       | -0.166057  | 0.0988302 | 0.0929129   |     385 | descriptive_tag_derived |
| city_industry_pilot_x_exposure_tag_descriptive | high_exposure_sector             | -0.0626271 | 0.0800926 | 0.434253    |     385 | descriptive_tag_derived |
| city_industry_pilot_x_exposure_tag_descriptive | pilot_zone:high_exposure_sector  |  0.262465  | 0.0786456 | 0.000845941 |     385 | descriptive_tag_derived |

Source: `paper/main_tables/table_F_ex_ante_industry_heterogeneity.csv` (903 rows in repository).
