# Engineer B pilot (runbook B1-B3). Run from repo via: .\scripts\engineer_b_pilot.ps1
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

Write-Host "=== B1: Confirm export batch 001 exists ==="
$batch001 = "data\interim\iids_geo_exports\iids_geo_export_batch_001.csv"
if (-not (Test-Path $batch001)) {
    Write-Error "Missing $batch001 - Engineer A must deliver batch 001 first."
}
Get-ChildItem $batch001

Write-Host "=== B2: Concatenate and normalize (pilot) ==="
make atlas-iids-geo-concat
make atlas-iids-geo-normalize

Write-Host "=== B3: Inspect pilot quality ==="
python scripts/80_inspect_normalized_geography.py
