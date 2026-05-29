# Full tiered geography validation pipeline (post manual-map update).
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

$Extend = $args -contains "-ExtendMap"
$PhaseF = $args -contains "-PhaseF"
$PhaseG = $args -contains "-PhaseG"
if ($PhaseG) {
    Write-Host "=== Phase G: full P12 alias registry + merge ===" -ForegroundColor Cyan
    python scripts/97_build_p12_region_anchor_alias_registry.py --top-n 0
} elseif ($PhaseF) {
    Write-Host "=== Phase F: top-5k map + P12 alias registry ===" -ForegroundColor Cyan
    python scripts/94_extend_top_applicant_city_map.py --top-n 5000
    python scripts/93_apply_curated_top_applicant_mappings.py --scope map
    python scripts/96_seed_map_from_region_anchors.py
    python scripts/97_build_p12_region_anchor_alias_registry.py --top-n 100000
} elseif ($Extend) {
    Write-Host "=== Extend top applicant map (P12 top 2000) ===" -ForegroundColor Cyan
    python scripts/94_extend_top_applicant_city_map.py --top-n 2000
    Write-Host "=== Apply curated registry to map ===" -ForegroundColor Cyan
    python scripts/93_apply_curated_top_applicant_mappings.py --scope map
}

Write-Host "=== P13 incremental manual mapping ===" -ForegroundColor Cyan
python scripts/90_measure_manual_mapping_incremental_coverage.py

Write-Host "=== Tiered merge + P14 ===" -ForegroundColor Cyan
python scripts/86_merge_tiered_patent_geography.py

Write-Host "=== Coverage validate ===" -ForegroundColor Cyan
make atlas-iids-geo-coverage-validate

Write-Host "=== Preflight + Atlas status ===" -ForegroundColor Cyan
make atlas-iids-geography-preflight
python scripts/50_atlas_status.py --json

Write-Host "`nReview:"
Write-Host "  outputs/tables/table_P13_manual_mapping_incremental_coverage.csv"
Write-Host "  outputs/tables/table_P14_tiered_geography_coverage_by_confidence.csv"
Write-Host "  outputs/tables/table_P10_iids_geography_procurement_status.json"
