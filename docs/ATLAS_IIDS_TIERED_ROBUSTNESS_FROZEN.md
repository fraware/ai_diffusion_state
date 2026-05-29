# Tiered geography robustness layer (frozen)

**Status:** Frozen at **65.36%** tiered city fill on **4,014,104** IIDS keys (phase G merge, 2026-05-29).  
**Do not** resume manual top-100 / top-500 applicant mapping or phase D–G geography sprints unless driven by a **P16 unresolved-pattern table** with measured high marginal return.

## Evidence gates (exact vs tiered — not interchangeable)

| Flag | Rule |
|------|------|
| `iids_geography_ready` | **Exact only** (`exact_publication_number*` tiers, strict thresholds) |
| `exact_geography_ready` | **Exact only** |
| `ready_for_evidence_chain` | **Exact only** (same as `iids_geography_ready`) |
| `tiered_geography_ready` | Tiered confidences, **≥80%** city fill on keys |
| `ready_for_tiered_evidence_chain` | Tiered **≥80%** |
| `ready_for_tiered_robustness_patent_layer` | Tiered **≥60%** (current operational path) |

Tiered geography is **not** laundered into exact flags. Implementation: `src/diffusion_state/iids_geography_gate.py`.

## What is frozen

| Item | Policy |
|------|--------|
| `cnipa_patent_geography_2015_2024.csv` at ~65.4% | **Robustness baseline** — rebuild only after external geo import |
| `exact_geography_ready` / `iids_geography_ready` | **Strict** until external CNIPA/Incopat batches |
| `ready_for_evidence_chain` / 80% gate | **Do not weaken** |
| In-repo manual mapping / phase D–G Makefile sprints | **Deprecated** — fail with pointer to this doc |
| Patent Atlas in paper | **Tiered robustness extension only** — not exact geocoding |

## Routine commands (engineers)

**Fast verify** (P14/P17 + claim guard; no 4M panel rebuild):

```powershell
make atlas-iids-frozen-verify
```

**Full refresh** (streaming panel + atlas merge):

```powershell
make atlas-iids-tiered-extension
```

Paper methods text: `paper/tiered_patent_geography_methods_snippet.md`

**Do not run** (deprecated, exit 1):

- `make atlas-iids-manual-mapping-incremental`
- `make atlas-iids-tiered-geography-phase-c` / `phase-d` / `phase-f` / `phase-g`
- `make atlas-iids-tiered-geography`

## Outputs (tiered extension)

- `outputs/tables/table_P14_tiered_geography_coverage_by_confidence.csv`
- `outputs/tables/table_P17_tiered_geography_tier_breakdown.csv`
- `outputs/tables/table_P17_tiered_robustness_audit.csv` (+ `.json`)
- `data/processed/industrial_ai_patents_city_industry_year.csv`
- `paper/atlas_gate_report.json` (`atlas_tiered_extension_ready`)

## Paper language

**Allowed (robustness / appendix):** tiered applicant-geography layer; ~65% city coverage on 4,014,104 keys; institutional/corated/name-token tiers; results as **tiered robustness extension**, not exact geocoded evidence.

**Forbidden while `ready_for_evidence_chain=false`:**

- Publication-ready F1 or pilot-zone × patent causal claims as core findings
- Exact publication-number applicant-address geocoding of the full corpus
- “Exact evidence chain passes”

## External geography (80% gate)

Target **+751k** keyed cities (~**80%** of 4,014,104).

**Procurement pack (vendor handoff):**

```powershell
make atlas-iids-procurement-pack
make atlas-iids-procurement-priority-unresolved
```

- Status: `outputs/tables/table_P18_procurement_pack_status.json`
- Vendor CSV: `data/interim/iids_geo_procurement_priority_unresolved.csv` (~750k–900k rows, gitignored)
- Drop zone: `docs/ATLAS_IIDS_EXTERNAL_GEO_DROPZONE.md`

Gate scans are cached at `outputs/tables/table_P11_iids_geography_gate_snapshot.json` (invalidate with `ATLAS_IIDS_GATE_NO_CACHE=1`).

**After batches land:**

```powershell
make atlas-iids-external-geo-prepare
make atlas-iids-external-geo-pipeline
make atlas-iids-geo-coverage-validate
make atlas-iids-control-evidence-chain
python scripts/50_atlas_status.py --json --require-evidence
```

See `docs/ATLAS_IIDS_GEO_VENDOR_HANDOFF.md`.
