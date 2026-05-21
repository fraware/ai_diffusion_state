# Industry AI exposure (ex ante classification)

## Purpose

`data/seed/industry_ai_exposure_ex_ante.csv` classifies smart-factory **industry buckets** by technological compatibility with industrial AI **before** using smart-factory list outcomes. This file is **not** derived from `smart_factories_clean.csv`, tag frequencies, or adoption counts.

The tag-derived file `data/processed/industry_ai_exposure.csv` remains for **descriptive** exploration only.

## Scale

All exposure dimensions use:

- `0` = low
- `1` = medium
- `2` = high

Columns: `ai_exposure_ex_ante`, `robot_complementarity_ex_ante`, `process_control_exposure`, `machine_vision_exposure`, `digital_twin_exposure`.

## High-exposure industries (ai_exposure_ex_ante = 2)

| industry_label | Rationale |
|----------------|-----------|
| semiconductors | Fab automation, inline inspection, yield optimization |
| electronics | Assembly automation, AOI, SMT process control |
| ai_servers | Compute-intensive production; supply-chain digitalization |
| batteries | Process control critical for NEV supply chains |
| automotive | Robotics-heavy assembly; vision QC |
| general_equipment | Industrial machinery; CNC and robotics integration |
| special_equipment | Custom equipment; robotics and process automation |
| electrical_machinery | Motor/transformer production automation |
| metals | Steel/metals process optimization |
| railway_shipbuilding_aerospace | Large discrete manufacturing; digital twin in aerospace |
| pharma | GMP process control; packaging vision |
| chemicals | Process industries; DCS and advanced control |

## Medium and low exposure

- **instruments** (medium): measurement equipment with moderate automation potential.
- **non_metallic_minerals**, **mining** (medium on process control; lower robotics).
- **food**, **textiles**, **paper**, **furniture_wood** (low): labor-intensive or limited industrial-AI relevance in listed projects.

## Sources (classification_source column)

Classifications synthesize public sector guidance (MIIT smart manufacturing), industry 4.0 adoption literature, and OECD-style AI exposure mappings. They are **judgment-based** and should be updated if the paper adopts a published crosswalk.

## Build

```bash
python -c "from diffusion_state.build_industry_ai_exposure_ex_ante import build_industry_ai_exposure_ex_ante; build_industry_ai_exposure_ex_ante()"
```

Processed output: `data/processed/industry_ai_exposure_ex_ante.csv`.

## Models

`table_13_city_industry_adoption_models.csv` uses `ai_exposure_ex_ante` / `high_exposure_ex_ante` as the preferred heterogeneity spec. Tag-derived exposure specs are labeled `descriptive_tag_derived` in the `note` column.
