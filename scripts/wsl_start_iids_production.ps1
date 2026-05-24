# Launch IIDS Phase-1 production on WSL (uses ~950 GB WSL disk, not Windows C:).
$ErrorActionPreference = "Stop"
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
