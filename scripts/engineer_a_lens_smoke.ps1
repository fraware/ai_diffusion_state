# Engineer A — Lens 25-ID smoke test (Step 5–6 gate before batch 001).
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
. (Join-Path $PSScriptRoot "load_repo_env.ps1")

if (-not $env:LENS_API_TOKEN) {
    Write-Error "LENS_API_TOKEN not set. Add it to .env or export it in this session."
}

python scripts/create_lens_smoke_keys.py
$sslFlag = @()
if ($env:LENS_INSECURE_SSL -match '^(1|true|yes)$') { $sslFlag = @("--insecure-ssl") }

python scripts/79_lens_geography_export.py `
  --input data/interim/iids_geo_key_batches/iids_geo_keys_smoke_025.csv `
  --output data/interim/iids_geo_exports/iids_geo_export_smoke_025.csv `
  --chunk-size 10 `
  --sleep 1.0 `
  @sslFlag

python scripts/82_inspect_lens_geography_export.py --smoke
