# Extract cloud VM tarball into repo root and verify copy-back artifacts.
param(
    [Parameter(Mandatory = $true)]
    [string]$Archive,
    [switch]$SkipVerify
)

$ErrorActionPreference = "Stop"
$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo

if (-not (Test-Path $Archive)) {
    Write-Error "Archive not found: $Archive"
}

Write-Host "Extracting $Archive into $Repo ..."
tar -xzf $Archive -C $Repo
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not $SkipVerify) {
    python scripts/70_verify_iids_copyback.py
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    python scripts/71_geography_procurement_brief.py
}

Write-Host ""
Write-Host "Next: obtain cnipa_patent_geography_2015_2024.csv, then:"
Write-Host "  make atlas-iids-control-evidence-chain"
