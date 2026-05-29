# Atlas IIDS tiered applicant geography

Lens Patent API does not return CN applicant addresses on our plan. We build a **tiered, high-confidence** geography layer instead of fabricating exact address matches.

## Paper framing (required)

> We construct a tiered applicant-geography layer. Exact external publication-number geography was unavailable at the time of analysis, so the patent geography layer uses high-confidence applicant-name city tokens and curated mappings for high-volume applicants. We report coverage by tier and treat the patent Atlas as a robustness extension, not as the sole identification layer.

Do **not** describe this as exact publication-number applicant-address geocoding.

## Gate flags

| Flag | Meaning |
|------|---------|
| `exact_geography_ready` | ≥80% city/province/key-match on keys, mostly `exact_publication_number*` confidence |
| `tiered_geography_ready` | Same coverage thresholds, allows `applicant_name_city_token` + curated top-applicant tiers |
| `iids_geography_ready` | **Exact only** (unchanged strict flag) |
| `ready_for_tiered_evidence_chain` | Tiered file passes coverage validation |

## Pipeline

```powershell
make atlas-iids-applicant-concentration   # table_P12
make atlas-iids-name-geography            # *_applicant_name_inferred.csv
make atlas-iids-name-geography-coverage   # fill report
# Manual: fill data/seed/top_applicant_city_map.csv (top 500+)
make atlas-iids-top-applicant-map-seed    # blank template from P12
make atlas-iids-tiered-geography-merge    # cnipa_patent_geography_2015_2024.csv
make atlas-iids-geo-coverage-validate
```

## Applicant concentration (2026-05-29)

On 4,014,104 IIDS rows (`table_P12`):

| Top N applicants | Cumulative patent share |
|------------------|------------------------|
| 100 | 14.9% |
| 500 | 28.4% |
| 1,000 | 34.4% |
| 5,000 | 48.4% |

Curating the top 500–5,000 applicants is a realistic manual sprint to raise coverage beyond name-token matching.

## Name-token tier rules

Implemented in `src/diffusion_state/china_city_gazetteer.py`:

- Match explicit city/municipality tokens in `applicant_name` only
- Chinese (`深圳`, `北京市`) and English (`SHENZHEN`, `HANGZHOU`) tokens
- No title, inventor, or fuzzy guessing
- `geo_match_confidence = applicant_name_city_token`

500k-row sample city fill: **~42%** (pilot; full-file run via `make atlas-iids-name-geography`).

## Manual top-applicant map

`data/seed/top_applicant_city_map.csv` — fill city/province for high-volume applicants using official HQ pages only.

Confidence labels: `official_headquarters_page`, `university_location`, `public_registry_address`, `ambiguous_unresolved` (leave blank if ambiguous).

## Merge priority (`scripts/86_merge_tiered_patent_geography.py`)

1. External exact geography (if present later)
2. `top_applicant_city_map.csv`
3. Name-token inferred file
4. Unresolved (blank)
