# Data availability (PCS measurement paper)

## Public policy and list sources

- National AI innovation and development pilot zones: CSET summary and Xinhua 17-zone list (see `paper/references.bib`, `configs/sources.yml`).
- MIIT excellence-level smart-factory projects (2024 and 2025): public HTML mirrors documented in `data/raw/smart_factories/` and `configs/sources.yml`.

## Processed data in repository

After `make pcs`, the following support all main-text statistics:

- `data/processed/pilot_zones.csv`
- `data/processed/smart_factories_clean.csv`
- `data/processed/city_resolution_register.csv`
- `data/processed/analysis_city_year_panel.csv`
- `paper/main_tables/` (Tables A–I)

## Restricted or external data

- **EPS/NBS city economic controls:** not included; strict controlled adoption (Table 5) is skipped by design.
- **Appendix Table I:** partial 2024 China City Statistical Yearbook variables via ChinaUTC public fallback (`paper/main_tables/table_I_appendix_public_fallback_controls.csv`). Not equivalent to EPS/NBS.
- **BACI trade data:** optional for export-relevance descriptives; download from CEPII under their terms.

## Replication package

The directory `paper/submission_bundle/` (built by `make submission-bundle`) contains the draft, tables, figures, claim maps, and gate report for journal submission.
