# The Diffusion State: AI Pilot Zones, Smart Factories, and the Hub Architecture of China’s Industrial AI Adoption

**Draft v1**  
**Status:** Passes 1–6 draft (abstract through conclusion). Grounded in `paper/main_tables/`, `paper/claim_table_map.csv`, `paper/results_memo.md`, `paper/red_team_memo.md`. Figures: `paper/figure_manifest.json`.  
**Core thesis:** China’s AI diffusion state is visible as a hub-centered industrial adoption architecture. Pilot-zone designation marks part of this architecture, but the evidence does not establish a uniform average treatment effect across treated cities.

## Abstract

**Frontier capability** asks who can build the most powerful AI—models, compute, labs, and private investment. **Diffusion capacity** asks who can embed AI into production. Those are different economic objects. This paper introduces a measurement architecture for China’s industrial **diffusion capacity** and documents how adoption appears in institutions, cities, sectors, and export-relevant manufacturing—not in frontier-model leaderboards alone.

The empirical setting links 17 National New Generation AI Innovation and Development Pilot Zone units with 509 Ministry of Industry and Information Technology excellence-level smart-factory projects (2024–2025 lists). Every project is assigned to a city under an evidence-classified procedure: 102 official-location exact rows, 357 rule-based text inferences, and 50 external-evidence verified rows, with a 70-row stratified audit (20/20 official confirmations; 20 confirmed and 30 insufficient-evidence rule-based rows). Listed recognition is concentrated in pilot-zone and high-capacity hub cities: 192 projects across 16 pilot-zone cities (mean 12.00 per city) versus 317 projects across 143 non-pilot cities (mean 2.22 per city).

The central pattern is **hub attenuation**, not a flat pilot-zone treatment. The baseline pilot-zone association is 4.55 (p < 0.001) but falls to 3.67 when Beijing, Shanghai, Shenzhen, and Hangzhou are excluded, to 2.90 when direct-admin municipalities are excluded, and to 2.95 when the top five smart-factory cities are excluded—remaining positive yet materially weaker. That supports a hub-centered **diffusion-state** interpretation: national designation operates through municipal implementation capacity and industrial ecosystems. The paper does not claim that pilot zones caused adoption or estimate an average treatment effect. Appendix robustness includes partial ChinaUTC public controls (51 cities; OLS count and log-count significant, Poisson not) and a frozen tiered patent-geography layer (~65% city fill) that is explicitly not exact publication-number geocoding. Strict EPS/NBS production controls remain blocked.

## 1. Introduction

The global debate over artificial intelligence is organized around **frontier capability**: which economy trains the strongest models, secures the most advanced chips, and attracts the largest private AI investment. That debate matters. It is also incomplete. AI becomes economically consequential when it **diffuses** into production systems—plants, logistics, quality control, scheduling, engineering workflows, and industrial coordination. The model frontier can advance quickly while the adoption frontier moves slowly. An economy can trail on headline model benchmarks yet still compete through the institutions that convert capability into recognized industrial practice.

This paper studies that second frontier in China. It is a **measurement and political-economy** study of how AI capability is converted into industrial adoption—not a patent-geography paper, a causal pilot-zone evaluation, a census of all smart factories, or a frontier-model competition account. The object of analysis is the **diffusion state**: the institutional architecture that moves a general-purpose technology from strategic priority into factories, sectors, and export-relevant supply chains.

China offers a disciplined empirical window because two public layers can be linked reproducibly. National **AI pilot zones** (17 designated city or county-level units, 2019–2021) mark places selected for AI development and application capacity—they are institutional markers, not randomly assigned treatments. **MIIT excellence-level smart-factory lists** (509 projects on the 2024 and 2025 registers) mark administrative recognition of advanced manufacturing adoption, not the full universe of Chinese smart factories. Linking the two layers reveals where adoption is visible in policy space: pilot-zone cities hold 192 listed projects across 16 cities (mean 12.00 per city) versus 317 projects across 143 non-pilot cities (mean 2.22 per city). The baseline city-year association is 4.55 (p < 0.001).

