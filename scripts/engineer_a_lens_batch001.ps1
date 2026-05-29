# Engineer A — Lens batch 001 pilot (after smoke passes).
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
. (Join-Path $PSScriptRoot "load_repo_env.ps1")

if (-not $env:LENS_API_TOKEN) {
    Write-Error "LENS_API_TOKEN not set. Add it to .env or export it in this session."
}

$sslFlag = @()
if ($env:LENS_INSECURE_SSL -match '^(1|true|yes)$') { $sslFlag = @("--insecure-ssl") }

python scripts/79_lens_geography_export.py `
  --input data/interim/iids_geo_key_batches/iids_geo_keys_batch_001.csv `
  --output data/interim/iids_geo_exports/iids_geo_export_batch_001.csv `
  --chunk-size 100 `
  --sleep 1.0 `
  @sslFlag

python scripts/82_inspect_lens_geography_export.py --batch-001
