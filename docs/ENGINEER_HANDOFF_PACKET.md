# Engineer handoff packet (PCS + frozen tiered patent layer)

Paper owners can proceed with writing while engineers refresh artifacts below.  
**Do not:** manual top-applicant mapping, Lens batches, weaken exact-geography gates, or force tiered fill to 80% by inference.

---

## 1. PCS / smart-factory submission package

```powershell
cd C:\Users\mateo\ai_diffusion_state
git pull origin main
make pcs-paper-owner
make validate-submission
```

**Confirm** in `paper/pcs_gate_report.json`:

- `"ready": true`
- `"submission_ready": true`

**Deliver / point paper owner to:**

| Artifact |
|----------|
| `paper/SUBMISSION_OWNER_BRIEF.md` |
| `paper/SUBMISSION_CHECKLIST.md` |
| `paper/COVER_LETTER_DRAFT.md` |
| `paper/submission_bundle.zip` (`make submission-zip` if missing) |
| `paper/submission_bundle/` |
| `paper/main_tables/` |
| `paper/results_memo.md` |
| `paper/red_team_memo.md` |
| `paper/reviewer_results_snapshot.md` |
| `paper/claim_table_map.csv` |

**Purpose:** freeze main evidence base (pilot zones + smart factories + city resolution + hub attenuation + export relevance).

---

## 2. Tiered patent robustness extension

**Fast path (~1 min with gate cache):**

```powershell
make atlas-iids-frozen-verify
python scripts/50_atlas_status.py --json --tiered-extension
```

**Full refresh** (streaming panel + atlas merge, ~45+ min):

```powershell
make atlas-iids-tiered-extension
```

**Confirm** in `paper/atlas_gate_report.json`:

| Flag | Expected |
|------|----------|
| `ready_for_evidence_chain` | **false** |
| `iids_geography_ready` | **false** |
| `exact_geography_ready` | **false** |
| `ready_for_tiered_evidence_chain` | **false** |
| `ready_for_tiered_robustness_patent_layer` | **true** |
| `atlas_tiered_extension_ready` | **true** |

**Deliver:**

| Artifact |
|----------|
| `paper/atlas_gate_report.json` |
| `outputs/tables/table_P14_tiered_geography_coverage_by_confidence.csv` |
| `outputs/tables/table_P17_tiered_geography_tier_breakdown.csv` |
| `outputs/tables/table_P17_tiered_robustness_audit.csv` |
| `data/processed/industrial_ai_patents_city_industry_year.csv` |

**Purpose:** freeze patent Atlas as **robustness only** (65.4% tiered city fill; not exact geocoding).

---

## 3. Paper claim guard

```powershell
make atlas-paper-claim-guard
```

Must **PASS** (no forbidden affirmative claims in `paper/draft_atlas_v1.md` while `ready_for_evidence_chain=false`).

Forbidden examples (non-exhaustive): publication-ready F1; exact applicant-address geocoding; pilot-zone × patent causal results; pilot zones *caused* stronger industrial AI patenting; strict EPS/NBS controls pass.

Send updated `paper/atlas_gate_report.json` with `forbidden_claim_flags` / `premature_patent_claim_flags`.

---

## 4. Final artifact inventory

Update or confirm:

`paper/FINAL_ARTIFACT_INVENTORY.md`

Lists main text, appendix, figures, robustness-only patent tables, and **blocked** items.

---

## 5. Deprecated Makefile targets

These **intentionally exit 1** with a clear message (not broken):

- `atlas-iids-manual-mapping-incremental`
- `atlas-iids-tiered-geography-phase-c` / `phase-f` / `phase-g`
- `atlas-iids-tiered-geography`

Routine command: `make atlas-iids-tiered-extension`  
80% gate: external batches — `docs/ATLAS_IIDS_EXTERNAL_GEO_DROPZONE.md`

---

## One-command verification (engineers)

```powershell
make engineer-handoff-verify
```

Writes `paper/ENGINEER_HANDOFF_CONFIRMATION.json` and prints pass/fail for sections 1–3.

---

## External geography (later — not this handoff)

When vendor CSVs arrive:

```powershell
make atlas-iids-procurement-priority-unresolved
make atlas-iids-external-geo-pipeline
make atlas-iids-control-evidence-chain
python scripts/50_atlas_status.py --json --require-evidence
```

Do not start until paper owner requests post-submission geography sprint.
