# Atlas IIDS tiered applicant geography

**Frozen (65.4%):** routine work is `make atlas-iids-tiered-extension` only. Manual mapping sprints are stopped — see [ATLAS_IIDS_TIERED_ROBUSTNESS_FROZEN.md](ATLAS_IIDS_TIERED_ROBUSTNESS_FROZEN.md).

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
| `ready_for_tiered_evidence_chain` | Tiered file passes **80%** coverage validation |
| `ready_for_tiered_robustness_patent_layer` | Tiered file passes **60%** threshold for appendix / robustness builds |

## Manual mapping sprint (phased — do not map 5,000 upfront)

| Phase | Action |
|-------|--------|
| A | Fill **top 100** rows in `data/seed/top_applicant_city_map.csv` |
| B | `make atlas-iids-manual-mapping-incremental` → `table_P13` |
| C | `make atlas-iids-tiered-geography-phase-c` — curated institution registry + top-500 map |
| D | `make atlas-iids-tiered-geography-phase-d` — extend map to top 2,000 + global registry merge tier |
| E | University region-anchor inference (`university_region_inference.py`) in merge |
| F | Map top **5,000** + 100k P12 region-anchor aliases |
| G | Full P12 alias registry + co-applicant scan + CAS/SOE rules (`make atlas-iids-tiered-geography-phase-g`) |
| R | **≥60%** tiered robustness patent layer (`make atlas-iids-tiered-extension` after IIDS restore) — diagnostics only |
| X | End-to-end tiered extension: streaming panel + P17 audit + atlas panel rebuild + `atlas_tiered_extension_ready` |

**Join safety:** Never run `make atlas-iids-geo` on the full IIDS file until `docs/ATLAS_IIDS_IIDS_JOIN_SAFETY.md` fix is in place and the export has ≥4M rows.

**Do not** manually map 5,000 applicants before measuring marginal return on P13.

### Top-applicant map columns

`applicant_name`, `applicant_city`, `applicant_province`, `source_url`, `geo_match_confidence`, `notes`

**Confidence labels (high-confidence only):** `official_headquarters_page`, `university_location`, `public_registry_address`. Leave blank if `ambiguous_unresolved` — do not guess.

### Mapping rules

- Universities → main campus city (`university_location`)
- Companies → registered HQ / official profile (`official_headquarters_page`)
- Registry scrape → `public_registry_address`
- Ambiguous holding groups / unclear subsidiaries → **leave blank**

## Pipeline

```powershell
make atlas-iids-applicant-concentration   # table_P12
make atlas-iids-name-geography            # *_applicant_name_inferred.csv
make atlas-iids-top-applicant-map-seed    # blank top 500 from P12
# Phase A: fill first 100 rows in top_applicant_city_map.csv
make atlas-iids-manual-mapping-incremental  # table_P13 — measure before scaling manual work
make atlas-iids-tiered-geography-merge      # streaming merge + table_P14
make atlas-iids-geo-coverage-validate
make atlas-iids-geography-preflight
make atlas-iids-tiered-extension
python scripts/50_atlas_status.py --json --tiered-extension
```

After reconstruction from P9 (abstract/IPC blank), prefer the streaming path above over `make atlas-iids-geo` on the full export.

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

**Full IIDS merge (2026-05-29, phase G):** city fill **65.4%** (`table_P14`: official HQ 43.9%, university_location 12.1%, name-token 9.3%, unresolved 34.6%). Phase G adds full P12 region-anchor registry (~329k applicants), co-applicant scan, and CAS/SOE inference rules.

| Gate | Status at 65.4% |
|------|-----------------|
| `ready_for_tiered_robustness_patent_layer` | **true** (≥60%) — run `make atlas-iids-tiered-robustness-patent-layer` |
| `tiered_geography_ready` / `ready_for_tiered_evidence_chain` | **false** (needs ≥80%) |
| `ready_for_evidence_chain` (exact) | **false** |

**Engineer A** external CNIPA/Incopat publication-number geography remains required for the **80%** publication gate without over-guessing English applicant strings.

```powershell
make atlas-iids-tiered-geography-phase-f
# or: .\scripts\run_tiered_geography_pipeline.ps1 -PhaseF
```

## Manual top-applicant map

`data/seed/top_applicant_city_map.csv` — fill city/province for high-volume applicants using official HQ pages only.

Confidence labels: `official_headquarters_page`, `university_location`, `public_registry_address`, `ambiguous_unresolved` (leave blank if ambiguous).

## Merge priority (`scripts/86_merge_tiered_patent_geography.py`)

1. External exact geography (if present later)
2. `top_applicant_city_map.csv` (top 5,000; includes anchor-seeded rows)
3. Exact alias registry (`applicant_exact_aliases.py` + generated `p12_region_anchor_aliases.json`)
4. Curated institution registry (`top_applicant_institutions.py`)
5. Corporate/grid/CAS rules (`corporate_region_inference.py`)
6. University region anchors (`university_region_inference.py` + `region_anchors.py`)
7. Name-token gazetteer (`china_city_gazetteer.py`)
8. Unresolved (blank)
