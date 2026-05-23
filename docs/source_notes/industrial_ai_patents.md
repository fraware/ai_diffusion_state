# Industrial AI patents (Workstream A)

## Purpose

Long-run city-industry-year counts of applied industrial AI patenting for the China AI Diffusion Atlas. This layer supports pre/post pilot-zone variation and `PostPilot × AIExposure` models before procurement scraping is complete.

## Outputs

| File | Description |
|------|-------------|
| `data/interim/industrial_ai_patents_long.csv` | Patent-level classified records |
| `data/processed/industrial_ai_patents_city_industry_year.csv` | Main panel (high/medium industry mapping, non-empty city) |
| `outputs/tables/table_A1_patent_taxonomy_counts.csv` | Taxonomy counts from microdata |
| `outputs/tables/table_A2_city_industry_patent_coverage.csv` | Coverage diagnostics |
| `outputs/tables/table_A1_patent_taxonomy_counts_cset_validation.csv` | CSET China validation (optional) |

## Taxonomy

Fourteen binary industrial AI categories are defined in `configs/patent_taxonomy.yml` (machine vision, robotics, predictive maintenance, digital twin, quality inspection, industrial scheduling, process control, smart logistics, industrial software, industrial foundation model, semiconductor/battery/chemical process AI).

Patents must match at least one category keyword in title/abstract/claims (or mapped CSET fields for validation rows only). Surveillance/governance keywords are excluded from the industrial diffusion measure.

## Industry mapping

`data/seed/industry_crosswalk_atlas.csv` maps IPC prefixes and Chinese keywords to Atlas industries. Low-confidence mappings are retained in the long file but excluded from the main panel.

## Identification boundaries

Allowed:

- Industrial AI patenting provides a long-run applied-innovation layer for the Atlas.

Forbidden:

- Higher patent counts prove higher AI quality.
- CSET-only province/country aggregates as city-industry causal evidence.

## Commands

```bash
make patents
```

Validation exit code `2` means CNIPA microdata is missing; exit code `1` means microdata exists but minimum coverage thresholds are not met.
