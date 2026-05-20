# Repro verification for sprint Step 1 (Windows PowerShell)
$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$LogDir = Join-Path $Root "docs\run_logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$LogFile = Join-Path $LogDir "repro_run_2026_05_20.txt"
$FailureFile = Join-Path $LogDir "repro_failure_2026_05_20.md"

function Write-Log($msg) {
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$ts $msg" | Tee-Object -FilePath $LogFile -Append
}

Write-Log "=== Repro verification start ==="
Write-Log "OS: $([System.Environment]::OSVersion.VersionString)"
Write-Log "Python: $(python --version 2>&1)"
Write-Log "CWD: $Root"
$baci = Test-Path (Join-Path $Root "data\raw\baci\BACI_HS17_V202601.zip")
Write-Log "BACI raw zip present: $baci"

$failed = $false
$failCmd = ""
$failErr = ""

$steps = @(
    @("venv", { python -m venv .venv }),
    @("pip", { .\.venv\Scripts\python -m pip install -e ".[dev]" }),
    @("seed", { make seed }),
    @("fetch", { make fetch }),
    @("build", { make build }),
    @("panel", { make panel }),
    @("analysis", { make analysis }),
    @("paper", { make paper }),
    @("test", { make test })
)

foreach ($step in $steps) {
    $name = $step[0]
    Write-Log "--- $name ---"
    try {
        & $step[1]
        if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) { throw "exit code $LASTEXITCODE" }
        Write-Log "$name OK"
    } catch {
        $failed = $true
        $failCmd = $name
        $failErr = $_.Exception.Message
        Write-Log "$name FAILED: $failErr"
        break
    }
}

if ($failed) {
    @"
# Repro failure 2026-05-20

- **Failing step:** $failCmd
- **Error:** $failErr
- **OS:** $([System.Environment]::OSVersion.VersionString)
- **Python:** $(python --version 2>&1)
- **BACI raw present:** $baci
- **Log:** docs/run_logs/repro_run_2026_05_20.txt
"@ | Set-Content -Path $FailureFile -Encoding utf8
    Write-Log "Wrote $FailureFile"
    exit 1
}

Write-Log "=== Repro verification complete ==="
exit 0
