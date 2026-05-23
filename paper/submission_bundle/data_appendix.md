# Data appendix

All paths are relative to the repository root. Tables and figures are produced by scripts; do not hand-edit generated files.

## PCS reproduction (paper-ready build)

```powershell
make pcs
```

This runs: geo-audit, analysis, public fallback (Table I), main tables, memo sync, production-check, draft-number validation, validate-sprint, validate-audit, paper bundle, tests, and PCS status JSON.

Expected PCS outcome: `paper/pcs_gate_report.json` with `"ready": true` and `"submission_ready": true`.

## Submission package

```powershell
make submission-bundle
make validate-submission
```

Produces `paper/submission_bundle/` (draft, tables, figures, claim maps, gate report) and `paper/SUBMISSION_MANIFEST.json` with SHA256 checksums. See `paper/REPRODUCIBILITY.md` and `paper/DATA_AVAILABILITY.md`.

## Standard reproduction

```bash
make setup
make seed
make fetch
make build
make baci          # optional; ~800 MB CEPII download
make panel
make analysis
make public-fallback-controls
make main-tables
make paper
make test
```

## Core processed files (current build)

| File | Rows | Unit | Years | Script |
|------|-----:|------|-------|--------|
| `data/processed/pilot_zones.csv` | 17 | pilot unit | 2019–2021 | `scripts/00_build_seed_tables.py` |
| `data/processed/smart_factories_clean.csv` | 509 | project | 2024, 2025 | `scripts/02_parse_smart_factories.py` |
| `data/processed/analysis_city_year_panel.csv` | 1120 | city-year | 2019–2025 | `scripts/04_build_city_year_panel.py` |
| `data/processed/city_resolution_register.csv` | 509 | project | 2024–2025 | geo-audit |

## Smart-factory geography (evidence classes)

| Class | Projects |
|-------|--------:|
| `official_location_exact` | 102 |
| `rule_based_text_inference` | 357 |
| `external_evidence_verified` | 50 |

All 509 projects have a resolved city. Stratified audit: 70/70 sample decisions (`data/audit/city_resolution_sample_audit.csv`).

Manual corrections: `data/seed/smart_factory_city_overrides.csv`. Rebuild with `make geo-audit`.

## City controls

| Source | Path | Paper use |
|--------|------|-----------|
| ChinaUTC public fallback | `data/raw/city_controls/chinautc_city_controls_public_fallback.csv` | Appendix Table I only (2024; no FDI/fixed-asset) |
| EPS/NBS (preferred) | `data/raw/city_controls/` | Strict Table 5 when ingested |

## Paper tables (draft-facing)

| Table | Source output |
|-------|----------------|
| A | `table_1_dataset_summary.csv` |
| B | `table_16_geo_evidence_quality.csv` |
| C | `table_pilot_zone_overlap.csv` |
| D | `table_6_hub_exclusion_robustness.csv` |
| E | `table_14_city_diffusion_typology.csv` |
| E (ex ante) | `table_18_city_diffusion_typology_ex_ante.csv` |
| F | `table_13_city_industry_adoption_models.csv` |
| G | `table_15_export_relevance_by_sector.csv` |
| H | `table_export_sector_share_comparison.csv` |
| I (appendix) | `table_5b_public_fallback_controls.csv` |

Copied by `make main-tables` into `paper/main_tables/`.

## Export outcomes (BACI)

| File | Coverage |
|------|----------|
| `data/processed/export_outcomes_hs6_year.csv` | China exporter, HS6, 2017–2024 |
| `data/processed/export_outcomes_sector_year.csv` | Sector-year via HS bridge |

## Schema contracts

`docs/DATA_CONTRACTS.md` defines required columns and validation rules.

## Provenance

Every smart-factory row includes `source_url`, `source_file`, `parse_method`, `city_confidence`, `industry_confidence`, and `manual_override_flag`.
