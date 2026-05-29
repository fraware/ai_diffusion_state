# Engineer E — pre-push git hygiene (repo root).
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

Write-Host "=== Engineer E: pre-push hygiene ===" -ForegroundColor Cyan
$status = git status --short
if (-not $status) {
    Write-Host "Working tree clean."
    exit 0
}

Write-Host $status
$blockedPatterns = @(
    "opendatalab_iids_industrial_ai_patents",
    "iids_filtered_patent_ids_for_geography",
    "table_P9_iids_patent_keys_for_geography",
    "cnipa_patent_geography_2015_2024",
    "iids_geo_key_batches",
    "iids_geo_exports",
    "atlas_iids_filtered_outputs.tar.gz",
    "base_patent_detail.sql"
)

$hits = @()
foreach ($line in $status) {
    foreach ($pat in $blockedPatterns) {
        if ($line -match [regex]::Escape($pat)) {
            $hits += $line
        }
    }
}

if ($hits.Count -gt 0) {
    Write-Host "`nBLOCKED: large/proprietary paths in git status:" -ForegroundColor Red
    $hits | ForEach-Object { Write-Host "  $_" }
    exit 1
}

Write-Host "`nNo blocked IIDS/geography paths in status. Safe to commit docs/scripts/gate JSON only." -ForegroundColor Green
exit 0
