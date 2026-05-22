# Red-team memo: identification and overclaiming risks

This memo lists threats to causal interpretation and defensible claims for the NBER draft. It is tied to the current pipeline build, not a hypothetical final sample.

## 1. Selection into pilot zones

**Issue:** The 17 national AI innovation and development pilot zones were not randomly assigned. They skew toward major municipalities and existing innovation hubs (Beijing, Shanghai, Shenzhen, Hangzhou, etc.).

**Evidence in data:** `table_2_top_smart_factory_cities.csv` shows the largest project counts in pilot-flagged cities.

**What we can say:** Pilot zones overlap with higher **listed** smart-factory recognition.

**What we cannot say:** Pilot designation caused adoption without covariate balance and design-based variation.

## 2. Pre-trends and timing

**Issue:** Smart-factory outcomes exist only for 2024 and 2025. The analysis panel zero-fills earlier years.

**Evidence:** `table_timing_diagnostic_coefficients.csv` note: pre-2024 bins are zero-filled.

**What we can say:** Post-2024 bins describe recognition after lists existed.

**What we cannot say:** Parallel pre-trends in adoption before designation; event-study pre coefficients are mechanical zeros, not validation.

## 3. Survivorship and list construction

**Issue:** MIIT excellence lists measure **official recognition** of nominated projects, not the stock of all smart manufacturing or AI investment.

**Bias directions:**

- Firms that already invested in visibility may be more likely to appear.
- Batch timing (2024 vs 2025) may reflect policy cycles, not steady adoption.

**Mitigation in writing:** Refer to “listed excellence-level projects,” not “total smart factories.”

## 4. Smart-factory recognition bias

**Issue:** Selection into the public list may correlate with firm size, state ownership, prior subsidies, and documentation capacity.

**Empirical symptom:** Heavy tails (Shanghai 30 projects) drive means; Model 3 uses `log1p` but does not remove composition bias.

**Required robustness (now run):** Hub-exclusion table (`table_6_hub_exclusion_robustness.csv`); city typology (`table_14_city_diffusion_typology.csv`). Controlled specs and matching require city controls.

## 5. City and industry mapping uncertainty

**Issue:** Current build resolves **509/509** projects to a city using official location, rule-based list-text inference, or plant-city registry (Table 16). **Zero** rows are `external_evidence_verified` until non-list URLs are added to the registry.

**Consequence:** City-level models use the full list; province-only robustness (Table 19) remains a coarser check. Do not describe registry matches as externally audited without a real `evidence_url`.

**Province overlap inflates pilot counts:** `table_pilot_zone_province_overlap.csv` assigns all projects in pilot **provinces** to the pilot-province sample, including non-pilot cities.

**Governance:** City assignments use the **city-resolution register** (`data/seed/smart_factory_city_overrides.csv`) with documented `evidence_url`, `evidence_type`, `resolution_class`, and `notes`. Do not call these “externally verified” unless a non-list `external_evidence_url` is supplied.

## 6. Post-pilot indicator with city fixed effects

**Issue:** Model 2 and 3 `post_pilot` coefficients are identified from within-city variation after `pilot_year`, but adoption lists start in 2024 while pilot years span 2019–2021. Many pre-2024 `post_pilot=1` years still have zero outcomes.

**Risk:** High R² (≈ 0.91) with city FE largely reflects cross-city levels, not dynamic treatment effects.

**What we can say:** Within-city models are consistent with higher counts in post-designation years **conditional on list availability**.

**What we cannot say:** Clean event-study dynamics without aligning outcome measurement to pre-policy baselines.

## 7. Export upgrading linkage

**Issue:** Causal export-growth regressions are underpowered and confounded.

**Current approach:** Descriptive export relevance (`table_15_export_relevance_by_sector.csv`) and sector descriptives—not effect claims.

**What we can say:** Listed smart-factory recognition overlaps sectors in China’s advanced manufacturing export basket.

**What we cannot say:** Diffusion state raised export quality from this coarse panel alone.

## 8. Missing city controls

**Issue:** `analysis_city_year_panel.csv` does not yet merge EPS/NBS controls. Omitted variables (GDP, manufacturing, patents, universities) correlate with both pilot status and adoption.

**Blocker:** `data/raw/city_controls/` empty until user supplies files (`make city-controls`).

## Hub-selection robustness now run

<!-- PCS:RED_TEAM_HUB -->
The hub-exclusion table (analysis universe: **160** cities, **507** listed projects in 2024–2025) shows that the baseline pilot-zone coefficient **weakens outside mega-hubs** and **falls substantially when direct-admin municipalities are excluded** (coef ≈ 2.90 vs. 4.55 full sample; top-five smart-factory cities ≈ 2.95). The association does not go to zero with full city coverage, but hub concentration remains visible in typology and descriptive overlap. Evidence is consistent with **hub-centered diffusion capacity** rather than uniform treatment across treated cities.
<!-- /PCS:RED_TEAM_HUB -->

Table 6 now includes `interpretation`, `coefficient_relative_to_full_sample`, and `projects_remaining_share` so readers can read the conclusion from the table. Controlled hub exclusions run automatically after `make city-controls`.

## 9. Industry exposure (ex ante vs tag-derived)

**Issue:** Tag-derived `industry_ai_exposure.csv` is built from smart-factory outcomes and must not enter causal heterogeneity claims.

**Mitigation:** `industry_ai_exposure_ex_ante.csv` is manually classified (`docs/source_notes/industry_ai_exposure.md`). Table 13 labels tag-derived specs as `descriptive_tag_derived`.

## 10. Defensible main claims (current pipeline)

1. China’s pilot-zone map and MIIT smart-factory lists merge into a reproducible city-year panel with explicit coverage limits.
<!-- PCS:PILOT_MEAN_CLAIM -->
2. Listed adoption is **concentrated** in pilot-zone cities among resolved-city projects (mean **12.00** vs **2.22**).
<!-- /PCS:PILOT_MEAN_CLAIM -->
3. The descriptive pilot-zone association is **substantially mediated by major hub cities** and direct-admin municipalities.
4. China’s AI diffusion state is visible as a **hub-and-spoke architecture** (typology table), not uniform treatment across treated cities.

## 11. Claims to avoid

- “Pilot zones caused a productivity shock.”
- “Pre-trends are flat.”
- “National smart-factory adoption rose X% because of AI zones.”
- “Export upgrading proves industrial upgrading” (with causal export regressions).
- **“Pilot-zone designation has an average effect across treated cities.”**

## 12. Next empirical priorities (ordered)

1. Ingest city controls and re-estimate Models 4–7, balance, matching, and controlled hub exclusions.
<!-- PCS:RED_TEAM_GEO -->
2. City resolution uses **three evidence classes** (Table 16): **102** official-location exact, **357** rule-based, **50** external-evidence verified (non-list URLs). Stratified audit sample complete (Table 17). Do not claim full external audit of all 509 assignments; use class-specific language.
<!-- /PCS:RED_TEAM_GEO -->
3. City-industry heterogeneity using ex ante exposure only in main text.
4. Keep export section descriptive (Table 15).
