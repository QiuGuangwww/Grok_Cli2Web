---
name: web
description: >
  Start the local Grok Chat website at http://127.0.0.1:8787 and open it.
  Use when the user runs /web, says "open the web UI", "打开网页",
  or wants the localhost chat interface.
user-invocable: true
metadata:
  short-description: "Start local Grok Chat"
---

# /web

Start the local chat UI. Do not ask questions. Do not run `start.sh` or `start.ps1` in the foreground.

## Windows (PowerShell / pwsh / cmd)

Run this with the terminal tool:

```powershell
$root = $env:GROK_CHAT_HOME
if (-not $root) {
  $homeFile = Join-Path $HOME ".grok\web-chat\home.txt"
  if (Test-Path -LiteralPath $homeFile) {
    $root = (Get-Content -LiteralPath $homeFile -Raw).Trim()
  }
}
if (-not $root) {
  if (Test-Path -LiteralPath ".\launch.cmd") { $root = (Resolve-Path ".").Path }
  elseif (Test-Path -LiteralPath "$HOME\Grok_Cli2Web\launch.cmd") { $root = "$HOME\Grok_Cli2Web" }
  elseif (Test-Path -LiteralPath "$HOME\code\grok-chat\launch.sh") { $root = "$HOME\code\grok-chat" }
}
if (-not $root) { throw "set GROK_CHAT_HOME to the Grok_Cli2Web repo" }
& "$root\launch.cmd"
```

Reply with the printed URL.

## macOS / Linux / Git Bash

```bash
ROOT="${GROK_CHAT_HOME:-}"
if [ -z "$ROOT" ]; then
  if [ -x "$PWD/launch.sh" ]; then ROOT="$PWD"
  elif [ -x "$HOME/code/grok-chat/launch.sh" ]; then ROOT="$HOME/code/grok-chat"
  fi
fi
bash "${ROOT:?set GROK_CHAT_HOME to the grok-chat repo}/launch.sh"
```

Reply with the printed URL.