The paper’s interpretive contribution is that overlap alone is misleading without **hub architecture**. Excluding Beijing, Shanghai, Shenzhen, and Hangzhou lowers the coefficient to 3.67; excluding direct-admin municipalities to 2.90; excluding the top five smart-factory cities to 2.95. Associations stay positive but attenuate sharply—consistent with diffusion through municipal scale, administrative status, and industrial ecosystems rather than a uniform pilot shock. Sectoral ex ante exposure and export-relevant descriptives show where AI is complementary to production; they do not claim productivity or export causal effects.

### Contribution

This paper contributes an operational **measurement architecture for AI diffusion capacity**: reproducible linkage of pilot zones, smart-factory recognition, evidence-classified city resolution, hub-exclusion diagnostics, ex ante industry heterogeneity, and export-relevant sector tables—mapped to claim tiers and frozen engineering gates. Conceptually, it separates frontier capability from diffusion capacity and shows that China’s visible industrial AI adoption is **hub-centered**. Empirically, it documents concentration and attenuation patterns the design can support while blocking causal, productivity, and strict controlled claims the design cannot.

### Roadmap

Section 2 develops the diffusion-state concept and five-layer framework (national designation through sectoral compatibility). Section 3 describes institutional background. Section 4 presents data and measurement, including evidence classes and the stratified audit. Sections 5–8 present overlap, hub attenuation, sectoral selectivity, and export relevance. Section 9 reports appendix robustness—public ChinaUTC controls and tiered patent geography—without elevating blocked EPS/NBS or exact-geocoding claims. Sections 10–11 state limits and conclude on measuring diffusion capacity through cities, sectors, institutions, and standards—not frontier models alone.

## 2. Conceptual framework: the diffusion state

**Diffusion capacity** is the ability to embed general-purpose AI into production—not the ability to train the largest model. The **diffusion state** is the institutional architecture that performs that embedding: it links frontier capability to factories, sectors, and tradable industry through stacked policy and administrative layers. This paper measures one observable slice of that architecture in China; it does not reduce the diffusion state to patent counts, model benchmarks, or a single policy treatment.

The framework organizes adoption into **five layers**, each necessary but insufficient on its own (Figure 1):

1. **National designation** — strategic selection of places for AI development and application (here: 17 AI pilot-zone units, 2019–2021).
2. **Municipal implementation capacity** — local government scale, administrative status, and ability to run industrial programs.
3. **Industrial ecosystems** — depth of manufacturing clusters, engineering labor, parks, and automation complements.
4. **Administrative recognition** — public registers that certify exemplar adoption (here: MIIT excellence-level smart-factory lists, 509 projects in 2024–2025).
5. **Sectoral compatibility** — technological fit between AI tools and production processes (machine vision, predictive maintenance, digital twins, robotics, semiconductors, batteries, automotive, chemicals, pharmaceuticals, and related process industries).

Frontier capability enters at the top of the stack; export-relevant manufacturing sits at the bottom. Pilot zones mark layer 1; smart-factory lists mark layer 4. **Hub architecture** is how layers 2–3 concentrate adoption in a subset of cities—so overlap between layers 1 and 4 is expected but not interpretable as a uniform treatment effect.

### Why China

China combines a visible national AI program, city-level designation, and a recent administrative recognition register dense enough to link in a reproducible pipeline. That makes it a disciplined case for **measurement and political economy**: where adoption is visible in policy space, how it clusters, and what a hub-centered architecture implies for interpreting designation. The design generalizes as a template—designation, recognition, evidence-classified geography, hub diagnostics, sectoral exposure—even when other countries lack identical institutions.

### Contribution to policy debate

Industrial and technology policy often tracks frontier capability; this paper argues that **diffusion capacity** deserves parallel measurement: institutions, cities, sectors, procurement, parks, firms, and standards that convert models into production. For AI geopolitics, the relevant question is not only who leads on benchmarks but who can operationalize capability in manufacturing systems at scale.

### Related literature

The framework connects to general-purpose-technology implementation lags [@brynjolfsson2021productivity; @bloom2020diffusion], task-based automation in production [@acemoglu2014robots; @ifr2023worldrobotics], spatially concentrated Chinese industrial upgrading [@autor2013china], and frontier-centric AI rankings that understate adoption infrastructure [@masi2024aiindex]. The empirical contribution is **measurement architecture**, not closure of any causal literature.

