# Model interpretation matrix

**Paper frame:** Hub-centered diffusion architecture; **not** uniform pilot-zone treatment, productivity causality, or export effects.

**Last rebuilt:** Run `make analysis` after Engineer A (controls) and Engineer B (geo) updates.

| Table | What variation identifies the coefficient | Supports (claim tier) | Cannot support |
|-------|----------------------------------------|------------------------|----------------|
| **Table 3** — baseline adoption | Cross-city differences in 2024–2025 listed project counts; `pilot_zone` = city ever in national AI pilot list | Positive **association** between pilot status and listed adoption (descriptive / associational) | Causal effect of pilot designation; uniform treatment across treated cities |
| **Table 3** — Model 2–3 (`post_pilot` + city FE) | Within-city years after `pilot_year` vs before, holding city fixed | Post-designation years coincide with higher counts **given list availability from 2024** | Clean event-study dynamics; pre-2024 zeros are mechanical |
| **Table 5** — controlled adoption | Same as Table 3 plus city-year covariates (GDP, population, industry structure, FDI, etc.) | Whether pilot association **survives** observable city economic differences | Causal identification without design-based variation; claims if controls are stub/missing |
| **Table 6** — hub exclusion | `pilot_zone` coef under sample restrictions (drop mega-hubs, direct-admin, top adopters) | **Attenuation** of association outside hubs — hub-centered architecture | That association is zero nationally; average treatment effect |
| **Table 7** — balance | Pre-treatment (2018) covariate means: pilot vs non-pilot cities; matched subsample | Whether treated/control cities are **comparable** on observables before lists exist | Randomization; causal balance without controls data |
| **Table 8** — matched adoption | Matched pilot/control cities on pre-treatment covariates; adoption 2024–2025 | **Robustness** of associational pattern in matched sample | Full causal interpretation; valid if matching fails or controls missing |
| **Table 13** — city-industry | `pilot_zone` × ex ante AI exposure (`industry_ai_exposure_ex_ante.csv`) with city + industry + year FE | **Heterogeneity** — higher-exposure industries more concentrated in pilot cities | Causal mechanism; tag-derived specs (labeled descriptive only) |
| **Table 14** — city typology | Descriptive counts by diffusion type (hub, pilot hub, non-pilot, etc.) | **Architecture** — adoption clusters by institutional/industrial hub type | Binary pilot flag as sufficient summary |
| **Table 18** — ex ante typology | Capacity typology without top smart-factory city labels; uses real GDP ranks only if production controls merged | Ex ante **capacity** framing for heterogeneity | Outcome-driven labels; stub-driven GDP ranks |
| **Table 19** — province-year | Province-year FE; “pilot province” if any pilot city in province | **Coarse** check using all projects | Pilot-city effect (non-pilot cities inside pilot provinces) |
| **Table 15 / G** — export relevance | Sector shares: listed projects vs export basket | **Descriptive** strategic overlap with advanced exports | Export causality or upgrading effects |
| **Table 4 / 12** | Export growth on sector outcomes | — | **Do not use** in main text (underpowered, non-causal) |
| **Timing diagnostic** | Event-time bins around pilot year with zero-filled pre-2024 outcomes | Timing **diagnostic** only | Pre-trend validation |

## Table 5–8 gate (Engineer A)

Until `make production-check` passes with `City controls: production`:

- Table 5 must show `model_4_controlled_count` with numeric `pilot_zone` — not `skipped`.
- Table 7 must show covariate rows — not a single `skipped` row.
- Table 8 must show matched pilot **and** control cities with `matched_city_ratio` metadata.

## Geo gate (Engineer B)

Until `make validate-audit` and Table 16 show `external_evidence_verified >= 50`:

- Do not claim externally audited geocoding.
- Use rule-based / official-location language from Table 16.

## Drafting rule

Use only `paper/main_tables/` (Tables A–H) for numbers in the draft. Run `make sync-paper-stats` after every `make analysis`.
