# Data appendix

All paths are relative to the repository root. Tables and figures are produced by scripts; do not hand-edit generated files.

## Reproduction

```bash
make setup
make seed
make fetch
make build
make baci          # optional; ~800 MB CEPII download
make panel
make analysis
make paper
make test
```

City controls (when EPS/NBS exports are available):

```bash
# Place files under data/raw/city_controls/ per docs/source_notes/city_controls.md
make city-controls
make panel
make analysis
```

## Core processed files

| File | Rows (current build) | Unit | Years | Script |
|------|---------------------:|------|-------|--------|
| `data/processed/pilot_zones.csv` | 17 | pilot unit | 2019–2021 | `scripts/00_build_seed_tables.py` |
| `data/processed/smart_factories_clean.csv` | 509 | project | 2024, 2025 | `scripts/02_parse_smart_factories.py` |
| `data/processed/smart_factory_city_year.csv` | 60 | city-year | 2024–2025 | `src/diffusion_state/build_smart_factories.py` |
| `data/processed/smart_factory_province_year.csv` | 59 | province-year | 2024–2025 | same |
| `data/processed/analysis_city_year_panel.csv` | 280 | city-year | 2019–2025 | `scripts/04_build_city_year_panel.py` |

## Smart-factory geography

| `city_confidence` | Projects |
|-------------------|--------:|
| exact | (see `table_9_city_resolution_audit.csv`) |
| high | (see audit table) |
| unknown | **6** (post geo-audit v2) |

City-level tables and overlap statistics use only rows with resolved `city` (**503** projects, **158** cities in overlap table). Adoption models use the wider **125**-city analysis universe (pilot cities plus smart-factory cities). Province-only locations in MIIT HTML (e.g. `江苏省`) or national firm names without plant city remain `city=unknown` until audited overrides are added.

Manual city assignment: add audited rows to `data/seed/smart_factory_city_overrides.csv` (header-only by default). Rebuild with `make build`.

## Raw sources (not committed)

| Source | Path | Notes |
|--------|------|-------|
| 2024 list mirror | `data/raw/smart_factories/2024_mirror.html` | Solarbe mirror; `make fetch` |
| 2025 list | `data/raw/smart_factories/2025_jlts.html` | JLT table; `make fetch` |
| BACI HS17 | `data/raw/baci/BACI_HS17_V202601.zip` | CEPII 202601; `make baci` |
| City controls | `data/raw/city_controls/` | User-supplied EPS/NBS |

## Export outcomes (BACI)

| File | Rows | Coverage |
|------|-----:|----------|
| `data/processed/export_outcomes_hs6_year.csv` | 42,650 | China exporter, HS6, 2017–2024 |
| `data/processed/export_outcomes_sector_year.csv` | (sector-year) | Mapped via `configs/hs_smart_factory_bridge.yml` |
| `data/processed/hs_to_smart_factory_sector_bridge.csv` | bridge | Documented HS2/HS4 → industry |

## Paper tables and figures

| Output | Description |
|--------|-------------|
| `outputs/tables/table_1_dataset_summary.csv` | Observation counts |
| `outputs/tables/table_2_top_smart_factory_cities.csv` | Top cities by project count |
| `outputs/tables/table_pilot_zone_overlap.csv` | Pilot vs non-pilot (resolved cities) |
| `outputs/tables/table_pilot_zone_province_overlap.csv` | Province-level counts (all projects) |
| `outputs/tables/table_3_pilot_zone_adoption_models.csv` | OLS adoption specs |
| `outputs/tables/table_event_study_coefficients.csv` | Event-study coefficients |
| `outputs/figures/fig_event_study_pilot_zones.png` | Event-study plot |
| `outputs/tables/table_4_export_upgrading_models.csv` | Sector export growth (if BACI built) |

## Schema contracts

`docs/DATA_CONTRACTS.md` defines required columns and validation rules.

## Provenance fields

Every smart-factory row includes `source_url`, `source_file`, `parse_method`, `city_confidence`, `industry_confidence`, and `manual_override_flag`.
