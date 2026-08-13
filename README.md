# Grok Chat

A localhost chat UI for [Grok](https://x.ai), visually close to Claude: warm paper background, centered composer, sidebar history, `/` commands, file upload.

The server binds to `127.0.0.1` only. Conversations stay on your machine under `~/.grok/web-chat/`.

## Run

```bash
git clone https://github.com/YOU/grok-chat.git
cd grok-chat
chmod +x start.sh launch.sh
./launch.sh
```

- `./launch.sh` — start in the background (or reuse a running instance) and open the browser
- `./start.sh` — run in the foreground (`Ctrl+C` stops it)

Then open [http://127.0.0.1:8787](http://127.0.0.1:8787).

Needs Python 3.13+ (3.14's `venv` is flaky on some Homebrew installs). Dependencies install into `.venv` automatically.

## Auth

Credentials are resolved in this order:

1. `XAI_API_KEY` in the environment (or a gitignored `.env`)
2. An API key saved in the in-app settings page
3. Your existing `grok login` session at `~/.grok/auth.json`

If you already use the Grok CLI, you usually do not need a separate key.

## Grok CLI: `/web`

From a Grok TUI session:

```
/web
```

That starts this app (or reuses it) and opens the browser. The skill lives at `~/.grok/skills/web/` after you copy it, or in this repo under `.grok/skills/web/`.

```bash
mkdir -p ~/.grok/skills
cp -R .grok/skills/web ~/.grok/skills/
export GROK_CHAT_HOME="$PWD"   # if the repo is not ~/code/grok-chat
```

## What it does

- Streaming replies with Markdown, tables, KaTeX (`$...$` / `$$...$$`)
- Copy on code blocks and tables
- Upload / drag / paste images and documents
- Loads Grok CLI sessions from `~/.grok/sessions/` (read-only; you can continue them here)
- `/` command menu (modes, export, usage, workflows, …)
- Server-side tools: web search, X search, code interpreter — tool stubs are stripped so they never show up as the answer

## Shortcuts

`Enter` send · `Shift+Enter` newline · `/` commands · `⌘N` new chat · `⌘K` search history

## Config

| Variable | Meaning |
| --- | --- |
| `XAI_API_KEY` | API key from [console.x.ai](https://console.x.ai) |
| `PORT` | Listen port, default `8787` |
| `GROK_CHAT_HOME` | Repo path used by `/web` / `launch.sh` helpers |

Data: `~/.grok/web-chat/` (conversations, uploads, optional key). Never commit that folder.

## License

MIT
