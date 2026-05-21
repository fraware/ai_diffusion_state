# Export relevance memo (descriptive only)

**Status:** Built from `outputs/tables/table_15_export_relevance_by_sector.csv` and `paper/main_tables/table_G_export_relevance.csv`.

## What this analysis is

This section measures **strategic overlap** between:

1. Sectors where China lists excellence-level smart-factory projects (2024–2025 MIIT lists), and  
2. Sectors in China’s advanced manufacturing export basket (BACI-based sector groups, 2017–2024).

It is a **descriptive alignment** exercise. It does **not** estimate whether pilot zones, smart-factory recognition, or AI policy **caused** export growth, export upgrading, or productivity change.

## What we can say

- Listed smart-factory activity is concentrated in sector groups that also account for a large share of China’s export basket (see `share_of_smart_factory_projects` vs `share_of_china_exports_2024` in Table G).
- `share_gap_sf_minus_export` highlights sectors where listed projects are more (or less) prominent relative to the export basket.
- Cumulative log export growth 2017–2024 (`log_export_growth_2017_2024`) is reported for context only; it is not a treatment outcome in this paper.

## What we cannot say

- Pilot-zone designation raised export quality or export growth.
- Smart-factory lists caused sectoral export upgrading.
- Any causal effect from industrial AI adoption on foreign trade performance.

Legacy Tables 4 and 12 (export-upgrading regressions) remain **underpowered and non-causal**; do not use them in the main text.

## Paper sentence (template)

> Listed smart-factory recognition overlaps strategically with sectors central to China’s advanced manufacturing exports, but this overlap is descriptive and does not identify causal effects of pilot zones or smart-factory policy on export outcomes.

## Rebuild

```powershell
make analysis
make main-tables
```
