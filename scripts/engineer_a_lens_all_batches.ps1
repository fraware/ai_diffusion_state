# Engineer A — Lens export all 17 batches (after batch 001 quality gate).
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
. (Join-Path $PSScriptRoot "load_repo_env.ps1")

if (-not $env:LENS_API_TOKEN) {
    Write-Error "LENS_API_TOKEN not set. Add it to .env or export it in this session."
}

for ($i = 1; $i -le 17; $i++) {
    $batch = "{0:D3}" -f $i
    Write-Host "=== Lens export batch $batch ===" -ForegroundColor Cyan

    $sslFlag = @()
    if ($env:LENS_INSECURE_SSL -match '^(1|true|yes)$') { $sslFlag = @("--insecure-ssl") }

    python scripts/79_lens_geography_export.py `
        --input "data/interim/iids_geo_key_batches/iids_geo_keys_batch_$batch.csv" `
        --output "data/interim/iids_geo_exports/iids_geo_export_batch_$batch.csv" `
        --chunk-size 100 `
        --sleep 1.0 `
        @sslFlag

    if ($LASTEXITCODE -ne 0) {
        Write-Error "Batch $batch failed with exit code $LASTEXITCODE"
    }
}

$count = (Get-ChildItem data\interim\iids_geo_exports\iids_geo_export_batch_*.csv).Count
Write-Host "Export batch files: $count (expected 17)"
