# Industry ex ante AI exposure and robot compatibility (Atlas Phase 1)

## Purpose

These layers supply **ex ante** interaction variables for pilot-zone × industry designs. They must not be calibrated on smart-factory counts or other Atlas outcomes.

## Files

| File | Role |
|------|------|
| `data/seed/industry_ai_exposure_ex_ante_v2_seed.csv` | Curated dimension scores (0/1/2) |
| `data/seed/industry_robot_compatibility_seed.csv` | Robot compatibility (0/1/2) |
| `data/processed/industry_ai_exposure_ex_ante_v2.csv` | Built exposure panel |
| `data/processed/industry_robot_compatibility.csv` | Built robot panel |
| `outputs/tables/table_C1_industry_exposure_scores.csv` | Review table |

## Exposure dimensions

`machine_vision_exposure`, `robotics_exposure`, `predictive_maintenance_exposure`, `digital_twin_exposure`, `process_control_exposure`, `quality_inspection_exposure`, `smart_logistics_exposure`, `industrial_software_exposure`.

Composite: `ai_exposure_ex_ante` = row mean of non-missing dimensions.

## Evidence standard

Scores use engineering judgment, IFR/OECD/MIIT sector reviews, and process-automation literature. Reasons must not reference observed smart-factory counts in this repository.

## Build

```bash
make atlas-exposure
```
