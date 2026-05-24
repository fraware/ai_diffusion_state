# Clean IIDS restart on external SSD (D: or E:). Do not use WSL home or repo C: for SQL.
param(
    [string]$TargetDir = "D:\iids_sources",
    [ValidateSet("docs", "detail", "smoke-convert", "full-convert", "status")]
    [string]$Step = "status"
)

$ErrorActionPreference = "Stop"
$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo

if (-not $env:OPENXLAB_AK -or -not $env:OPENXLAB_SK) {
    Write-Error "Set OPENXLAB_AK and OPENXLAB_SK before running IIDS production."
}

$env:OPENXLAB_IIDS_SOURCES_DIR = $TargetDir
$env:OPENXLAB_INSECURE_SSL = if ($env:OPENXLAB_INSECURE_SSL) { $env:OPENXLAB_INSECURE_SSL } else { "1" }
$env:PYTHONUTF8 = "1"

$drive = [System.IO.Path]::GetPathRoot($TargetDir)
if (-not (Test-Path $drive)) {
    Write-Error "Drive not found for $TargetDir. Attach external SSD or pass -TargetDir E:\iids_sources"
}
New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null

function Invoke-Python {
    param([string[]]$Args)
    & python @Args
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

switch ($Step) {
    "docs" {
        Write-Host "Downloading IIDS documentation only -> $TargetDir"
        Invoke-Python @("scripts/59_download_iids_patent_sources.py", "--target-dir", $TargetDir)
        Invoke-Python @("scripts/60_inspect_iids_patent_schema.py")
    }
    "detail" {
        Write-Host "Downloading base_patent_detail.sql only -> $TargetDir"
        Invoke-Python @(
            "scripts/59_download_iids_patent_sources.py",
            "--detail-only",
            "--target-dir", $TargetDir
        )
    }
    "smoke-convert" {
        $sql = Get-ChildItem $TargetDir -Recurse -Filter "base_patent_detail.sql" -File |
            Select-Object -First 1 -ExpandProperty FullName
        if (-not $sql) { Write-Error "base_patent_detail.sql not found under $TargetDir" }
        Write-Host "Smoke convert: $sql"
        Invoke-Python @(
            "scripts/61_iids_sql_to_patent_csv.py",
            "--detail-sql", $sql,
            "--max-rows", "50000",
            "--production"
        )
    }
    "full-convert" {
        $sql = Get-ChildItem $TargetDir -Recurse -Filter "base_patent_detail.sql" -File |
            Select-Object -First 1 -ExpandProperty FullName
        if (-not $sql) { Write-Error "base_patent_detail.sql not found under $TargetDir" }
        Write-Host "Full convert: $sql"
        Invoke-Python @(
            "scripts/61_iids_sql_to_patent_csv.py",
            "--detail-sql", $sql,
            "--production"
        )
        Invoke-Python @("scripts/66_export_iids_patent_keys.py", "--production")
        Invoke-Python @("scripts/58_prepare_patent_source_manifest.py")
        Invoke-Python @("scripts/68_merge_patent_manifest_draft.py")
        Write-Host "Done. Archive or delete SQL on $TargetDir, then build geography (see docs/ATLAS_IIDS_CLEAN_RESTART_RUNBOOK.md)."
    }
    default {
        Invoke-Python @("scripts/67_atlas_iids_preflight.py")
        Invoke-Python @("scripts/69_iids_production_status.py")
        Write-Host ""
        if (-not (Test-Path $drive)) {
            Write-Host "No external drive at $drive. This laptop cannot hold 136 GB SQL on C:."
            Write-Host "Use a cloud VM (300 GB disk) — see docs/ATLAS_IIDS_CLEAN_RESTART_RUNBOOK.md (Option B)."
            Write-Host ""
            Write-Host "On the VM:"
            Write-Host "  bash scripts/cloud_iids_production.sh status"
            Write-Host "  bash scripts/cloud_iids_production.sh docs"
            Write-Host "  bash scripts/cloud_iids_production.sh detail"
            Write-Host "  bash scripts/cloud_iids_production.sh smoke-convert"
            Write-Host "  bash scripts/cloud_iids_production.sh full-convert"
        } else {
            Write-Host "Next steps (external SSD at $TargetDir):"
            Write-Host "  powershell -File scripts/windows_iids_external.ps1 -TargetDir $TargetDir -Step docs"
            Write-Host "  powershell -File scripts/windows_iids_external.ps1 -TargetDir $TargetDir -Step detail"
            Write-Host "  powershell -File scripts/windows_iids_external.ps1 -TargetDir $TargetDir -Step smoke-convert"
            Write-Host "  powershell -File scripts/windows_iids_external.ps1 -TargetDir $TargetDir -Step full-convert"
        }
        Write-Host ""
        Write-Host "Runbook: docs/ATLAS_IIDS_CLEAN_RESTART_RUNBOOK.md"
    }
}
