# The Diffusion State: AI Pilot Zones, Smart Factories, and the Hub Architecture of China’s Industrial AI Adoption

**Target:** NBER Economics of AI conference (papers due 4 June 2026).

**Empirical status:** Measurement and disciplined descriptive / associational evidence. **No causal claims** until city controls are ingested. Main empirical story: **hub-centered diffusion architecture**, not uniform pilot-zone treatment.

---

## 1. Motivation

China’s AI policy stack combines national pilot-zone designation, smart-manufacturing recognition, and export-oriented industry. The paper asks whether this bundle constitutes a distinctive **diffusion state**—institutional capacity to move AI from rhetoric into **listed** industrial adoption—concentrated in high-capacity hubs rather than evenly across treated cities.

## 2. Contribution

1. **Reproducible measurement** of national AI pilot zones (17 units, 2019–2021) linked to MIIT excellence-level smart-factory lists (509 projects, 2024–2025).
2. **Transparent geo and industry coding** with confidence flags; ex ante industry AI exposure separate from outcome-built tags.
3. **Hub-architecture evidence:** pilot-zone overlap exists, but robustness shows adoption is driven by municipalities and manufacturing hubs (`table_6`, `table_14`).
4. **Red-team discipline** on identification limits (`paper/red_team_memo.md`).

## 3. Empirical chain

```text
AI pilot zones → listed smart-factory recognition → hub-typed diffusion geography → (descriptive) export-relevant sectors
```

**Built in repo:** pilot zones, smart factories, city-year panels, hub exclusions, typology, city-industry heterogeneity (ex ante), export relevance table.

**Blocked:** EPS/NBS city controls (`make city-controls`).

## 4. Section outline

### 4.1 Introduction

- Frame diffusion state vs frontier AI.
- Lead with hub concentration finding; pilot zones as marker of architecture, not average treatment.

### 4.2 Institutional background

- National AI innovation pilot zones (2019–2021).
- MIIT excellence-level smart-factory lists (2024–2025).

### 4.3 Data and measurement

- **509/509** projects assigned to cities; evidence split in Table 16 (102 official, 407 rule-based; external verification in progress).
- Ex ante industry exposure (`docs/source_notes/industry_ai_exposure.md`).

### 4.4 Descriptive results

- Tables 1–2, pilot overlap (city and province).
- **Table 14 / Figure:** city diffusion typology (central table).

### 4.5 Associational models and robustness

- Table 3: baseline adoption (interpret with Table 6).
- **Table 6:** hub-exclusion robustness (main robustness table).
- Tables 5, 7–8 after city controls.

### 4.6 City-industry heterogeneity (exploratory)

- Table 13 with ex ante exposure.

### 4.7 Export strategic relevance (descriptive)

- Table 15; not causal export effects.

### 4.8 Limitations and red team

- `paper/red_team_memo.md`.

### 4.9 Conclusion

- Diffusion state as **spatially concentrated hub architecture**—policy designation overlaps capacity, but listed adoption is not uniformly distributed across treated cities.

## 5. Artifact index

`paper/artifact_manifest.json`, `paper/claim_table_map.csv`, `paper/reviewer_results_snapshot.md`.
