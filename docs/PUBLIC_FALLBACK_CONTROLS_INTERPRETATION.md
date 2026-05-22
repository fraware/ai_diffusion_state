# Public Fallback Controls — Interpretation Memo

## Status

The strict EPS/NBS production-control gate remains skipped. That is expected because the public ChinaUTC fallback lacks FDI and fixed-asset investment.

The new appendix-only table is:

```text
outputs/tables/table_5b_public_fallback_controls.csv
paper/main_tables/table_I_appendix_public_fallback_controls.csv
```

Evidence tier:

```text
partial_public_controls_appendix_only
```

Paper use:

```text
Appendix robustness only; not EPS-equivalent Table 5.
```

## Current Table 5b result

Sample:

```text
chinautc_public_fallback_2024_only
52 cities, 51 complete cases after dropna, year 2024 only
```

Controls included:

```text
log_gdp
log_population
secondary_industry_share
foreign_trade_log1p
telecom_log1p
industrial_output_log1p
```

Missing from public fallback:

```text
FDI
fixed-asset investment
```

Pilot-zone rows:

| Model | Coefficient | Std. error | p-value | N | R² |
|---|---:|---:|---:|---:|---:|
| 5b OLS count | +1.58 | 0.65 | 0.020 | 51 | 0.52 |
| 5c OLS log count | +0.50 | 0.21 | 0.018 | 51 | 0.51 |
| 5d Poisson count | +0.23 | 0.29 | 0.43 | 51 | — |

## Interpretation

The public fallback result is useful because the pilot-zone association survives after controlling for public China City Statistical Yearbook measures of city GDP, population, secondary-industry structure, foreign trade, telecom, and industrial-output proxies in the 2024 subset.

The coefficient shrinks substantially relative to the uncontrolled full-panel association, which is consistent with the paper’s hub-centered interpretation: pilot-zone status partly captures pre-existing city scale and industrial capacity, but pilot-zone cities still show higher listed smart-factory counts within the limited public-control sample.

## What this supports

Allowed language:

```text
As appendix robustness, the pilot-zone association remains positive in a 2024 ChinaUTC public-controls cross-section covering 51 complete city observations. The result is significant in OLS count and log-count specifications but not in the Poisson count specification.
```

Allowed interpretation:

```text
This supports the descriptive claim that the pilot-zone pattern is not entirely explained by GDP, population, industrial structure, foreign trade, telecom, and industrial-output proxies in the limited public-control sample.
```

## What this does not support

Do not say:

```text
The strict EPS/NBS controlled model passes.
```

Do not say:

```text
Table 5 establishes a controlled treatment effect.
```

Do not say:

```text
Pilot zones caused smart-factory adoption.
```

Do not say:

```text
The production controlled design is complete.
```

## Paper wording

Use this wording:

```text
As an appendix robustness check, we estimate a partial public-controls specification using China City Statistical Yearbook tables obtained through ChinaUTC. This public fallback includes GDP, population, secondary-industry structure, and limited 2024 coverage for foreign trade, telecom, and industrial-output proxies. Because FDI and fixed-asset investment are unavailable in the public bundle, this specification is not treated as equivalent to the EPS/NBS production-control design. In this 2024 cross-section, pilot-zone status remains positively associated with listed smart-factory counts in OLS count and log-count models, while the Poisson count specification is not statistically significant.
```

## Next step

If the paper needs a stronger controlled claim, obtain EPS/NBS city controls with FDI and fixed-asset investment. Otherwise keep Table 5b in the appendix and frame the main paper around measurement, geography, hub concentration, and descriptive robustness.
