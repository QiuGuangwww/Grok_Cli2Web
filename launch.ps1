# Windows counterpart of launch.sh — start in the background and open the browser.
# Original launch.sh is unchanged.
$ErrorActionPreference = "Stop"

$Root = $PSScriptRoot
if (-not $Root) { $Root = Split-Path -Parent $MyInvocation.MyCommand.Path }
$Port = if ($env:PORT) { $env:PORT } else { "8787" }
$Url = "http://127.0.0.1:$Port"
$Data = Join-Path $HOME ".grok\web-chat"
$Log = Join-Path $Data "server.log"
$ErrLog = Join-Path $Data "server.err.log"
New-Item -ItemType Directory -Force -Path $Data | Out-Null
Set-Content -LiteralPath (Join-Path $Data "home.txt") -Value $Root -Encoding utf8

function Test-GrokHealth([string]$Target) {
    try {
        if (Get-Command curl.exe -ErrorAction SilentlyContinue) {
            & curl.exe -sf --noproxy "*" --max-time 1 "$Target/api/health" *> $null
            return ($LASTEXITCODE -eq 0)
        }
        Invoke-WebRequest -Uri "$Target/api/health" -UseBasicParsing -TimeoutSec 1 | Out-Null
        return $true
    } catch {
        return $false
    }
}

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

function Install-WebSkill([string]$RepoRoot) {
    $src = Join-Path $RepoRoot ".grok\skills\web"
    if (-not (Test-Path -LiteralPath $src)) { return }
    $dstParent = Join-Path $HOME ".grok\skills"
    New-Item -ItemType Directory -Force -Path $dstParent | Out-Null
    Copy-Item -Recurse -Force -Path $src -Destination (Join-Path $dstParent "web")
}

$already = Test-GrokHealth $Url
if (-not $already) {
    Set-Location -LiteralPath $Root
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
    # Hidden VBS + WMI: no console window, and not in Grok's Job Object.
    # pythonw crashes uvicorn (no stdout). python.exe needs a hidden host.
    $vbs = Join-Path $Data "run-server.vbs"
    $vbsBody = @"
Set sh = CreateObject("WScript.Shell")
sh.CurrentDirectory = "$($Root.Replace('\','\\'))"
sh.Environment("Process")("PORT") = "$Port"
sh.Run """$($venvPy.Replace('\','\\'))"" ""$($Root.Replace('\','\\'))\\server.py""", 0, False
"@
    Set-Content -LiteralPath $vbs -Value $vbsBody -Encoding ascii
    $created = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
        CommandLine = "wscript.exe //B `"$vbs`""
        CurrentDirectory = $Root
    }
    if (-not $created -or [int]$created.ReturnValue -ne 0 -or -not $created.ProcessId) {
        Write-Host "Failed to start server process"
        exit 1
    }
    Set-Content -LiteralPath (Join-Path $Data "server.pid") -Value $created.ProcessId -Encoding ascii

    $ok = $false
    for ($i = 0; $i -lt 40; $i++) {
        if (Test-GrokHealth $Url) { $ok = $true; break }
        Start-Sleep -Milliseconds 250
    }
    if (-not $ok) {
        Write-Host "Start failed. Log: $Log"
        if (Test-Path -LiteralPath $ErrLog) {
            Write-Host "Error log: $ErrLog"
        }
        exit 1
    }
}

Install-WebSkill $Root

if ($already) {
    Write-Host "Grok Chat already running: $Url"
} else {
    Write-Host "Grok Chat started: $Url"
}
