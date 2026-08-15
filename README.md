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
- Upload, drag, or paste images and documents. Every composer mode (chat, research, web, think, code, write, multi-agent) can read local files like the CLI. The permission menu is 需要批准 / 自动审批 / 全部权限; a crew asks once for the whole run, not per specialist.
- Load Grok CLI history from `~/.grok/sessions/` as **read-only** (web chats stay in `~/.grok/web-chat/`)
- `/` command menu: modes, export, usage, workflows, and more
- Server-side tools: web search, X search, and code interpreter (tool stubs are stripped from the answer)
- If a reply loops on “I’ll call / I’ll execute”, it is cut off and recovered in layers: retry, swap model, then shrink the task
- Inspect panel for process and team; **View process** only appears when there is something to show
- Settings split like Claude (account / multi-agent / appearance / language). Multi-agent has a headcount cap and a **run budget** slider (far right = ♾️ Unlimited)
- Themes: light, paper, moss, **azure**; dark, midnight, dusk, **cyber**. UI in 中文 / English / 日本語

## Multi-agent

Composer mode **Multi-agent**. The lead plans a few steps; independent steps run together. A step can have several specialists plus a step lead who aligns them. Later steps consume a **filtered fact contract** (claim, source, confidence), not other specialists' essays. The original user goal is pinned and cannot be overwritten by the board.

The headcount slider is a **maximum** (2–144), not a fixed roster. A second slider sets the **run budget** in tokens; the far right is **Unlimited** (♾️). A tighter cap uses fewer specialists and fewer rework rounds, then synthesizes with what it has. Lead and workers use separate models in settings.

<p align="center">
  <img src="static/crew.svg" alt="Multi-agent flow: Brain owns the contract, verifies contested claims once, records equally sourced splits as disputed facts, then scores whether to stop or reuse agents" width="720" />
</p>

<p align="center"><em>Brain is the state machine, not another chatting agent. Specialists never share full essays — only a filtered contract.</em></p>

- A **server-side state machine (Brain)** owns the run: plan version, contract, spend, who is running, who was sent back, and when to stop. Reviewer JSON is optional; missing output is decided in code.
- Stall recovery is layered (retry → swap model → shrink the brief). After that the agent is marked partial and the crew continues.
- **Reviewer** can send work back. Extra rounds **reuse** existing agents and hand them a changelog of what changed. Two review passes is the hard cap; a score (coverage, confidence, open conflicts, your acceptance points) can stop earlier.
- If Brain cannot decide without guessing, questions are **batched** into one `/`-style choice. The last option is always **Other**.
- Specialists must not invent missing facts. They route uncertainty to the right teammate. Later agents only see contract entries tagged for them.
- **Conflicts:** higher confidence / sourced claim wins. An unresolved tie is `contested`; Brain freezes dependents and sends a verify/cite specialist **once**. If both sides stay equally sourced, that pair is promoted to a permanent **`disputed`** fact with both citations. Downstream reports the split — it does not wait for a winner, and review does not send the crew back just because the world disagrees. Ordinary workers never see unresolved `contested` claims.
- Guidance you type into a worker is written back into Brain (new plan version + updated brief). Later scheduling follows the correction, not the old plan.
- While a run is live, click a worker in the team list or the graph and type guidance. Stop marks every live agent as stopped; switching chats closes the team pane so it does not leak into another conversation.
- Graph: green node = working, green edge = aligning, amber edge = feedback or verify. Nodes can be dragged. **View process** stays hidden when there is nothing to show.

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

### Windows

```powershell
git clone https://github.com/QiuGuangwww/Grok_Cli2Web.git
cd Grok_Cli2Web
.\launch.cmd
```

Then open [http://127.0.0.1:8787](http://127.0.0.1:8787).

| Script | What it does |
| --- | --- |
| `.\launch.cmd` / `.\launch.ps1` | Start in the background (or reuse a running instance) and print the URL |
| `.\start.cmd` / `.\start.ps1` | Run in the foreground; `Ctrl+C` stops it |

`launch.cmd` / `start.cmd` bypass ExecutionPolicy so you do not need to change system policy. Python 3.13+ is required (`py -3.14` or `py -3.13`). The default `python` on some PCs is 3.10 and will be skipped.

On Windows, `launch.cmd` starts uvicorn through a hidden VBS + WMI process so the server is not killed when the Grok TUI `/web` skill returns.

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

Windows (PowerShell):

```powershell
New-Item -ItemType Directory -Force "$HOME\.grok\skills" | Out-Null
Copy-Item -Recurse -Force .\.grok\skills\web "$HOME\.grok\skills\"
```

`.\launch.cmd` also copies the skill and writes the repo path to `~\.grok\web-chat\home.txt`, so `/web` works from any directory after the first launch. Set `GROK_CHAT_HOME` only if you move the repo.

## Shortcuts

`Enter` send · `Shift+Enter` newline · `/` commands · `⌘N` / `Ctrl+N` new chat · `⌘K` / `Ctrl+K` search history

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
