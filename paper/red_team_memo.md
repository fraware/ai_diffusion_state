# Red-team memo: identification and overclaiming risks

This memo lists threats to causal interpretation and defensible claims for the NBER draft. It is tied to the current pipeline build, not a hypothetical final sample.

## 1. Selection into pilot zones

**Issue:** The 17 national AI innovation and development pilot zones were not randomly assigned. They skew toward major municipalities and existing innovation hubs (Beijing, Shanghai, Shenzhen, Hangzhou, etc.).

**Evidence in data:** `table_2_top_smart_factory_cities.csv` shows the largest project counts in pilot-flagged cities.

**What we can say:** Pilot zones overlap with higher **listed** smart-factory recognition.

**What we cannot say:** Pilot designation caused adoption without covariate balance and design-based variation.

## 2. Pre-trends and timing

**Issue:** Smart-factory outcomes exist only for 2024 and 2025. The analysis panel zero-fills earlier years.

**Evidence:** `table_event_study_coefficients.csv` note: pre-2024 bins are zero-filled.

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

**Required robustness (not yet run):** Drop mega-cities; compare within-province non-pilot cities; use 2024 only as outcome to limit 2025 policy feedback.

## 5. City and industry mapping uncertainty

**Issue:** 316 of 509 projects lack resolved `city` (province-only `location_raw` in source HTML).

**Consequence:** City-level overlap uses 193 projects; estimates may overweight cities with parseable locations (municipalities and explicit 市 strings).

**Province overlap inflates pilot counts:** `table_pilot_zone_province_overlap.csv` assigns all projects in pilot **provinces** to the pilot-province sample, including non-pilot cities.

**Governance:** Manual fixes only via `data/seed/smart_factory_city_overrides.csv` with documented `notes`; no imputation from HQ guesses.

## 6. Post-pilot indicator with city fixed effects

**Issue:** Model 2 and 3 `post_pilot` coefficients are identified from within-city variation after `pilot_year`, but adoption lists start in 2024 while pilot years span 2019–2021. Many pre-2024 `post_pilot=1` years still have zero outcomes.

**Risk:** High R² (≈ 0.91) with city FE largely reflects cross-city levels, not dynamic treatment effects.

**What we can say:** Within-city models are consistent with higher counts in post-designation years **conditional on list availability**.

**What we cannot say:** Clean event-study dynamics without aligning outcome measurement to pre-policy baselines.

## 7. Export upgrading linkage

**Issue:** `table_4_export_upgrading_models.csv` has 9 sector-year observations; exposure is mean province smart-factory share.

**Confounds:** Sector demand shocks, HS mapping error, and simultaneity between recognition and exports.

**Current result:** Exposure coefficient insignificant (p ≈ 0.82).

**What we can say:** No robust descriptive correlation in this coarse spec.

**What we cannot say:** Diffusion state raised export quality without city-industry panel and instruments.

## 8. Missing city controls

**Issue:** `analysis_city_year_panel.csv` does not yet merge EPS/NBS controls. Omitted variables (GDP, manufacturing, patents, universities) correlate with both pilot status and adoption.

**Blocker:** `data/raw/city_controls/` empty until user supplies files (`make city-controls`).

## 9. Defensible main claims (current pipeline)

1. China’s pilot-zone map and MIIT smart-factory lists can be merged into a reproducible city-year panel with explicit coverage limits.
2. Listed adoption is **concentrated** in pilot-zone cities among resolved-city projects (mean 8.33 vs 2.83).
3. Associational models show positive `pilot_zone` and `post_pilot` terms **after** listing years exist, subject to selection and measurement caveats above.

## 10. Claims to avoid

- “Pilot zones caused a productivity shock.”
- “Pre-trends are flat.”
- “National smart-factory adoption rose X% because of AI zones.”
- “Export upgrading proves industrial upgrading” (with current Table 4).

## 11. Next empirical priorities (ordered)

1. Ingest city controls and re-estimate Models 1–3.
2. Matching / dropping mega-cities per `docs/research_design.md`.
3. Enrich city assignment via audited overrides and external registries (not bulk imputation).
4. City-industry panel linking BACI sectors to `analysis_city_industry_year_panel.csv`.