## 3. Institutional background

National AI pilot zones designate cities and localities as environments for AI development and application. Designation is **not random**: authorities select units with prior research capacity, industrial depth, platform firms, or strategic relevance. Pilot zones are therefore **institutional markers** of the diffusion state’s first layer—not instruments for a clean average treatment effect.

MIIT excellence-level smart-factory lists identify projects that exemplify advanced smart-manufacturing adoption on public 2024 and 2025 registers. The lists measure **official recognition**, not the full stock of Chinese smart factories. That boundary is analytically productive: recognition is part of the diffusion system—standards, showcases, and links between firm-level adoption and industrial policy.

The paper asks whether layers 1 and 4 overlap in geography and whether that overlap is better read as a flat pilot shock or as **hub-mediated diffusion**. The evidence supports the second reading.

## 4. Data and measurement

The pipeline links pilot zones, smart-factory projects, evidence-classified city resolution, sectoral exposure, and export-relevant descriptives. Every claim maps to a reproducible artifact via `paper/claim_table_map.csv`.

### Claim-tier hierarchy

| Tier | Role in this paper |
|------|-------------------|
| Measured | Parsed pilot zones and smart-factory registers |
| Validated descriptive | Overlap, typology, export relevance, geo evidence classes |
| Baseline association | Pilot-zone coefficient in city-year models (uncontrolled) |
| Robust association | Hub exclusions; ex ante typology |
| Suggestive mechanism | Ex ante industry AI exposure |
| Partial public controls | Table I appendix only; not EPS-equivalent |
| Blocked | Strict EPS/NBS Table 5 (missing FDI, fixed-asset investment in public bundle) |
| Not supported | Causal ATE of pilot zones; productivity or export effects |

### Core counts

- **17** AI pilot-zone units (2019–2021) [@cset2020pilotzones; @xinhua2021seventeenzones].
- **509** MIIT excellence-level projects (235 from 2024 list, 274 from 2025) [@miit2024smartfactory; @miit2025smartfactory].
- **Outcome unit:** listed recognition, not total smart-factory activity.

### City-resolution evidence classes

All 509 projects receive a city assignment classified as:

| Class | Count | Role |
|-------|------:|------|
| Official-location exact | 102 | List or repost states project city |
| Rule-based text inference | 357 | Parsed from text when address incomplete |
| External-evidence verified | 50 | Confirmed via company site, annual report, government page, park, or registry |

A **70-row stratified audit** (20 official, 50 rule-based) finds 20/20 official confirmations, 20 confirmed rule-based rows, 30 insufficient-evidence rule-based rows, and no incorrect rows in the audit sample. Rule-based rows are reported with weaker status; the full register is not externally audited.

### Panels and limitations

The adoption panel covers **160 cities** and **320 city-years**; pre-2024 smart-factory counts are zero-filled because public excellence lists begin in 2024—event-time plots are **timing diagnostics only**, not pre-trend tests (Appendix Figure A2). Industry heterogeneity uses **ex ante** AI-exposure categories, not tags derived from project text, so the outcome does not define exposure. Export tables are **strategic relevance** descriptives, not export-effect estimates.

## 5. Descriptive overlap

The empirical puzzle is **concentration**: listed recognition is not spread evenly across China’s city system.

Among resolved cities, pilot-zone cities hold **192** projects across **16** cities (mean **12.00** per city). Non-pilot cities hold **317** projects across **143** cities (mean **2.22** per city)—a gap of **9.78** projects per city. Top cities illustrate hub concentration within the overlap: Shanghai (30, pilot), Chongqing (22, pilot), Beijing (19, pilot), Tianjin (17, pilot), Qingdao (14, non-pilot).

The baseline city-year association is **4.55** (p < 0.001; Table C). That coefficient is an association in the constructed adoption universe, not a causal effect of designation. It establishes that layers 1 and 4 align in policy space. It does not yet identify **how** that alignment is structured—flat pilot contrast or hub architecture.

