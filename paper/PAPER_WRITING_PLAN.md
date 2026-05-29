# Paper writing plan — diffusion state (measurement + political economy)

**Identity:** A measurement and political-economy paper on how China converts AI capability into industrial adoption—not a patent-geography paper, causal pilot-zone paper, complete smart-factory census, or frontier-model competition paper.

**Core contrast:** Frontier capability measures who can build powerful AI. Diffusion capacity measures who can embed AI into production.

**Submission framing:** This paper introduces a measurement architecture for AI diffusion capacity. It shows that China’s industrial AI adoption is visible through the overlap between national AI pilot zones, MIIT smart-factory recognition, city-level hub structure, sectoral AI compatibility, and export-relevant manufacturing. The evidence supports a hub-centered diffusion-state interpretation while avoiding causal claims the design cannot support.

Engineers: send [ENGINEER_EVIDENCE_FREEZE_NOTE.md](../docs/ENGINEER_EVIDENCE_FREEZE_NOTE.md) in parallel. Do not wait on engineering to draft.

---

## Final structure

| # | Section |
|---|---------|
| — | **Title:** The Diffusion State: AI Pilot Zones, Smart Factories, and the Hub Architecture of China’s Industrial AI Adoption |
| — | **Abstract** — rewrite: frontier vs diffusion, dataset, main pattern, hub attenuation, limits |
| 1 | Introduction |
| 2 | Conceptual framework — diffusion state; five layers (national designation → municipal capacity → industrial ecosystems → administrative recognition → sectoral compatibility) |
| 3 | Institutional background — pilot zones + MIIT recognition; designation ≠ random treatment |
| 4 | Data and measurement — 17 zones, 509 projects, evidence classes, 70-row audit, tables |
| 5 | Descriptive overlap — puzzle (192/16 vs 317/143; 12.00 vs 2.22 means) |
| 6 | Hub architecture — attenuation (4.55 → 3.67 / 2.90 / 2.95) |
| 7 | Sectoral selectivity — ex ante industry exposure |
| 8 | Export relevance — descriptive strategic relevance only |
| 9 | Robustness — 9.1 hub/typology; 9.2 Table I appendix; 9.3 tiered patent Atlas appendix |
| 10 | What the paper does not claim |
| 11 | Conclusion — measure diffusion capacity through institutions, cities, sectors, procurement, parks, firms, standards |

---

## Writing passes

### Pass 1: Abstract and introduction — **done** (`draft_v1.md`)

### Pass 2: Conceptual framework — **done** (Section 2; Figure 1)

### Pass 3: Data and measurement — **done** (Section 4; claim-tier table)

### Pass 4: Results narrative — **done** (Sections 5–8; Figure 2–3)

### Pass 5: Robustness and limitations — **done** (Section 9; tiered patent + Table I)

### Pass 6: Full-paper polish — **done** (argument-first paragraphs; limits Section 10)

### Submission export — **done**

- `paper/draft_v1_appendix.md` (Tables I, P14/P17, audit, reproducibility)
- `make paper-draft-export` → `draft_v1_submission.md` + embedded tables/figures + validators

---

## Main text vs appendix

| Main text | Appendix |
|-----------|----------|
| Diffusion state concept | Full audit table |
| Pilot / smart-factory overlap | External verification list |
| City-resolution summary | Full city-resolution table |
| Hub-exclusion results | Table I public controls |
| City typology | P14 / P17 tiered patent geography |
| Ex ante industry exposure | Patent Atlas robustness outputs |
| Export relevance summary | Red-team memo |
| Claim limits | Claim-to-table map; reproducibility |

---

## Figures to add

**Figure 1 — Diffusion-state architecture (conceptual):**  
Frontier AI capability → national designation → municipal implementation capacity → industrial ecosystems → smart-factory recognition → sectoral and export-relevant adoption.

**Figure 2 — Hub attenuation (coefficient plot):**  
Full sample; drop Beijing/Shanghai/Shenzhen/Hangzhou; drop direct-admin municipalities; drop top five smart-factory cities.

---

## Draft file

Primary: `paper/draft_v1.md`  
Maps: `paper/claim_table_map.csv`, `paper/FINAL_ARTIFACT_INVENTORY.md`
