# Atlas IIDS geography program status

**As of:** 2026-05-28 (parallel workstreams launched)  
**Program manager checkpoint:** control laptop preflight  
**Critical path:** Engineer A external batch exports (0/17 delivered)

### Parallel launch (same day)

| Engineer | Launched | Outcome |
|----------|----------|---------|
| A | **Tiered geography pivot** (Lens not viable) | `make atlas-iids-tiered-geography`; P12 concentration; name-token ~42% city on 500k sample |
| B | Preflight + tooling | `scripts/engineer_b_pilot.ps1`, `engineer_b_full.ps1`, `make atlas-iids-geo-inspect` |
| C | Prep only | Gate tests green; chain blocked until B6 |
| D | Draft audit + fix | `paper/draft_atlas_v1.md` scrubbed of pre-geography F1 claims |
| E | Hygiene audit + script | `scripts/engineer_e_pre_push.ps1`; `.gitignore` root key file |

## Gate snapshot

| Flag | Value |
|------|-------|
| `iids_patent_export_ready` | true |
| `iids_geography_keys_ready` | true (4,014,104 keys; 17 batches) |
| `iids_geography_ready` | false |
| `ready_for_evidence_chain` | false |
| `tiered_robustness_ready` | true (65.4% city fill) |
| `ready_for_tiered_robustness_patent_layer` | true |
| `tiered_geography_ready` (80%) | false |
| `atlas_evidence_ready` | false |
| `patent_layer_ready` | false |

**Artifacts:** `outputs/tables/table_P10_iids_geography_procurement_status.json`, `paper/atlas_gate_report.json`

**Refresh:**

```powershell
make atlas-iids-geography-preflight
python scripts/50_atlas_status.py --json
```

## Workstream RACI

| Engineer | Role | Status |
|----------|------|--------|
| A | External geography export (17 batch CSVs) | **BLOCKED — not started** |
| B | Concat, normalize, coverage validate | Waiting on A (pilot after batch 001 only) |
| C | Full evidence chain | Waiting on B coverage pass |
| D | Paper claims | Procurement-safe language only |
| E | Git hygiene | Active — no large data in commits |

## Engineer A deliverables checklist

- [ ] `data/interim/iids_geo_exports/iids_geo_export_batch_001.csv` … `017.csv`
- [ ] Each file keyed to matching `iids_geo_keys_batch_NNN.csv` (250k keys × 16 + 14,104 in batch 017)
- [ ] Minimum columns: publication id + city + province + address (English or accepted Chinese headers)
- [ ] `geo_match_confidence=exact_publication_number` for publication-number lookup
- [ ] Name-only fallback labeled `applicant_registry_match` (sparse use only)

**Do not** deliver province-only exports without city — insufficient for Atlas F1 geography.

## Engineer B milestones

| Milestone | Trigger | Command |
|-----------|---------|---------|
| B1–B3 pilot | Batch 001 export exists | See [runbook](ATLAS_IIDS_GEOGRAPHY_ENGINEER_RUNBOOK.md#engineer-b--after-batch-001-pilot-only) |
| B5–B6 full | All 17 exports exist | `make atlas-iids-geo-concat` → normalize → coverage-validate |

**Expected pilot:** schema OK, high city/province fill on merged rows; `make atlas-iids-geo-coverage-validate` **fails** key-match (one batch ≪ 4M keys).

**Expected full:** city ≥ 80%, province ≥ 80%, key match ≥ 95% on full IIDS key list.

## Engineer C (after coverage pass)

```powershell
make atlas-iids-control-evidence-chain
python scripts/50_atlas_status.py --json --require-evidence
```

Target flags: `iids_geography_ready`, `ready_for_evidence_chain`, `patent_layer_ready`, `atlas_evidence_ready`, `atlas_ready`, `atlas_models_ready` all true.

## Engineer D — claim policy

**Allowed now:** Real OpenXLab IIDS-derived layer with 4,014,104 filtered CN industrial-AI patents; publication-number key list generated for geography procurement.

**Forbidden until `ready_for_evidence_chain`:** publication-ready F1, pilot-zone × AI-exposure results, “pilot zones associated with stronger industrial AI patenting,” publication-ready evidence chain, any stale coefficient (e.g. `coef=-0.0207`). Regenerate tables after chain pass: `make atlas-v02`, `make atlas-models-v02`.

## Engineer E — pre-push

```powershell
git status --short
```

Must not stage: IIDS CSV, key files, geography CSV/raw, `data/interim/iids_geo_*`, tarball, SQL dumps (see runbook).

## Next action

**Engineer A:** procure and place batch 001 export, notify Engineer B for pilot gate before producing batches 002–017.