## 6. Hub architecture and attenuation

**Hub attenuation** is the paper’s central empirical result (Figure 2; Table D). The question is how the pilot-zone coefficient moves when high-capacity cities are removed.

| Exclusion rule | Coefficient | Share of full sample |
|--------------|------------:|---------------------:|
| Full sample | 4.55 | 100% |
| Drop Beijing, Shanghai, Shenzhen, Hangzhou | 3.67 | 81% |
| Drop direct-admin municipalities | 2.90 | 64% |
| Drop top five smart-factory cities | 2.95 | 65% |

Coefficients stay positive and significant, but **attenuation is large**. A flat pilot-zone story predicts similar associations across treated cities; a pure mega-city story predicts collapse once hubs exit. The data sit between: pilot status matters descriptively, yet a substantial share of the baseline association runs through municipal scale, direct-administrative status, and industrial hubs.

Ex ante city typologies (Tables E, E ex ante; Figure 3) reinforce this: adoption clusters in frontier municipality hubs, pilot industrial hubs, and non-pilot industrial hubs—not in a simple pilot/non-pilot split. Typology labels use pre-existing attributes (pilot status, direct-admin status, mega-hub flags), not outcomes from the smart-factory counts themselves.

**Interpretation:** China’s visible industrial AI adoption is a **hub-and-spoke diffusion state**. National designation is meaningful because it operates where implementation capacity and ecosystems already exist.

## 7. Sectoral selectivity

Diffusion is **sectorally selective** because AI complements some production processes more than others. Ex ante industry exposure (Table F) tests whether listed projects concentrate in sectors with high technological compatibility—machine vision, quality inspection, predictive maintenance, digital twins, scheduling, robotics, logistics, semiconductors, batteries, automotive, machinery, chemicals, pharmaceuticals, and related process industries.

Preferred specifications use ex ante classifications; description-based tags are descriptive only. Results are **suggestive mechanism** evidence: they explain why hub cities host recognizable adoption but do not identify causal sectoral treatment effects. Diffusion capacity is industrial, not merely geographic.

## 8. Export relevance

Export tables (Tables G, H) ask whether recognized sectors overlap China’s **advanced manufacturing export basket**—strategic relevance, not export causation. Global demand, trade policy, exchange rates, and firm competitiveness also shape exports; this design does not isolate effects of MIIT recognition on export growth.

The descriptive finding still matters politically: if recognition clusters in electronics, batteries, machinery, automotive, steel, chemicals, pharmaceuticals, shipbuilding, and AI servers, the diffusion state connects to **tradable industrial capacity**. Industrial AI adoption is therefore a competitiveness question, not only a domestic modernization story.

## 9. Robustness and extensions

### 9.1 Hub exclusions and typology

Section 6 reports the main hub-attenuation and typology evidence. Province-year checks and balance diagnostics in the appendix remain **descriptive or controls-dependent**; they do not upgrade the causal tier.

### 9.2 Public ChinaUTC controls (appendix only)

Strict **EPS/NBS Table 5** models remain **blocked**—the public ChinaUTC bundle lacks FDI and fixed-asset investment required for the intended production-control design.

**Table I** reports a partial 2024 cross-section (51 complete cities) with GDP, population, secondary-industry structure, foreign trade, telecom, and industrial-output proxies [@chinautc2024]. Pilot-zone status stays positive in **OLS count** (+1.58, p = 0.020) and **OLS log-count** (+0.50, p = 0.018) specifications; **Poisson** (+0.23, p = 0.43) is not significant. Language must stay narrow: appendix robustness only—not EPS-equivalent, not a causal treatment effect, not a main-text controlled result.

### 9.3 Tiered patent Atlas (appendix only)

As a **robustness extension**, the repository links an industrial-AI patent corpus (4,014,104 OpenXLab IIDS keys) to a **tiered** applicant-geography layer frozen at **65.4%** city fill. Exact publication-number applicant-address geocoding is **not** available (`exact_geography_ready: false`; `ready_for_evidence_chain: false`). Locations follow a fixed priority stack: headquarters-page matches (~44% of keys), university locations (~12%), applicant-name city tokens (~9%), and an explicit unresolved stratum (~35%). **Publication-ready patent F1** and pilot-zone × patent causal claims remain blocked.

