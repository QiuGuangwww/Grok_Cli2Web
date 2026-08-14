# Windows counterpart of start.sh — run in the foreground. Ctrl+C stops it.
# Original start.sh is unchanged.
$ErrorActionPreference = "Stop"

$Root = $PSScriptRoot
if (-not $Root) { $Root = Split-Path -Parent $MyInvocation.MyCommand.Path }
Set-Location -LiteralPath $Root

$Port = if ($env:PORT) { $env:PORT } else { "8787" }
$Url = "http://127.0.0.1:$Port"
$Data = Join-Path $HOME ".grok\web-chat"
New-Item -ItemType Directory -Force -Path $Data | Out-Null
Set-Content -LiteralPath (Join-Path $Data "home.txt") -Value $Root -Encoding utf8

function Test-Python313([string]$Exe, [string[]]$PrefixArgs) {
    try {
        $out = & $Exe @($PrefixArgs + "--version") 2>&1 | Out-String
        if ($out -match "Python (\d+)\.(\d+)") {
            $maj = [int]$Matches[1]
            $min = [int]$Matches[2]
            return ($maj -gt 3) -or ($maj -eq 3 -and $min -ge 13)
        }
    } catch { }
    return $false
}

function Find-Python313 {
    $tries = @(
        @{ E = "py"; A = @("-3.14") },
        @{ E = "py"; A = @("-3.13") },
        @{ E = "py"; A = @("-3") },
        @{ E = "python3.14"; A = @() },
        @{ E = "python3.13"; A = @() },
        @{ E = "python"; A = @() }
    )
    foreach ($t in $tries) {
        if (-not (Get-Command $t.E -ErrorAction SilentlyContinue)) { continue }
        if (Test-Python313 $t.E $t.A) { return $t }
    }
    return $null
}

$venvPy = Join-Path $Root ".venv\Scripts\python.exe"
$venvOk = (Test-Path -LiteralPath $venvPy) -and (Test-Python313 $venvPy @())
if (-not $venvOk) {
    if (Test-Path -LiteralPath (Join-Path $Root ".venv")) {
        Remove-Item -Recurse -Force (Join-Path $Root ".venv")
    }
    $py = Find-Python313
    if (-not $py) {
        Write-Host "Failed to create venv. Install Python 3.13+"
        exit 1
    }
    & $py.E @($py.A + @("-m", "venv", (Join-Path $Root ".venv")))
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $venvPy)) {
        Write-Host "Failed to create venv. Install Python 3.13+"
        exit 1
    }
}

& $venvPy -m pip install -q -r (Join-Path $Root "requirements.txt")
if ($LASTEXITCODE -ne 0) {
    Write-Host "pip install failed"
    exit 1
}

$env:PORT = "$Port"
Write-Host ""
Write-Host "  Grok Chat  →  $Url"
Write-Host "  Press Ctrl+C to stop"
Write-Host ""

Start-Job -ScriptBlock {
    param($Target)
    Start-Sleep -Milliseconds 800
    Start-Process $Target
} -ArgumentList $Url | Out-Null

& $venvPy (Join-Path $Root "server.py")
exit $LASTEXITCODE
