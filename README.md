<div align="center">

<img src="static/grok-mark.svg" width="72" alt="Grok" />

# Grok-Cli2Web

A local web UI for Grok, styled after Claude

Listens on `127.0.0.1` only · chats stay on disk in `~/.grok/web-chat/`

[Features](#features) · [Multi-agent](#multi-agent) · [Run](#run) · [Auth](#auth) · [`/web`](#grok-cli-web)

</div>

---

## Features

- Streaming replies with Markdown, tables, and KaTeX (`$...$` / `$$...$$`)
- Modes in the composer (chat, research, web, think, code, write, **multi-agent**)
- Copy on code blocks and tables; edit or regenerate messages
- Upload, drag, or paste images and documents
- Load Grok CLI history from `~/.grok/sessions/` and continue those chats here
- `/` command menu: modes, export, usage, workflows, and more
- Server-side tools: web search, X search, and code interpreter (tool stubs are stripped from the answer)
- Inspect panel: process, team roster, and progress board; drag sidebars and the graph to resize
- Settings split like Claude (account / multi-agent / appearance / language)
- Themes, plus UI in 中文 / English / 日本語

## Multi-agent

Composer mode **Multi-agent**. The lead plans a few steps; independent steps run together. A step can have several specialists plus a step lead who aligns them. Later steps reuse the progress board instead of starting over.

The slider is a **maximum** headcount (2–144), not a fixed roster. Lead and workers use separate models in settings.

```mermaid
flowchart TD
  U[You] --> L[Lead plans steps]
  L --> P[Independent steps in parallel]
  P --> A[Step lead aligns workers]
  A --> V[Reviewer]
  V -->|pass| F[Lead writes the answer]
  V -->|send back| D[Lead decides]
  D -->|rework: reuse the same agents| P
  D -->|good enough| F
  W[Any specialist] -.->|don't guess: ask a teammate| P
  U -.->|click a worker and type guidance| W
```

- **Reviewer** can send work back. The lead decides whether another round is needed, and extra rounds reuse existing agents (at most two).
- If the lead still cannot decide without guessing, it asks you in a `/`-style multiple choice. The last option is always **Other**.
- Specialists must not invent missing facts. They route uncertainty to the right teammate (search, verify, compute, write, …).
- While a run is live, click a worker in the **team list or the graph** and send a short note. It applies after that agent’s current turn.
- The graph is Obsidian-style: green node = working, green edge = aligning, amber edge = feedback / send-back. Nodes can be dragged; nearby nodes slide out of the way.

## Run

```bash
git clone https://github.com/QiuGuangwww/Grok_Cli2Web.git
cd Grok_Cli2Web
chmod +x start.sh launch.sh
./launch.sh
```

Then open [http://127.0.0.1:8787](http://127.0.0.1:8787).

| Script | What it does |
| --- | --- |
| `./launch.sh` | Start in the background (or reuse a running instance) and open the browser |
| `./start.sh` | Run in the foreground; `Ctrl+C` stops it |

Python 3.13+ is required (Homebrew Python 3.14 `venv` is flaky on some machines). Dependencies install into `.venv` automatically.

## Auth

Credentials are resolved in this order:

1. `XAI_API_KEY` in the environment (or a gitignored `.env`)
2. An API key saved in the in-app settings page
3. Your existing `grok login` session at `~/.grok/auth.json`

If you already use the Grok CLI, you usually do not need a separate key.

## Grok CLI: `/web`

In a Grok TUI session:

```
/web
```

That starts this app (or reuses it) and opens the browser. The skill lives in this repo at `.grok/skills/web/`. Copy it to your user skills to use `/web` everywhere:

```bash
mkdir -p ~/.grok/skills
cp -R .grok/skills/web ~/.grok/skills/
export GROK_CHAT_HOME="$PWD"   # needed if the repo is not at ~/code/grok-chat
```

## Shortcuts

`Enter` send · `Shift+Enter` newline · `/` commands · `⌘N` new chat · `⌘K` search history

Enter during IME composition (for example Chinese pinyin confirm) does not send.

## Config

| Variable | Meaning |
| --- | --- |
| `XAI_API_KEY` | API key from [console.x.ai](https://console.x.ai) |
| `PORT` | Listen port, default `8787` |
| `GROK_CHAT_HOME` | Repo path used by `/web` and `launch.sh` |

Data lives in `~/.grok/web-chat/` (conversations, uploads, optional key). Do not commit that folder.

## License

MIT