Appendix Tables P14 and P17 report coverage by confidence tier and audit summary (`paper/appendix_tables/`). Patent geography supports **robustness diagnostics only**—not main identification and not exact geocoding. Methods language follows `paper/tiered_patent_geography_methods_snippet.md`.

## 10. What the paper does not claim

The paper does **not** claim that:

- pilot zones **caused** smart-factory adoption or an average treatment effect across treated cities;
- AI diffusion **caused** productivity growth;
- MIIT recognition **caused** export upgrading;
- excellence-level lists are a **complete census** of Chinese smart factories;
- rule-based city assignment is **full external verification**;
- partial ChinaUTC controls **replace** blocked EPS/NBS specifications;
- tiered patent geography is **exact address geocoding** or evidence-chain-ready identification.

These limits define the contribution: a credible **measurement architecture** for diffusion capacity under transparent claim tiers.

## 11. Conclusion

Frontier capability and diffusion capacity are different economic objects. China’s industrial AI strategy is visible in the **overlap** between national pilot designation and MIIT smart-factory recognition, but the deeper pattern is **hub architecture**: associations attenuate when Beijing, Shanghai, Shenzhen, Hangzhou, direct-admin municipalities, and top adoption cities are excluded. Sectoral and export-relevant descriptives show where AI fits production; they do not substitute for causal designs the data cannot support.

The policy implication is to **measure diffusion capacity**—institutions, cities, sectors, procurement systems, industrial parks, firms, and standards—not frontier models alone. The next wave of AI’s economic impact may depend less on which economy trains the single best model and more on which economy embeds capability into the industrial base fastest. That is the diffusion state this paper makes measurable.

## Figures

| Figure | File | Role |
|--------|------|------|
| 1 | `fig_1_diffusion_state_architecture.png` | Five-layer conceptual framework |
| 2 | `fig_2_hub_attenuation_pilot_coefficients.png` | Hub-exclusion coefficient plot (main result) |
| 3 | `fig_3_city_typology_smart_factory_counts.png` | Ex ante city typology |
| A2 | `fig_A2_timing_diagnostic_pilot_zones.png` | Timing diagnostic (appendix) |

## Tables to use in this draft

- `paper/main_tables/table_A_dataset_counts.csv`
- `paper/main_tables/table_B_city_resolution_quality.csv`
- `paper/main_tables/table_C_pilot_overlap.csv`
- `paper/main_tables/table_D_hub_exclusion.csv`
- `paper/main_tables/table_E_city_typology.csv`
- `paper/main_tables/table_E_ex_ante_city_typology.csv`
- `paper/main_tables/table_F_ex_ante_industry_heterogeneity.csv`
- `paper/main_tables/table_G_export_relevance.csv`
- `paper/main_tables/table_H_export_sector_share_comparison.csv`
- `paper/main_tables/table_I_appendix_public_fallback_controls.csv`

## Engineering status (PCS submission package)

Completed in repository:

- BibTeX: `paper/references.bib` (keys mapped in `paper/citation_map.csv`)
- Figures: `make paper-figures` → `paper/figures/` + `paper/figure_manifest.json`
- Tables: `make paper-tables` → `paper/tables_md/` + embedded in `paper/draft_v1_submission.md`
- Submission draft export: `make export-submission` → `paper/draft_v1_submission.md`, `paper/draft_v1.tex` (scaffold)
- Validation: `make validate-submission` (PCS gates + figures + draft numbers + language gates)

## Paper owner (remaining)

1. Paste journal-specific author/affiliation block and abstract word limits.
2. Convert `paper/draft_v1_submission.md` to target LaTeX/Word template (or compile `paper/draft_v1.tex` after Pandoc import).
3. Insert numbered tables from `paper/main_tables/` at submission positions.
4. Keep strict Table 5 out of main text unless real EPS/NBS controls are added.
5. Final proofread: claim tiers in `paper/claim_table_map.csv`; Table I remains appendix-only.
