# Launch IIDS Phase-1 production on WSL (DEPRECATED — use external SSD; see docs/ATLAS_IIDS_CLEAN_RESTART_RUNBOOK.md).
$ErrorActionPreference = "Stop"
if (-not $PSBoundParameters.ContainsKey("ForceWsl")) {
    Write-Error @"
WSL production is deprecated. Do not download to /home/mateo/iids_sources.

Use external SSD instead:
  powershell -File scripts/windows_iids_external.ps1 -TargetDir D:\iids_sources -Step docs
  powershell -File scripts/windows_iids_external.ps1 -TargetDir D:\iids_sources -Step detail

See docs/ATLAS_IIDS_CLEAN_RESTART_RUNBOOK.md
"@
}
$repo = "C:\Users\mateo\ai_diffusion_state"
if (-not $env:OPENXLAB_AK -or -not $env:OPENXLAB_SK) {
    Write-Error "Set OPENXLAB_AK and OPENXLAB_SK before running production."
}
$ak = $env:OPENXLAB_AK
$sk = $env:OPENXLAB_SK
$ssl = if ($env:OPENXLAB_INSECURE_SSL) { $env:OPENXLAB_INSECURE_SSL } else { "1" }
Write-Host "Starting WSL IIDS production (log: outputs/logs/iids_wsl_production.log)"
wsl.exe -d Ubuntu env `
    OPENXLAB_AK=$ak `
    OPENXLAB_SK=$sk `
    OPENXLAB_INSECURE_SSL=$ssl `
    PYTHONUTF8=1 `
    bash /mnt/c/Users/mateo/ai_diffusion_state/scripts/wsl_iids_production.sh
