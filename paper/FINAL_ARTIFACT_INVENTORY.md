# Final artifact inventory (drafting map)

**Last aligned with repo gates:** tiered patent layer frozen at **65.4%**; PCS submission package **ready**.  
**Regenerate:** `make engineer-handoff-verify` (checks only) or full tasks in `docs/ENGINEER_HANDOFF_PACKET.md`.

---

## Main text tables

| Label | Paper path | Source / build | Claim tier |
|-------|------------|----------------|------------|
| Table A | `paper/main_tables/table_A_dataset_counts.csv` | `outputs/tables/table_A_dataset_counts.csv` | measured |
| Table B | `paper/main_tables/table_B_city_resolution_quality.csv` | Roll-up of Table 16 evidence classes | validated_descriptive |
| Table C | `paper/main_tables/table_C_pilot_overlap.csv` | `outputs/tables/table_C_pilot_overlap.csv` | validated_descriptive |
| Table D | `paper/main_tables/table_D_hub_exclusion.csv` | `outputs/tables/table_D_hub_exclusion.csv` | robust_association |
| Table E | `paper/main_tables/table_E_city_typology.csv` | `outputs/tables/table_E_city_typology.csv` | validated_descriptive |
| Table E (ex ante) | `paper/main_tables/table_E_ex_ante_city_typology.csv` | `outputs/tables/table_E_ex_ante_city_typology.csv` | validated_descriptive |
| Table F | `paper/main_tables/table_F_ex_ante_industry_heterogeneity.csv` | `outputs/tables/table_F_ex_ante_industry_heterogeneity.csv` | suggestive_mechanism |
| Table G | `paper/main_tables/table_G_export_relevance.csv` | `outputs/tables/table_G_export_relevance.csv` | validated_descriptive |
| Table H | `paper/main_tables/table_H_export_sector_share_comparison.csv` | `outputs/tables/table_H_export_sector_share_comparison.csv` | validated_descriptive |

Markdown mirrors: `paper/tables_md/table_*.md`

---

## Main text figures

| Figure | Paper path | Source |
|--------|------------|--------|
| Fig 1 | `paper/figures/fig_1_timing_diagnostic_pilot_zones.png` | Timing diagnostic (not pre-trend test) |
| Fig 2 | `paper/figures/fig_2_city_typology_smart_factory_counts.png` | City typology × smart-factory counts |

---

## Appendix tables (PCS / smart-factory)

| Label | Output path | Paper role |
|-------|-------------|------------|
| Table I | `outputs/tables/table_I_public_fallback_controls.csv` → `paper/main_tables/table_I_appendix_public_fallback_controls.csv` | Partial 2024 public controls (not EPS-equivalent) |
| Table 16 | `outputs/tables/table_16_geo_evidence_quality.csv` | City-resolution evidence classes (maps to main Table B narrative) |
| Table 17 | `outputs/tables/table_17_geo_audit_error_rate.csv` | Stratified geo audit sample (70/70) |
| Fig A1 | `paper/figures/fig_A1_balance_standardized_differences.png` | Balance / standardized differences (appendix) |

---

## Robustness-only patent tables (tiered Atlas)

**Not main identification.** Use language from `paper/tiered_patent_geography_methods_snippet.md`.

| Label | Path | Notes |
|-------|------|--------|
| P14 | `outputs/tables/table_P14_tiered_geography_coverage_by_confidence.csv` | Coverage by `geo_match_confidence` tier |
| P17 tiers | `outputs/tables/table_P17_tiered_geography_tier_breakdown.csv` | P14 + overall fill rate |
| P17 audit | `outputs/tables/table_P17_tiered_robustness_audit.csv` (+ `.json`) | Extension gate summary |
| Panel | `data/processed/industrial_ai_patents_city_industry_year.csv` | Streaming city–industry–year (65% geo subset) |
| Gate | `paper/atlas_gate_report.json` | `atlas_tiered_extension_ready`; evidence chain **false** |
| Paper copies | `paper/appendix_tables/` | `make paper-tiered-appendix-sync` |

Build: `make atlas-iids-frozen-verify` or `make atlas-iids-tiered-extension`.

Paper owner entry: `paper/PAPER_OWNER_START.md`, `paper/REVIEWER_DEFENSE_OUTLINE.md`.

---

## PCS submission package (main evidence base)

| Artifact | Path |
|----------|------|
| Owner brief | `paper/SUBMISSION_OWNER_BRIEF.md` |
| Checklist | `paper/SUBMISSION_CHECKLIST.md` |
| Cover letter | `paper/COVER_LETTER_DRAFT.md` |
| Portal zip | `paper/submission_bundle.zip` (gitignored; `make submission-zip`) |
| Bundle folder | `paper/submission_bundle/` |
| Main tables | `paper/main_tables/` |
| Memos | `paper/results_memo.md`, `paper/red_team_memo.md`, `paper/reviewer_results_snapshot.md` |
| Claim map | `paper/claim_table_map.csv` |
| PCS gate | `paper/pcs_gate_report.json` — expect `ready: true`, `submission_ready: true` |

Refresh: `make pcs-paper-owner` then `make validate-submission`.

---

## Blocked / unavailable (do not draft as completed results)

| Item | Reason |
|------|--------|
| Strict EPS/NBS city Table 5 | No full 2019–2024 prefecture panel in open pipeline |
| Exact CNIPA/Incopat publication-number geography | `exact_geography_ready: false`; 0% exact tier on keys |
| Publication-ready F1 patent Atlas | `ready_for_evidence_chain: false`; `atlas_models_ready: false` |
| Pilot-zone × AI-exposure **causal** patent claims | Geography gate + claim guard block |
| `ready_for_tiered_evidence_chain` (80% tiered) | Current fill **65.4%** — need external geo (+~588k cities) |
| Main-text patent coefficients from pre-geography F1 tables | Exploratory only; do not cite |

---

## Writing sequence (paper owner — no engineer rebuild required)

1. Rebuild argument: frontier capability vs **diffusion capacity** / **AI diffusion state**.
2. Abstract + introduction (importance before tables).
3. Conceptual framework: diffusion state, hub architecture, administrative recognition, sectoral compatibility.
4. Results: overlap → hub attenuation → typology → sectoral selectivity → export relevance → robustness → limits.
5. Patent Atlas **last**, appendix-only: tiered robustness, 65.4%, P14/P17, not exact geocoding.
6. Reviewer-defense appendix (endogeneity, admin recognition, geo uncertainty, partial controls, tiered patents).

See `paper/outline.md`, `paper/red_team_memo.md`, `paper/reviewer_results_snapshot.md`.
