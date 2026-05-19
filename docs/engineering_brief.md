# Engineering brief

## Mission

Build a reproducible empirical pipeline for an NBER-style paper on China's AI diffusion state.

## Non-negotiables

1. Every row must have a source URL or source file.
2. Raw files must be preserved exactly as acquired.
3. No hand edits directly inside processed files; use seed files or correction tables.
4. Any inferred city, sector, or HS mapping must carry a confidence flag.
5. The first paper needs credible descriptive and quasi-experimental evidence, not perfect national coverage.

## Immediate work allocation

### Engineer A — Source acquisition
Owns source registry, raw HTML/PDF downloads, attachment extraction, and reproducibility.

### Engineer B — Smart-factory parser
Owns 2024/2025 list parsing, row validation, field extraction, and project keyword classification.

### Engineer C — Trade/outcomes
Owns BACI download, China export panel, unit values, HS-sector mappings, and export-upgrading measures.

### Engineer D — City controls and econometrics
Owns EPS/NBS city controls, panel construction, baseline event studies, and output tables.

## Sprint 1 deliverable

By end of sprint, produce:

- `pilot_zones.csv`
- `smart_factories_clean.csv`
- `smart_factory_city_year.csv`
- first overlap table of pilot-zone cities and smart-factory counts
- one baseline regression table
- one diagnostic memo on data quality

## Done definition

The repo is considered MVP-complete when a fresh clone can run `make all` after raw data files are placed in `data/raw`, and reproduce the first dataset summary table.
