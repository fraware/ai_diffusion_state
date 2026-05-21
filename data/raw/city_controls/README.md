# City controls (EPS / NBS)

Place city-year statistical exports here before running:

```bash
make city-controls
make panel
make analysis
```

## Required files

One or more `.csv`, `.xlsx`, or `.xls` files with English column names (or aliases documented in `src/diffusion_state/build_city_controls.py`).

## Required columns

`city`, `province`, `year`, `gdp`, `gdp_per_capita`, `secondary_value_added`, `industrial_output`, `population`, `employment`, `average_wage`, `fdi`, `fixed_asset_investment`, `education_proxy`, `telecom_or_internet_proxy`, `foreign_trade`, `source_name`, `source_file`

## Outputs

- `data/processed/city_controls_year.csv`
- `data/processed/city_controls_missingness.csv`

See `docs/source_notes/city_controls.md`.

**Do not commit proprietary EPS/NBS downloads.** This directory is gitignored except this README.
