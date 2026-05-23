# Atlas model interpretation matrix (Phase 1)

## Models

| Table | Question | Dependent variable | Key term | Fixed effects |
|-------|----------|-------------------|----------|---------------|
| F1 | Post-pilot × AI exposure → patents? | `industrial_ai_patents` | `post_pilot × ai_exposure_ex_ante` | City×industry, province×year, industry×year |
| F2 | Robot complementarity? | `industrial_ai_patents` | `post_pilot × ai_exposure × robot_compatibility` | Same as F1 |
| F3 | Post-pilot × exposure → smart factories? | `smart_factory_count` | `post_pilot × ai_exposure_ex_ante` | City×industry, industry×year |
| F4 | Event study (patents) | `industrial_ai_patents` | `1[years_since_pilot=k] × ai_exposure` | Same as F1; k=-1 omitted |

## Claim tier

All Phase 1 tables: **associational_exploratory**. Standard errors clustered at city.

## Supported (if coefficients positive and stable)

- Pilot-zone designation correlates with stronger industrial AI patenting in higher ex-ante AI-exposure industries.
- Effect may be stronger where robot compatibility is higher (F2).

## Not supported (do not claim from Phase 1)

- Causal productivity growth from pilot zones.
- Export upgrading or procurement-driven commercial AI output.
- Economy-wide productivity shock.

## Null result protocol

If F1/F2 are null: report honestly that smart-factory recognition remains spatially concentrated while the patent layer does not show a strong post-pilot response in AI-exposed industries.

## Run

```bash
make atlas-models-v02
```
