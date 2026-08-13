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

Start the local chat UI. Do not ask questions. Do not run `start.sh` in the foreground.

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
