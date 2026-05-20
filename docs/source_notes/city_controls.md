# City controls — source notes

## Status

**Not populated by default.** The pipeline does not scrape or synthesize city statistics.

## Required input

Place one or more EPS China City Statistics or NBS city-year exports under:

```text
data/raw/city_controls/
```

Supported formats: `.csv`, `.xlsx`, `.xls`

## Build

```bash
python -c "import sys; sys.path.insert(0,'src'); from diffusion_state.build_city_controls import build_city_controls_year; build_city_controls_year()"
```

Outputs:

- `data/processed/city_controls_year.csv`
- `data/processed/city_controls_missingness.csv`

## Column contract

Files must map to `docs/DATA_CONTRACTS.md` (`city_controls_year.csv`). Rename EPS/NBS columns to:

`city`, `province`, `year`, `gdp`, `gdp_per_capita`, `secondary_value_added`, `industrial_output`, `population`, `employment`, `average_wage`, `fdi`, `fixed_asset_investment`, `education_proxy`, `telecom_or_internet_proxy`, `foreign_trade`, `source_name`, `source_file`

Or use aliases documented in `build_city_controls.py` (`gdp100m`, `city_name`, etc.).

## Official sources

| Source | URL | Access |
|---|---|---|
| EPS China City Statistics | https://epschinastats.com/db_city.html | Institutional subscription |
| NBS China Statistical Yearbooks | https://www.stats.gov.cn/sj/ndsj/ | Publications / tables |

Document `source_name`, nominal vs real units, and coverage years in `source_file` metadata when exporting from EPS.

## Merge

After controls exist, re-run:

```bash
make panel
make analysis
```

`analysis_city_year_panel.csv` will left-join controls on `city`, `year`.
