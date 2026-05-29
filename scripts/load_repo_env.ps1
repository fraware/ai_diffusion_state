# Load KEY=VALUE lines from repo .env into the current PowerShell session.
# Skips comments and blank lines. Does not overwrite variables already set.
$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$envFile = Join-Path $repoRoot ".env"
if (-not (Test-Path $envFile)) {
    Write-Warning "No .env at $envFile"
    return
}
Get-Content $envFile | ForEach-Object {
    $line = $_.Trim()
    if (-not $line -or $line.StartsWith("#")) { return }
    if ($line -notmatch '^([^=]+)=(.*)$') { return }
    $name = $Matches[1].Trim()
    $value = $Matches[2].Trim().Trim('"')
    if (-not [string]::IsNullOrWhiteSpace($name) -and -not (Get-Item -Path "env:$name" -ErrorAction SilentlyContinue)) {
        Set-Item -Path "env:$name" -Value $value
    } elseif (-not [string]::IsNullOrWhiteSpace($name)) {
        Set-Item -Path "env:$name" -Value $value
    }
}
