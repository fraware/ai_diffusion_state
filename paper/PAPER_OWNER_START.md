# Paper owner — start here

You can write **now**. Engineers send a one-time [evidence-freeze note](../docs/ENGINEER_EVIDENCE_FREEZE_NOTE.md) in parallel—do not wait on it to begin drafting.

**Writing plan:** [PAPER_WRITING_PLAN.md](PAPER_WRITING_PLAN.md)  
**Draft status:** Passes 1–6 in `draft_v1.md`; appendix in `draft_v1_appendix.md`.

**Export submission package:** `make paper-draft-export` → `draft_v1_submission.md` + embedded tables/figures + validation.

Engineering gates are green for the **main PCS package** and the **frozen tiered patent robustness** layer (~65.4% tiered city fill; appendix only).

## Evidence hierarchy

1. **Main text:** pilot zones + smart factories + city resolution + hub attenuation + export relevance (`paper/main_tables/`, Figs 1–2).
2. **Appendix robustness:** partial public controls (Table I); tiered patent geography (P14/P17) only as extension.
3. **Blocked:** strict EPS/NBS Table 5; exact CNIPA geocoding; publication-ready patent F1.

## Key files

| Role | Path |
|------|------|
| Drafting map | `paper/FINAL_ARTIFACT_INVENTORY.md` |
| PCS submission | `paper/SUBMISSION_OWNER_BRIEF.md`, `paper/submission_bundle.zip` |
| Results | `paper/results_memo.md`, `paper/reviewer_results_snapshot.md` |
| Red team | `paper/red_team_memo.md` |
| Claim map | `paper/claim_table_map.csv` |
| Patent methods (appendix) | `paper/tiered_patent_geography_methods_snippet.md` |
| Patent tables | `paper/appendix_tables/` |
| Reviewer defense | `paper/REVIEWER_DEFENSE_OUTLINE.md` |

## Writing sequence (recommended)

1. Frame: frontier capability vs **diffusion capacity** / **AI diffusion state**.
2. Abstract + introduction — lead with importance before tables.
3. Conceptual framework: diffusion state, hub architecture, administrative recognition, sectoral compatibility.
4. Results: overlap → hub exclusion → typology → sectoral selectivity → export → robustness → limits.
5. Patent Atlas **last** (appendix; tiered language only).
6. Reviewer-defense appendix.

## Gates (do not overclaim)

- `paper/pcs_gate_report.json`: `submission_ready: true`
- `paper/atlas_gate_report.json`: `atlas_tiered_extension_ready: true`, `ready_for_evidence_chain: false`

Refresh engineering status: `make paper-owner-handoff` (full) or `make engineer-handoff-verify` (checks only)
