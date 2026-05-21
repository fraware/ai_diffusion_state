# Full PCS credibility sprint pipeline (Windows).
# Usage: .\scripts\run_pcs_pipeline.ps1 [-UseStubControls]
param(
    [switch]$UseStubControls
)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

Write-Host "==> build + geo-audit"
py -3 scripts\11_build_registry_supplement.py
py -3 scripts\10_build_audited_city_overrides.py
if ($LASTEXITCODE -ne 0) { Write-Warning "Geo-audit targets not met; continuing." }

Write-Host "==> panel"
py -3 scripts\04_build_city_year_panel.py

if ($UseStubControls) {
    Write-Host "==> city-controls-stub (CI only)"
    py -3 scripts\06b_install_city_controls_stub.py
    py -3 scripts\04_build_city_year_panel.py
} elseif (Test-Path "data\raw\city_controls\*.csv") {
    Write-Host "==> city-controls (production)"
    py -3 scripts\06_build_city_controls.py
    py -3 scripts\04_build_city_year_panel.py
} else {
    Write-Host "SKIP city-controls (no raw EPS/NBS files)"
}

Write-Host "==> analysis"
py -3 scripts\05_run_baseline_models.py

Write-Host "==> validate"
py -3 scripts\13_validate_geo_evidence.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
py -3 scripts\08_validate_sprint_outputs.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "==> main paper tables"
py -3 scripts\12_build_main_paper_tables.py

Write-Host "==> tests"
py -3 -m pytest -q

Write-Host "==> PCS status"
py -3 scripts\15_pcs_status.py

Write-Host "PCS pipeline complete."
