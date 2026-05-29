# Tiered patent geography — methods snippet (robustness extension)

Use when `ready_for_evidence_chain=false` and `atlas_tiered_extension_ready=true`. Do not edit into main text without removing exact-geocoding implications.

## Suggested paragraph

As a robustness extension, we construct a tiered applicant-geography layer for the industrial-AI patent records in the OpenXLab IIDS-derived corpus. Because exact publication-number applicant-address geography was unavailable at the time of analysis, we assign locations using a fixed priority stack: external publication-number matches (when present), manually curated headquarters and university locations for high-volume applicants, high-confidence applicant-name city tokens, and an explicit unresolved stratum. On 4,014,104 patent keys, this layer achieves 65.4% city coverage; we report all patent-location results as a tiered robustness extension rather than as exact address geocoding. Coverage by confidence tier is reported in Appendix Table P14.

## Do not use

- Exact publication-number applicant-address geocoding (full corpus).
- Publication-ready pilot-zone × AI-exposure patent estimates as the core finding.
- Claims that the exact evidence chain (`ready_for_evidence_chain`) has passed.

## Tables

- `outputs/tables/table_P14_tiered_geography_coverage_by_confidence.csv`
- `outputs/tables/table_P17_tiered_geography_tier_breakdown.csv`
- `outputs/tables/table_P17_tiered_robustness_audit.csv`

Regenerate: `make atlas-iids-frozen-verify` or full `make atlas-iids-tiered-extension`.
