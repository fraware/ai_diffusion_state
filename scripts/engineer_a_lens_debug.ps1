# Engineer A — Lens raw JSON diagnostic (Steps 1–2).
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
. (Join-Path $PSScriptRoot "load_repo_env.ps1")

if (-not $env:LENS_API_TOKEN) {
    Write-Error "LENS_API_TOKEN not set. Add it to .env."
}

$sslFlag = @()
if ($env:LENS_INSECURE_SSL -match '^(1|true|yes)$') { $sslFlag = @("--insecure-ssl") }

New-Item -ItemType Directory -Force -Path outputs\debug | Out-Null

Write-Host "=== Step 1: default biblio include ===" -ForegroundColor Cyan
python scripts/83_debug_lens_raw_response.py `
  --input data/interim/iids_geo_key_batches/iids_geo_keys_smoke_025.csv `
  --output-jsonl outputs/debug/lens_smoke_025_raw.jsonl `
  --output-audit outputs/debug/lens_smoke_025_party_field_audit.csv `
  --query-mode default `
  @sslFlag

python scripts/84_inspect_lens_party_audit.py `
  --path outputs/debug/lens_smoke_025_party_field_audit.csv

Write-Host "=== Step 2a: extended projection include (may 400 on this API plan) ===" -ForegroundColor Cyan
try {
  python scripts/83_debug_lens_raw_response.py `
    --input data/interim/iids_geo_key_batches/iids_geo_keys_smoke_025.csv `
    --output-jsonl outputs/debug/lens_smoke_025_raw_projection.jsonl `
    --output-audit outputs/debug/lens_smoke_025_party_field_audit_projection.csv `
    --query-mode extended `
    @sslFlag
  python scripts/84_inspect_lens_party_audit.py `
    --path outputs/debug/lens_smoke_025_party_field_audit_projection.csv
} catch {
  Write-Warning "Extended projection failed (expected if Lens rejects flat applicant.* fields)."
}

Write-Host "=== Step 2b: full record (no include filter) ===" -ForegroundColor Cyan
python scripts/83_debug_lens_raw_response.py `
  --input data/interim/iids_geo_key_batches/iids_geo_keys_smoke_025.csv `
  --output-jsonl outputs/debug/lens_smoke_025_raw_full.jsonl `
  --output-audit outputs/debug/lens_smoke_025_party_field_audit_full.csv `
  --query-mode full `
  @sslFlag

python scripts/84_inspect_lens_party_audit.py `
  --path outputs/debug/lens_smoke_025_party_field_audit_full.csv
