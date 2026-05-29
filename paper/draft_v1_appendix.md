# Appendix — The Diffusion State (measurement robustness)

This appendix supports the main text in `paper/draft_v1.md`. It does not upgrade claim tiers in `paper/claim_table_map.csv`.

---

## Appendix A. City-resolution evidence and audit

### A.1 Evidence classes (full distribution)

All 509 MIIT excellence-level projects receive a city assignment classified as official-location exact (102), rule-based text inference (357), or external-evidence verified (50). See main Table B and `outputs/tables/table_16_geo_evidence_quality.csv`.

### A.2 Stratified audit (70 rows)

The audit samples 20 official-location rows and 50 rule-based rows. Results: 20/20 official confirmations; 20 confirmed rule-based; 30 insufficient-evidence rule-based; no incorrect rows in the audit sample. See `outputs/tables/table_17_geo_audit_error_rate.csv`. This does **not** constitute full external verification of all 509 assignments.

### A.3 External verification queue

Projects promoted to `external_evidence_verified` require non-list documentation (company site, annual report, government page, industrial park, registry). The external verification workflow is documented in `docs/GEO_WORKFLOW.md`.

---

## Appendix B. Hub-exclusion and typology (extended)

### B.1 Full hub-exclusion grid

Main text Table D reports the core exclusions. Extended specifications including Guangzhou and top-GDP-city drops appear in `outputs/tables/table_6_hub_exclusion_robustness.csv`. Top-GDP exclusions require valid GDP control sources and are labeled controls-dependent.

### B.2 Ex ante city typology

Figure 3 and Tables E / E ex ante classify cities by pilot status, direct-administrative status, and mega-hub flags **before** using smart-factory counts to define hub labels. See `outputs/tables/table_14_city_diffusion_typology.csv` and `table_18_city_diffusion_typology_ex_ante.csv`.

### B.3 Province-year descriptive check

Province-year models treat entire provinces as treated if they contain a pilot-zone city. This is a coarse overlap check only—not a causal province design. See `outputs/tables/table_19_province_year_models.csv`.

---

## Appendix C. Table I — partial public controls (not EPS-equivalent)

**Blocked:** strict EPS/NBS Table 5 (`table_5_controlled_adoption_models.csv`) because the public ChinaUTC bundle lacks FDI and fixed-asset investment.

**Table I** (`paper/main_tables/table_I_appendix_public_fallback_controls.csv`) uses a 2024 cross-section with 51 complete cities. Controls: GDP, population, secondary-industry structure, foreign trade, telecom, and industrial-output proxies [@chinautc2024].

| Specification | Pilot-zone coefficient | p-value |
|---------------|------------------------:|--------:|
| OLS count | +1.58 | 0.020 |
| OLS log-count | +0.50 | 0.018 |
| Poisson count | +0.23 | 0.43 |

Interpretation: appendix-only robustness. OLS specifications remain positive; Poisson is not significant. This is **not** evidence that EPS/NBS models pass and **not** a causal treatment effect.

---

## Appendix D. Tiered patent geography (robustness extension)

Industrial-AI patent records (4,014,104 OpenXLab IIDS keys) carry a **tiered** applicant-geography layer frozen at **65.4%** city fill. Engineering gates: `ready_for_tiered_robustness_patent_layer: true`; `ready_for_evidence_chain: false`; `exact_geography_ready: false`.

**Not claimed:** exact publication-number applicant-address geocoding; publication-ready pilot-zone × patent F1; causal patent diffusion effects.

### D.1 Tier priority stack

1. External publication-number matches (when present)  
2. Curated headquarters / university locations  
3. High-confidence applicant-name city tokens  
4. Explicit unresolved stratum  

### D.2 Coverage by tier (P14)

| Tier | Share of keys | City fill |
|------|-------------:|----------:|
| Official headquarters page | 43.9% | 100% |
| University location | 12.1% | 100% |
| Applicant name city token | 9.3% | 100% |
| Unresolved | 34.6% | 0% |

Source: `paper/appendix_tables/table_P14_tiered_geography_coverage_by_confidence.csv`.

### D.3 Audit summary (P17)

See `paper/appendix_tables/table_P17_tiered_robustness_audit.csv` and `table_P17_tiered_geography_tier_breakdown.csv`. Regenerate: `make atlas-iids-frozen-verify`.

Methods paragraph for journal paste: `paper/tiered_patent_geography_methods_snippet.md`.

---

## Appendix E. Timing and balance diagnostics

**Figure A2** plots pilot-zone coefficients by event time. Pre-2024 smart-factory counts are zero-filled because public excellence lists begin in 2024. This is a **timing diagnostic**, not pre-trend validation.

**Figure A1** reports standardized mean differences for pilot vs non-pilot cities (controls-dependent; appendix only).

---

## Appendix F. Reviewer defense and reproducibility

- Claim-to-table map: `paper/claim_table_map.csv`  
- Red-team memo: `paper/red_team_memo.md`  
- Reviewer snapshot: `paper/reviewer_results_snapshot.md`  
- Reproducibility: `paper/REPRODUCIBILITY.md`  
- One-command PCS rebuild: `make pcs`  
- Submission validation: `make validate-submission`
