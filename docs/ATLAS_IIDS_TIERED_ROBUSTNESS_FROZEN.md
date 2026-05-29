# Tiered geography robustness layer (frozen)

**Status:** Frozen at **65.36%** tiered city fill on **4,014,104** IIDS keys (phase G merge, 2026-05-29).  
**Do not** resume manual top-100 / top-500 applicant mapping or phase D–G geography sprints unless driven by a **P16 unresolved-pattern table** with measured high marginal return.

## What is frozen

| Item | Policy |
|------|--------|
| `cnipa_patent_geography_2015_2024.csv` at ~65.4% | **Robustness baseline** — rebuild only after external geo import or explicit merge rule change |
| `exact_geography_ready` / `iids_geography_ready` | **Strict** — exact publication-number geography only; stays false until external batches |
| `ready_for_evidence_chain` / 80% gate | **Do not weaken** |
| In-repo English-name / manual map sprints | **Stopped** — marginal return too low vs procurement |
| Patent Atlas in paper | **Tiered robustness extension only** — not exact geocoding |

## Reproducible diagnostics (control laptop)

```powershell
make atlas-iids-tiered-extension
```

Writes / refreshes:

- `outputs/tables/table_P14_tiered_geography_coverage_by_confidence.csv`
- `outputs/tables/table_P17_tiered_geography_tier_breakdown.csv`
- `outputs/tables/table_P17_tiered_robustness_audit.csv` (+ `.json`)
- `data/processed/industrial_ai_patents_city_industry_year.csv` (streaming)
- `paper/atlas_gate_report.json` with `atlas_tiered_extension_ready`

Exit **0** with `--tiered-extension`; publication F1 remains blocked.

## Paper claim guards

While `ready_for_evidence_chain=false`:

- Do **not** use publication-ready F1 language.
- Do **not** claim pilot-zone × patent causal results.
- Do **not** call the layer exact geocoding.

Run: `make atlas-paper-claim-guard`

## Next move: external geography (80% gate)

Target: **+751k** additional keyed cities (~**80%** of 4,014,104).

1. Engineer A: place CNIPA/Incopat batch CSVs under `data/interim/iids_geo_exports/` (see `docs/ATLAS_IIDS_GEO_VENDOR_HANDOFF.md`).
2. `make atlas-iids-external-geo-prepare` — verify drop zone and batch checklist.
3. `make atlas-iids-external-geo-pipeline` — validate, concat, normalize, coverage.
4. `make atlas-iids-control-evidence-chain`
5. `python scripts/50_atlas_status.py --json --require-evidence`

Deprecated Makefile targets (manual mapping): `atlas-iids-manual-mapping-*`, `atlas-iids-tiered-geography-phase-d` through `phase-g` for routine use.
