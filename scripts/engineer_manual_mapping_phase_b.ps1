# Phase B — measure incremental gain before scaling manual mapping.
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

Write-Host "=== Phase B: incremental manual mapping coverage (P13) ===" -ForegroundColor Cyan
python scripts/90_measure_manual_mapping_incremental_coverage.py

Write-Host "`nReview outputs/tables/table_P13_manual_mapping_incremental_coverage.csv"
Write-Host "Only proceed to top 500 if manual_patents_incremental is meaningful."
