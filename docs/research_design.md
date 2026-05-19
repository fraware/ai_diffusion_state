# Research design

## Core hypothesis

China's AI pilot-zone policy did not only support frontier research; it created local institutional machinery for industrial adoption. That machinery should be visible in smart-factory recognition and industrial AI scenarios.

## Treatment

`post_pilot_ct = 1` when city `c` has been selected as a National New Generation AI Innovation and Development Pilot Zone and year `t >= pilot_year`.

## Main outcome

`smart_factory_count_ct` measures the number of MIIT excellence-level smart-factory projects in city `c` and year `t`.

## MVP specification

```text
smart_factory_count_ct = beta * post_pilot_ct + city_FE + year_FE + controls_ct + error_ct
```

This is not the final causal design. It is the first diagnostic.

## Preferred specification

```text
smart_factory_count_cit = beta * post_pilot_ct * AI_exposure_i
                         + city_industry_FE
                         + province_year_FE
                         + industry_year_FE
                         + error_cit
```

The identifying claim is that AI pilot-zone designation should have stronger effects in industries where AI is technologically useful for production.

## Required robustness

1. Pre-trend event-study around pilot-year.
2. Drop Beijing, Shanghai, Shenzhen, Hangzhou.
3. Match pilot cities to non-pilot cities using pre-2018 GDP, manufacturing share, patents, universities, and telecom infrastructure.
4. Use only non-frontier industrial cities.
5. Use 2024 smart-factory adoption as outcome to avoid reverse causality from 2025 policy changes.

## Paper interpretation rule

Do not claim pilot zones caused all smart factories. Claim that pilot zones are one observable institutional component of the diffusion state and that adoption is concentrated where local AI policy, industrial base, and smart-manufacturing programs overlap.
