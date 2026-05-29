# Engineer B full chain (runbook B5-B6). Run from repo via: .\scripts\engineer_b_full.ps1
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

Write-Host "=== B5: Verify export batch count ==="
$exports = Get-ChildItem "data\interim\iids_geo_exports\iids_geo_export_batch_*.csv" -ErrorAction SilentlyContinue
$count = @($exports).Count
Write-Host "batch_export_files: $count (expected 17)"
if ($count -ne 17) {
    Write-Warning "Expected 17 batch exports; continuing validate-batches anyway."
}
make atlas-iids-geo-validate-batches

Write-Host "=== B6: Full concat / normalize / coverage ==="
Remove-Item "data\raw\patents\cnipa_patent_geography_2015_2024_raw.csv" -ErrorAction SilentlyContinue
Remove-Item "data\raw\patents\cnipa_patent_geography_2015_2024.csv" -ErrorAction SilentlyContinue
make atlas-iids-geo-concat
make atlas-iids-geo-normalize
make atlas-iids-geo-coverage-validate
make atlas-iids-geo-validate
