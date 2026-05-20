# BACI export outcomes — source notes

## Status

**Not built in CI by default.** Place CEPII BACI HS17 yearly CSV files under `data/raw/baci/` before running `make baci`.

## Source

- Product: CEPII BACI
- URL: https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=37
- Documentation: https://www.cepii.fr/DATA_DOWNLOAD/baci/doc/baci_webpage.html
- Default vintage: **HS17** for 2017–2024 continuity

## Expected raw files

Download (202601 release, ~800 MB zip):

```bash
python -c "from diffusion_state.fetch_baci import fetch_baci_hs17; fetch_baci_hs17()"
```

URL: https://www.cepii.fr/DATA_DOWNLOAD/baci/data/BACI_HS17_V202601.zip

Extracted glob: `BACI_HS17_Y*_V*.csv` (columns `t`, `k`, `i`, `j`, `v`, `q`).

## Outputs (when raw files present)

| File | Description |
|---|---|
| `data/interim/baci_china_hs6_year.csv` | China as exporter, flow-level |
| `data/processed/export_outcomes_hs6_year.csv` | HS6-year outcomes, growth, unit values |

## Rules

- `export_value_usd = v * 1000` (BACI `v` is thousands USD).
- `unit_value` missing when `quantity <= 0`.
- Growth rates use log differences within HS6 over time.
- No winsorization in canonical file.

## Build

```bash
export BACI_DIR=/path/to/data/raw/baci   # optional
make baci
```
