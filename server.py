#!/usr/bin/env python3
"""Local Claude-style chat UI for Grok, bound to localhost only."""

from __future__ import annotations

import asyncio
import base64
import json
import mimetypes
import os
import re
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import logging

import httpx
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
DATA_DIR = Path.home() / ".grok" / "web-chat"
UPLOADS = DATA_DIR / "uploads"
CONTINUATIONS = DATA_DIR / "cli_continuations"
CONV_PATH = DATA_DIR / "conversations.json"
SETTINGS_PATH = DATA_DIR / "settings.json"
AUTH_PATH = Path.home() / ".grok" / "auth.json"
SESSIONS_DIR = Path.home() / ".grok" / "sessions"
XAI_BASE = "https://api.x.ai/v1"
MAX_UPLOAD_BYTES = 48 * 1024 * 1024
IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp", "image/gif"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

log = logging.getLogger("grok-chat")

DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS.mkdir(parents=True, exist_ok=True)
CONTINUATIONS.mkdir(parents=True, exist_ok=True)

MODE_PROMPTS = {
    "chat": (
        "You are Grok, a helpful, sharp, and warm assistant from xAI. "
        "Reply in the user's language. Use clean Markdown. Be concise unless the user wants depth."
    ),
    "research": (
        "You are Grok in deep-research mode. Search the web, cross-check sources, "
        "and write a structured report with headings, key findings, uncertainties, and links. "
        "Reply in the user's language. Prefer evidence over speculation."
    ),
    "web": (
        "You are Grok. Use web search for current facts, news, prices, and anything that may have changed. "
        "Cite sources briefly. Reply in the user's language."
    ),
    "think": (
        "You are Grok in careful-reasoning mode. Slow down, examine assumptions, "
        "consider alternatives, and give a precise answer. Reply in the user's language."
    ),
    "code": (
        "You are Grok as a senior software engineer. Prefer working code, exact file paths, "
        "and concise explanations. Reply in the user's language unless the user is writing code."
    ),
    "write": (
        "You are Grok as an editor and writer. Improve clarity, rhythm, and tone. "
        "Offer a polished draft first, then brief notes. Reply in the user's language."
    ),
    "multi": (
        "You are the lead agent of a small local team. "
        "Give a clear final answer in the user's language after your specialists report in."
    ),
}

ASK_RULE = (
    "If a material decision is missing (goal, audience, constraint, or two mutually exclusive directions) "
    "and you would have to guess, do not guess. After a short note in the user's language, emit one control JSON: "
    '{"ask":{"question":"...","options":[{"id":"a","label":"...","desc":"..."}]}}. '
    "Give 2-4 concrete options. Do not include an Other option. "
    "Ask only when you cannot proceed without that choice."
)

TOOL_RULE = (
    "You have real server-side tools (web_search, x_search, code_interpreter). "
    "Call those tools instead of writing tool invocations as text. "
    "Never narrate that you are about to call a tool, and never write I'll call / I'll execute / I'll go. "
    "If you need a tool, call it. Otherwise write the result. "
    "Never output tool names, XML, HTML, JSON stubs, function_call blocks, "
    "or chain-of-thought. The user only sees your final answer."
)

NOLOOP_RULE = (
    "You previously got stuck repeating that you would call a tool or start work. "
    "Do not write any sentence about what you will do next. "
    "Call a real server-side tool now, or write the actual answer now."
)

SHRINK_RULE = (
    "Your previous attempt stalled. Do a SMALLER job: one concrete result, at most 180 words. "
    "No preamble. No 'I will'. If you cannot finish, write the partial facts you already have."
)

STALL_RE = re.compile(
    r"(?:"
    r"I(?:'ll| will)\s+(?:"
    r"go(?:\s+ahead|\s+now)?"
    r"|run(?:\s+it)?"
    r"|do(?:\s+it(?:\s+now)?|\s+that(?:\s+now)?|\s+the\s+\w+)?"
    r"|call(?:\s+now|\s+the\s+\w+)?"
    r"|execute(?:\s+now|\s+verification(?:\s+code)?|\s+the\s+\w+)?"
    r"|invoke(?:\s+now|\s+the\s+\w+)?"
    r"|start(?:\s+now|\s+the\s+\w+)?"
    r"|send(?:\s+it|\s+the\s+\w+)?"
    r"|begin(?:\s+now|\s+the\s+\w+)?"
    r"|proceed|write(?:\s+it|\s+the\s+\w+)?"
    r"|actually\s+\w+"
    r")(?:\s+\w+){0,8}"
    r"|Let me (?:just )?(?:call|run|execute|invoke|start)"
    r"|我(?:现在|这就)?(?:来|去|开始)?(?:调用|执行|跑|写)(?:一下|了|起来)?"
    r")\.?",
    re.I,
)

FEEDBACK_RULE = (
    "Do not guess missing facts, sources, numbers, or another specialty's work. "
    "If you are uncertain or blocked, ask the matching teammate (search, verify, compute, write, review, etc.). "
    "After your draft you MAY emit one control JSON object: "
    '{"facts":[{"claim":"...","source":"url-or-paper","confidence":"high|medium|low|hypothesis","for":["step-id-or-role"]}],'
    '"feedback":[{"to":"agent-id-or-name","ask":"..."}]}. '
    "facts = checkable claims only, not prose. Omit feedback if you have no request. "
    "The control JSON is for routing, not for the user."
)

GOAL_PIN = (
    "IMMUTABLE GOAL — never replace, broaden, or drift from this. "
    "The contract below is read-only evidence. Hypothesis is not fact. "
    "If a contract entry conflicts with the goal, keep the goal and flag the conflict."
)

DEFAULT_TOOLS = [
    {"type": "web_search"},
    {"type": "x_search"},
    {"type": "code_interpreter"},
]

TOOL_NAMES = (
    "web_search",
    "x_search",
    "code_interpreter",
    "code_execution",
    "image_generation",
    "view_image",
    "attachment_search",
    "file_search",
    "collections_search",
    "browse_page",
    "web_fetch",
    "open_page",
)
_TOOL_ALT = "|".join(re.escape(n) for n in TOOL_NAMES)

LEAK_PATTERNS = [
    re.compile(rf"```(?:html|xml|json|text|tool)?\s*(?:{_TOOL_ALT})\b[\s\S]*?```", re.I),
    re.compile(rf"<(?:{_TOOL_ALT})\b[\s\S]*?</(?:{_TOOL_ALT})>", re.I),
    re.compile(
        r"<(?:xai:)?(?:function_call|tool_call|tool_request|invoke)\b[\s\S]*?</(?:xai:)?(?:function_call|tool_call|tool_request|invoke)>",
        re.I,
    ),
    re.compile(
        rf"(?:^|\n)\s*(?:{_TOOL_ALT})\s*\n\s*(?:query|q|arguments|input|code|prompt|num_results)\s*\n[\s\S]*?(?=\n\n|\n```|$)",
        re.I,
    ),
]
LEAK_OPENERS = (
    "```html",
    "```xml",
    "```json",
    "```tool",
    "<function_call",
    "<tool_call",
    "<xai:function_call",
) + tuple(f"<{name}" for name in TOOL_NAMES) + tuple(f"{name}\n" for name in TOOL_NAMES)


def strip_tool_leak(text: str) -> str:
    cleaned = text or ""
    for pat in LEAK_PATTERNS:
        cleaned = pat.sub("\n", cleaned)
    cleaned = re.sub(r"```(?:html|xml|json|tool)\s*```", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def stall_hits(text: str) -> list[re.Match[str]]:
    return list(STALL_RE.finditer(text or ""))


def repeated_chunk(text: str) -> bool:
    tail = (text or "")[-2500:]
    if len(tail) < 160:
        return False
    for size in (16, 24, 36, 48, 64):
        chunk = tail[-size:]
        if len(chunk.strip()) < 8:
            continue
        if tail.count(chunk) >= 5:
            return True
    return False


def loop_detected(text: str) -> bool:
    blob = text or ""
    if repeated_chunk(blob):
        return True
    hits = stall_hits(blob[-4000:])
    if len(hits) >= 6:
        return True
    if len(hits) >= 5 and hits[-1].end() - hits[-5].start() < 900:
        return True
    return False


def trim_loop(text: str) -> str:
    cleaned = visible_answer(text or "")
    hits = stall_hits(cleaned)
    if len(hits) >= 3:
        for i in range(len(hits) - 2):
            if hits[i + 2].end() - hits[i].start() < 420:
                return cleaned[: hits[i].start()].rstrip()
    tail = cleaned[-2000:]
    for size in (20, 32, 48):
        chunk = tail[-size:]
        if len(chunk.strip()) < 10:
            continue
        first = cleaned.find(chunk)
        if first != -1 and cleaned.count(chunk) >= 4:
            return cleaned[:first].rstrip()
    return cleaned.strip()


def noloop_payload(payload: dict[str, Any]) -> dict[str, Any]:
    nxt = {**payload}
    inputs = list(payload.get("input") or [])
    patched = False
    for i, msg in enumerate(inputs):
        if isinstance(msg, dict) and msg.get("role") == "system":
            inputs[i] = {**msg, "content": f"{msg.get('content') or ''} {NOLOOP_RULE}"}
            patched = True
            break
    if not patched:
        inputs = [{"role": "system", "content": NOLOOP_RULE}, *inputs]
    nxt["input"] = inputs
    return nxt


def recover_model(model: str) -> str | None:
    table = {"grok-4.6": "grok-4.5", "grok-4.5": "grok-4.3", "grok-4.3": "grok-4.5"}
    return table.get(model)


def shrink_payload(payload: dict[str, Any]) -> dict[str, Any]:
    nxt = noloop_payload(payload)
    inputs = []
    for msg in nxt.get("input") or []:
        if isinstance(msg, dict) and msg.get("role") == "system":
            inputs.append({**msg, "content": f"{msg.get('content') or ''} {SHRINK_RULE}"})
        elif isinstance(msg, dict) and msg.get("role") == "user":
            body = str(msg.get("content") or "")
            if len(body) > 1200:
                body = body[:1200] + "\n…"
            inputs.append({**msg, "content": f"{body}\n\nDo only the smallest next check. 180 words max."})
        else:
            inputs.append(msg)
    nxt["input"] = inputs
    return nxt


def is_drop_error(exc: BaseException) -> bool:
    if isinstance(exc, (httpx.RemoteProtocolError, httpx.ReadError, httpx.ConnectError, httpx.WriteError, httpx.TimeoutException)):
        return True
    blob = str(exc).lower()
    return any(
        key in blob
        for key in (
            "incomplete chunked",
            "peer closed connection",
            "connection reset",
            "server disconnected",
            "remoteprotocolerror",
            "stream closed",
        )
    )


def looks_complete(text: str) -> bool:
    blob = (text or "").strip()
    if len(blob) < 360:
        return False
    return blob[-1] in "。！？.!?」』…)"


def next_recovery(payload: dict[str, Any], restarts: int) -> dict[str, Any] | None:
    if restarts >= 3:
        return None
    if restarts == 0:
        return {"label": "检测到空转，已打断并重试", "payload": noloop_payload(payload)}
    if restarts == 1:
        model = str(payload.get("model") or "")
        alt = recover_model(model)
        nxt = noloop_payload({**payload, "model": alt or model})
        if isinstance(nxt.get("reasoning"), dict):
            nxt["reasoning"] = {"effort": _soften_effort(str(nxt["reasoning"].get("effort") or "medium"))}
        return {"label": f"空转未消，换模型再试（{alt or model}）", "payload": nxt}
    nxt = shrink_payload(payload)
    alt = recover_model(str(payload.get("model") or ""))
    if alt:
        nxt["model"] = alt
    if isinstance(nxt.get("reasoning"), dict):
        nxt["reasoning"] = {"effort": "low"}
    return {"label": "仍空转，缩小任务再试", "payload": nxt}


def visible_answer(text: str) -> str:
    cleaned = strip_tool_leak(text)
    lower = cleaned.lower()
    cut = len(cleaned)
    for marker in LEAK_OPENERS:
        idx = lower.rfind(marker)
        if idx == -1:
            continue
        rest = cleaned[idx:]
        closed = "```" in rest[3:] or bool(re.search(r"</[a-z_]+>", rest, re.I))
        if not closed:
            cut = min(cut, idx)
    return cleaned[:cut].rstrip()


def compact_activity(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    think = ""
    for entry in entries:
        kind = entry.get("kind") or "note"
        if kind == "think":
            think += str(entry.get("text") or "")
            continue
        key = (kind, str(entry.get("query") or entry.get("url") or entry.get("text") or ""))
        if key in seen:
            continue
        seen.add(key)
        out.append(entry)
    if think.strip():
        out.insert(0, {"kind": "think", "text": think.strip()})
    return out[:80]


def harvest_activity(event: dict[str, Any]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    etype = str(event.get("type") or "")
    item = event.get("item") if isinstance(event.get("item"), dict) else {}
    action = item.get("action") if isinstance(item.get("action"), dict) else {}
    extra_action = event.get("action") if isinstance(event.get("action"), dict) else {}
    query = action.get("query") or extra_action.get("query") or item.get("query")
    url = action.get("url") or extra_action.get("url") or item.get("url")
    title = action.get("title") or extra_action.get("title") or item.get("title")
    if query:
        entries.append({"kind": "search", "query": str(query)})
    if url:
        entries.append({"kind": "page", "url": str(url), "title": str(title or url)})
    code = item.get("code") or (item.get("inputs") if isinstance(item.get("inputs"), str) else None)
    if code and "code" in f"{etype} {item.get('type') or ''}".lower():
        entries.append({"kind": "code", "text": str(code)[:4000]})
    ann = event.get("annotation")
    if isinstance(ann, dict) and ann.get("url"):
        entries.append({"kind": "page", "url": str(ann["url"]), "title": str(ann.get("title") or ann["url"])})
    resp = event.get("response") if isinstance(event.get("response"), dict) else {}
    for cite in resp.get("citations") or []:
        if isinstance(cite, str):
            entries.append({"kind": "page", "url": cite, "title": cite})
        elif isinstance(cite, dict) and cite.get("url"):
            entries.append({"kind": "page", "url": str(cite["url"]), "title": str(cite.get("title") or cite["url"])})
    for out_item in resp.get("output") or []:
        if isinstance(out_item, dict):
            entries.extend(harvest_activity({"type": str(out_item.get("type") or ""), "item": out_item}))
    return entries


def tool_status(etype: str, item_type: str = "") -> str | None:
    blob = f"{etype} {item_type}".lower()
    if "x_search" in blob:
        return "正在搜索 X…"
    if "web_search" in blob or "file_search" in blob or "attachment" in blob:
        return "正在搜索…"
    if "code" in blob:
        return "正在运行代码…"
    if "image" in blob:
        return "正在处理图片…"
    if "function" in blob or "tool" in blob or blob.endswith("_call.in_progress"):
        return "正在调用工具…"
    if "reason" in blob:
        return "思考中"
    return None

_lock = threading.Lock()

app = FastAPI(title="Grok Chat", docs_url=None, redoc_url=None)
app.mount("/assets", StaticFiles(directory=STATIC), name="assets")


@app.middleware("http")
async def no_store(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return response


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def load_conversations() -> list[dict[str, Any]]:
    with _lock:
        data = read_json(CONV_PATH, {"conversations": []})
        return data.get("conversations", [])


def save_conversations(items: list[dict[str, Any]]) -> None:
    with _lock:
        write_json(CONV_PATH, {"conversations": items})


def load_settings() -> dict[str, Any]:
    return read_json(SETTINGS_PATH, {})


def save_settings(data: dict[str, Any]) -> None:
    current = load_settings()
    current.update(data)
    write_json(SETTINGS_PATH, current)


def parse_expiry(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)
    text = str(value).strip()
    if not text:
        return None
    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def grok_session() -> dict[str, Any] | None:
    raw = read_json(AUTH_PATH, {})
    if not isinstance(raw, dict) or not raw:
        return None
    best: dict[str, Any] | None = None
    best_exp: datetime | None = None
    for value in raw.values():
        if not isinstance(value, dict) or not value.get("key"):
            continue
        exp = parse_expiry(value.get("expires_at"))
        if best is None or (exp and (best_exp is None or exp > best_exp)):
            best = value
            best_exp = exp
    return best


def resolve_auth() -> dict[str, Any]:
    env_key = os.environ.get("XAI_API_KEY", "").strip()
    if env_key:
        return {"token": env_key, "source": "env", "user": None, "expired": False}

    settings_key = str(load_settings().get("api_key") or "").strip()
    if settings_key:
        return {"token": settings_key, "source": "settings", "user": None, "expired": False}

    session = grok_session()
    if session:
        exp = parse_expiry(session.get("expires_at"))
        expired = bool(exp and exp <= datetime.now(timezone.utc))
        user = {
            "name": session.get("first_name") or "",
            "email": session.get("email") or "",
            "expires_at": session.get("expires_at"),
        }
        return {
            "token": session.get("key") if not expired else "",
            "source": "grok",
            "user": user,
            "expired": expired,
        }

    return {"token": "", "source": "none", "user": None, "expired": False}


def require_token() -> str:
    auth = resolve_auth()
    if auth["expired"]:
        raise HTTPException(401, "Grok 登录已过期，请在终端运行 grok login")
    if not auth["token"]:
        raise HTTPException(401, "未找到可用凭证。请运行 grok login，或在设置里填入 XAI_API_KEY")
    return auth["token"]


def public_conversation(item: dict[str, Any]) -> dict[str, Any]:
    messages = item.get("messages") or []
    preview = ""
    for msg in messages:
        if msg.get("role") == "user" and msg.get("content"):
            preview = str(msg["content"]).strip().replace("\n", " ")
            break
    return {
        "id": item["id"],
        "title": item.get("title") or "新对话",
        "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at"),
        "model": item.get("model") or "grok-4.6",
        "preview": preview[:80],
        "message_count": item.get("message_count") if item.get("message_count") is not None else len(messages),
        "source": item.get("source") or "web",
        "cwd": item.get("cwd"),
    }


def is_cli_id(cid: str | None) -> bool:
    return bool(cid) and str(cid).startswith("cli:")


def cli_sid(cid: str) -> str:
    return cid[4:]


def find_cli_dir(sid: str) -> Path:
    if not SESSIONS_DIR.exists():
        raise HTTPException(404, "对话不存在")
    for summary in SESSIONS_DIR.rglob("summary.json"):
        if "subagents" in summary.parts:
            continue
        if summary.parent.name == sid:
            return summary.parent
        data = read_json(summary, {})
        if (data.get("info") or {}).get("id") == sid:
            return summary.parent
    raise HTTPException(404, "对话不存在")


def parse_cli_messages(session_dir: Path) -> list[dict[str, Any]]:
    path = session_dir / "updates.jsonl"
    if not path.exists():
        return []
    messages: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    tools: list[dict[str, str]] = []

    def flush() -> None:
        nonlocal current, tools
        if not current:
            tools = []
            return
        text = str(current.get("content") or "").strip()
        if current.get("role") == "user" and (
            text.startswith("<system-reminder>") or text.startswith("<user_info>")
        ):
            current = None
            tools = []
            return
        if tools:
            current["tools"] = tools[:12]
        if text or current.get("tools"):
            current["source"] = "cli"
            if (
                messages
                and messages[-1].get("role") == current.get("role") == "assistant"
            ):
                messages[-1]["content"] = (
                    (messages[-1].get("content") or "") + "\n\n" + (current.get("content") or "")
                ).strip()
                if current.get("tools"):
                    messages[-1]["tools"] = (messages[-1].get("tools") or []) + current["tools"]
            else:
                messages.append(current)
        current = None
        tools = []

    try:
        with path.open(encoding="utf-8", errors="replace") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                upd = (obj.get("params") or {}).get("update") or {}
                kind = upd.get("sessionUpdate")
                content = upd.get("content") or {}
                text = content.get("text") if isinstance(content, dict) else ""
                if kind == "user_message_chunk":
                    flush()
                    current = {
                        "id": f"cli-user-{len(messages)}",
                        "role": "user",
                        "content": text or "",
                        "files": [],
                        "created_at": obj.get("timestamp"),
                    }
                elif kind == "agent_message_chunk":
                    if not current or current.get("role") != "assistant":
                        flush()
                        current = {
                            "id": f"cli-asst-{len(messages)}",
                            "role": "assistant",
                            "content": "",
                            "files": [],
                            "created_at": obj.get("timestamp"),
                        }
                    current["content"] = (current.get("content") or "") + (text or "")
                elif kind == "tool_call":
                    title = str(upd.get("title") or upd.get("kind") or "工具")
                    tools.append({"title": title[:80]})
                elif kind == "turn_completed":
                    flush()
    except OSError:
        return messages
    flush()
    return messages


def list_cli_summaries() -> list[dict[str, Any]]:
    if not SESSIONS_DIR.exists():
        return []
    items: list[dict[str, Any]] = []
    for summary in SESSIONS_DIR.rglob("summary.json"):
        if "subagents" in summary.parts:
            continue
        data = read_json(summary, {})
        info = data.get("info") or {}
        sid = info.get("id") or summary.parent.name
        title = data.get("generated_title") or data.get("session_summary") or "CLI 对话"
        cont = read_json(CONTINUATIONS / f"{sid}.json", {})
        items.append(
            {
                "id": f"cli:{sid}",
                "title": cont.get("title") or title,
                "created_at": data.get("created_at"),
                "updated_at": cont.get("updated_at") or data.get("updated_at") or data.get("last_active_at"),
                "model": cont.get("model") or data.get("current_model_id") or "grok-4.6",
                "preview": (data.get("last_turn_summary") or title or "")[:80],
                "message_count": data.get("num_chat_messages") or data.get("num_messages") or 0,
                "source": "cli",
                "cwd": info.get("cwd"),
            }
        )
    return items


def get_web_conversation(cid: str) -> dict[str, Any] | None:
    for item in load_conversations():
        if item["id"] == cid:
            item.setdefault("source", "web")
            return item
    return None


def get_conversation(cid: str) -> dict[str, Any]:
    if is_cli_id(cid):
        sid = cli_sid(cid)
        folder = find_cli_dir(sid)
        summary = read_json(folder / "summary.json", {})
        info = summary.get("info") or {}
        cont = read_json(CONTINUATIONS / f"{sid}.json", {})
        cli_messages = parse_cli_messages(folder)
        extra = cont.get("messages") or []
        title = cont.get("title") or summary.get("generated_title") or summary.get("session_summary") or "CLI 对话"
        return {
            "id": cid,
            "title": title,
            "created_at": summary.get("created_at"),
            "updated_at": cont.get("updated_at") or summary.get("updated_at") or summary.get("last_active_at"),
            "model": cont.get("model") or summary.get("current_model_id") or "grok-4.6",
            "previous_response_id": cont.get("previous_response_id"),
            "messages": cli_messages + extra,
            "source": "cli",
            "cwd": info.get("cwd"),
        }
    item = get_web_conversation(cid)
    if not item:
        raise HTTPException(404, "对话不存在")
    return item


def upsert_conversation(updated: dict[str, Any]) -> dict[str, Any]:
    if is_cli_id(updated.get("id")):
        sid = cli_sid(updated["id"])
        extra = [m for m in (updated.get("messages") or []) if m.get("source") != "cli"]
        write_json(
            CONTINUATIONS / f"{sid}.json",
            {
                "id": updated["id"],
                "title": updated.get("title"),
                "previous_response_id": updated.get("previous_response_id"),
                "model": updated.get("model"),
                "messages": extra,
                "updated_at": updated.get("updated_at") or now_iso(),
            },
        )
        return updated
    items = load_conversations()
    found = False
    for i, item in enumerate(items):
        if item["id"] == updated["id"]:
            items[i] = updated
            found = True
            break
    if not found:
        items.insert(0, updated)
    items.sort(key=lambda x: x.get("updated_at") or "", reverse=True)
    save_conversations(items)
    return updated


def compact_history(messages: list[dict[str, Any]], skip_ids: set[str]) -> str:
    prior = [m for m in messages if m.get("id") not in skip_ids]
    prior = prior[-16:]
    chunks: list[str] = []
    for msg in prior:
        text = str(msg.get("content") or "").strip()
        if not text:
            continue
        role = "USER" if msg.get("role") == "user" else "ASSISTANT"
        chunks.append(f"{role}: {text[:4000]}")
    return "\n\n".join(chunks)


def title_from_text(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", (text or "").strip())
    if not cleaned:
        return "新对话"
    return cleaned[:36] + ("…" if len(cleaned) > 36 else "")


def guess_kind(filename: str, content_type: str | None) -> str:
    mime = (content_type or "").split(";")[0].strip().lower()
    ext = Path(filename).suffix.lower()
    if mime in IMAGE_TYPES or ext in IMAGE_EXTS:
        return "image"
    return "file"


def file_to_data_url(path: Path, mime: str) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


async def upload_remote_file(token: str, path: Path, filename: str) -> str:
    mime = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    data = path.read_bytes()
    files = {"file": (filename, data, mime)}
    form = {"purpose": "assistants", "expires_after": "86400"}
    async with async_client(timeout=120.0) as client:
        resp = await client.post(
            f"{XAI_BASE}/files",
            headers={"Authorization": f"Bearer {token}"},
            data=form,
            files=files,
        )
    if resp.status_code >= 400:
        detail = resp.text[:400]
        raise HTTPException(resp.status_code, f"文件上传到 xAI 失败：{detail}")
    payload = resp.json()
    file_id = payload.get("id")
    if not file_id:
        raise HTTPException(502, "xAI 未返回文件 ID")
    return file_id


class ChatIn(BaseModel):
    conversation_id: str | None = None
    message: str = ""
    file_ids: list[str] = Field(default_factory=list)
    model: str = "grok-4.6"
    web_search: bool = False
    mode: str = "chat"
    effort: str = "high"


class ConversationPatch(BaseModel):
    title: str | None = None
    truncate_before: str | None = None


class SettingsIn(BaseModel):
    api_key: str | None = None
    clear_api_key: bool = False
    lead_model: str | None = None
    lead_effort: str | None = None
    worker_model: str | None = None
    worker_effort: str | None = None
    worker_count: int | None = None


class GuideIn(BaseModel):
    run_id: str
    agent_id: str
    text: str = ""


class AskIn(BaseModel):
    run_id: str
    text: str = ""


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")


@app.get("/api/extras")
async def extras() -> dict[str, Any]:
    workflows: list[dict[str, str]] = []
    roots = [
        Path.home() / ".grok" / "workflows",
        Path.home() / ".grok" / "bundled" / "workflows",
        ROOT / ".grok" / "workflows",
    ]
    seen: set[str] = set()
    for folder in roots:
        if not folder.is_dir():
            continue
        for path in sorted(folder.glob("*.rhai")):
            key = path.stem
            if key in seen:
                continue
            seen.add(key)
            workflows.append({"name": key, "path": str(path)})
    return {
        "workflows": workflows,
        "usage_url": "https://console.x.ai/team/default/usage",
        "docs_url": "https://docs.x.ai/build/overview",
        "privacy_url": "https://console.x.ai",
    }


KNOWN_MODELS = {"grok-4.6", "grok-4.5", "grok-4.3"}
KNOWN_EFFORTS = {"low", "medium", "high", "xhigh"}


def _pick(value: str | None, allowed: set[str], fallback: str) -> str:
    key = (value or "").strip()
    return key if key in allowed else fallback


def clamp_workers(value: Any, fallback: int = 3) -> int:
    try:
        return max(2, min(144, int(value)))
    except (TypeError, ValueError):
        return fallback


def agent_settings() -> dict[str, Any]:
    raw = load_settings()
    return {
        "lead_model": _pick(raw.get("lead_model"), KNOWN_MODELS, "grok-4.6"),
        "lead_effort": _pick(raw.get("lead_effort"), KNOWN_EFFORTS, "high"),
        "worker_model": _pick(raw.get("worker_model"), KNOWN_MODELS, "grok-4.5"),
        "worker_effort": _pick(raw.get("worker_effort"), KNOWN_EFFORTS, "medium"),
        "worker_count": clamp_workers(raw.get("worker_count"), 3),
    }


@app.get("/api/health")
async def health() -> dict[str, Any]:
    auth = resolve_auth()
    return {
        "ok": bool(auth["token"]) and not auth["expired"],
        "source": auth["source"],
        "expired": auth["expired"],
        "user": auth["user"],
        "has_custom_key": bool(str(load_settings().get("api_key") or "").strip()),
        "agents": agent_settings(),
    }


@app.post("/api/settings")
async def update_settings(body: SettingsIn) -> dict[str, Any]:
    patch: dict[str, Any] = {}
    if body.clear_api_key:
        settings = load_settings()
        settings.pop("api_key", None)
        write_json(SETTINGS_PATH, settings)
    elif body.api_key is not None:
        key = body.api_key.strip()
        if key:
            patch["api_key"] = key
        else:
            settings = load_settings()
            settings.pop("api_key", None)
            write_json(SETTINGS_PATH, settings)
    if body.lead_model:
        patch["lead_model"] = _pick(body.lead_model, KNOWN_MODELS, "grok-4.6")
    if body.lead_effort:
        patch["lead_effort"] = _pick(body.lead_effort, KNOWN_EFFORTS, "high")
    if body.worker_model:
        patch["worker_model"] = _pick(body.worker_model, KNOWN_MODELS, "grok-4.5")
    if body.worker_effort:
        patch["worker_effort"] = _pick(body.worker_effort, KNOWN_EFFORTS, "medium")
    if body.worker_count is not None:
        patch["worker_count"] = clamp_workers(body.worker_count, 3)
    if patch:
        save_settings(patch)
    return await health()


@app.post("/api/crew/guide")
async def crew_guide(body: GuideIn) -> dict[str, Any]:
    text = (body.text or "").strip()
    if not text:
        raise HTTPException(400, "请输入指导")
    if not push_guidance(body.run_id, body.agent_id, text):
        raise HTTPException(409, "这一轮已经结束，无法再指导")
    return {"ok": True}


@app.post("/api/crew/answer")
async def crew_answer(body: AskIn) -> dict[str, Any]:
    text = (body.text or "").strip()
    if not text:
        raise HTTPException(400, "请选择或输入一项")
    if not resolve_ask(body.run_id, text):
        raise HTTPException(409, "没有等待中的选择")
    return {"ok": True}


@app.get("/api/conversations")
async def list_conversations() -> dict[str, Any]:
    web = [public_conversation(x) for x in load_conversations()]
    cli = list_cli_summaries()
    seen = {item["id"] for item in web}
    items = web + [item for item in cli if item["id"] not in seen]
    items.sort(key=lambda x: x.get("updated_at") or "", reverse=True)
    return {"conversations": items}


@app.post("/api/conversations")
async def create_conversation() -> dict[str, Any]:
    item = {
        "id": str(uuid.uuid4()),
        "title": "新对话",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "model": "grok-4.6",
        "previous_response_id": None,
        "messages": [],
    }
    upsert_conversation(item)
    return item


@app.get("/api/conversations/{cid}")
async def read_conversation(cid: str) -> dict[str, Any]:
    return get_conversation(cid)


@app.patch("/api/conversations/{cid}")
async def patch_conversation(cid: str, body: ConversationPatch) -> dict[str, Any]:
    item = get_conversation(cid)
    if body.title is not None:
        title = body.title.strip() or "新对话"
        item["title"] = title[:80]
        item["updated_at"] = now_iso()
    if body.truncate_before:
        msgs = item.get("messages") or []
        idx = next((i for i, msg in enumerate(msgs) if msg.get("id") == body.truncate_before), None)
        if idx is None:
            raise HTTPException(400, "找不到要回退的消息")
        if msgs[idx].get("source") == "cli":
            raise HTTPException(400, "不能改写 CLI 原对话")
        item["messages"] = msgs[:idx]
        item["previous_response_id"] = None
        item["updated_at"] = now_iso()
    upsert_conversation(item)
    return item


@app.delete("/api/conversations/{cid}")
async def delete_conversation(cid: str) -> dict[str, Any]:
    if is_cli_id(cid):
        path = CONTINUATIONS / f"{cli_sid(cid)}.json"
        if path.exists():
            path.unlink()
        return {"ok": True, "kept_cli": True}
    items = [x for x in load_conversations() if x["id"] != cid]
    save_conversations(items)
    return {"ok": True}


@app.post("/api/upload")
async def upload(file: UploadFile = File(...)) -> dict[str, Any]:
    filename = Path(file.filename or "upload.bin").name
    data = await file.read()
    if not data:
        raise HTTPException(400, "空文件")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(400, "文件不能超过 48 MB")

    local_id = str(uuid.uuid4())
    dest = UPLOADS / f"{local_id}__{filename}"
    dest.write_bytes(data)
    kind = guess_kind(filename, file.content_type)
    mime = (file.content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream").split(";")[0]
    record = {
        "id": local_id,
        "name": filename,
        "kind": kind,
        "mime": mime,
        "size": len(data),
        "path": str(dest),
        "remote_id": None,
        "created_at": now_iso(),
    }
    meta_path = dest.with_suffix(dest.suffix + ".meta.json")
    write_json(meta_path, record)
    return {
        "id": local_id,
        "name": filename,
        "kind": kind,
        "mime": mime,
        "size": len(data),
        "url": f"/api/files/{local_id}",
    }


def find_upload(local_id: str) -> tuple[Path, dict[str, Any]]:
    matches = list(UPLOADS.glob(f"{local_id}__*"))
    matches = [p for p in matches if not p.name.endswith(".meta.json")]
    if not matches:
        raise HTTPException(404, "文件不存在")
    path = matches[0]
    meta = read_json(path.with_suffix(path.suffix + ".meta.json"), {})
    return path, meta


@app.get("/api/files/{local_id}")
async def serve_file(local_id: str) -> FileResponse:
    path, meta = find_upload(local_id)
    filename = meta.get("name") or path.name.split("__", 1)[-1]
    mime = meta.get("mime") or mimetypes.guess_type(filename)[0] or "application/octet-stream"
    return FileResponse(path, media_type=mime, filename=filename)


async def build_user_content(
    token: str, text: str, file_ids: list[str]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    content: list[dict[str, Any]] = []
    public_files: list[dict[str, Any]] = []
    for fid in file_ids:
        path, meta = find_upload(fid)
        name = meta.get("name") or path.name.split("__", 1)[-1]
        kind = meta.get("kind") or guess_kind(name, meta.get("mime"))
        mime = meta.get("mime") or mimetypes.guess_type(name)[0] or "application/octet-stream"
        public = {
            "id": fid,
            "name": name,
            "kind": kind,
            "mime": mime,
            "url": f"/api/files/{fid}",
        }
        public_files.append(public)
        if kind == "image" and mime in {"image/jpeg", "image/jpg", "image/png"}:
            content.append({"type": "input_image", "image_url": file_to_data_url(path, mime)})
        else:
            remote_id = meta.get("remote_id")
            if not remote_id:
                remote_id = await upload_remote_file(token, path, name)
                meta["remote_id"] = remote_id
                write_json(path.with_suffix(path.suffix + ".meta.json"), meta)
            content.append({"type": "input_file", "file_id": remote_id})
    if text.strip():
        content.insert(0, {"type": "input_text", "text": text.strip()})
    elif not content:
        content.append({"type": "input_text", "text": "请看我上传的文件。"})
    return content, public_files


def sse(event: dict[str, Any]) -> bytes:
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n".encode("utf-8")


def async_client(**kwargs) -> httpx.AsyncClient:
    try:
        return httpx.AsyncClient(trust_env=True, **kwargs)
    except ImportError:
        return httpx.AsyncClient(trust_env=False, **kwargs)


def extract_error_message(raw: str) -> str:
    try:
        data = json.loads(raw)
        err = data.get("error")
        if isinstance(err, dict):
            return str(err.get("message") or raw)
        if isinstance(err, str):
            return err
    except json.JSONDecodeError:
        pass
    return raw[:500] or "请求失败"


def extract_output_text(data: dict[str, Any]) -> str:
    chunks: list[str] = []
    for item in data.get("output") or []:
        if not isinstance(item, dict):
            continue
        if item.get("type") == "message":
            for part in item.get("content") or []:
                if isinstance(part, dict) and part.get("type") == "output_text":
                    chunks.append(str(part.get("text") or ""))
        if item.get("type") == "output_text" and item.get("text"):
            chunks.append(str(item["text"]))
    return visible_answer("".join(chunks) or str(data.get("output_text") or ""))


def _fallback_model(model: str) -> str | None:
    if model in {"grok-4.3", "grok-4.5"}:
        return "grok-4.6" if model == "grok-4.5" else "grok-4.5"
    return None


def _soften_effort(effort: str) -> str:
    return "high" if effort == "xhigh" else effort


async def xai_complete(
    token: str, model: str, effort: str, messages: list[dict[str, Any]], tools: bool = False
) -> str:
    payload: dict[str, Any] = {
        "model": model,
        "stream": False,
        "store": False,
        "reasoning": {"effort": effort},
        "input": messages,
    }
    if tools:
        payload["tools"] = list(DEFAULT_TOOLS)
    async with async_client(timeout=httpx.Timeout(3600.0, connect=30.0)) as client:
        resp = await client.post(
            f"{XAI_BASE}/responses",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json=payload,
        )
    if resp.status_code >= 400:
        msg = extract_error_message(resp.text)
        log.warning("xai_complete %s %s failed: %s", model, effort, msg)
        alt = _fallback_model(model)
        if effort == "xhigh":
            return await xai_complete(token, model, "high", messages, tools)
        if alt:
            return await xai_complete(token, alt, _soften_effort(effort), messages, tools)
        raise HTTPException(resp.status_code, msg)
    return extract_output_text(resp.json())


async def xai_stream(token: str, payload: dict[str, Any], restarts: int = 0):
    collected: list[str] = []
    visible_len = 0
    activity: list[dict[str, Any]] = []
    response_id = None
    stalled = False
    dropped = False
    try:
        async with async_client(timeout=httpx.Timeout(3600.0, connect=30.0)) as client:
            async with client.stream(
                "POST",
                f"{XAI_BASE}/responses",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json=payload,
            ) as resp:
                if resp.status_code >= 400:
                    raw = (await resp.aread()).decode("utf-8", errors="replace")
                    msg = extract_error_message(raw)
                    log.warning("xai_stream %s failed: %s", payload.get("model"), msg)
                    model = str(payload.get("model") or "")
                    effort = ""
                    reasoning = payload.get("reasoning")
                    if isinstance(reasoning, dict):
                        effort = str(reasoning.get("effort") or "")
                    if effort == "xhigh":
                        payload = {**payload, "reasoning": {"effort": "high"}}
                        async for ev in xai_stream(token, payload, restarts=restarts):
                            yield ev
                        return
                    alt = _fallback_model(model)
                    if alt:
                        nxt = {**payload, "model": alt}
                        if effort == "xhigh":
                            nxt["reasoning"] = {"effort": "high"}
                        async for ev in xai_stream(token, nxt, restarts=restarts):
                            yield ev
                        return
                    yield {"type": "error", "message": msg}
                    return
                buffer = ""
                async for chunk in resp.aiter_text():
                    buffer += chunk
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        line = line.strip()
                        if not line.startswith("data:"):
                            continue
                        data_str = line[5:].strip()
                        if not data_str or data_str == "[DONE]":
                            continue
                        try:
                            event = json.loads(data_str)
                        except json.JSONDecodeError:
                            continue
                        etype = event.get("type") or ""
                        if etype == "response.output_text.delta":
                            delta = event.get("delta") or ""
                            if delta:
                                collected.append(delta)
                                visible = visible_answer("".join(collected))
                                if loop_detected(visible):
                                    stalled = True
                                    break
                                if len(visible) > visible_len:
                                    yield {"type": "delta", "text": visible[visible_len:]}
                                    visible_len = len(visible)
                        elif etype == "response.completed":
                            response = event.get("response") or {}
                            response_id = response.get("id") or event.get("id")
                            for entry in harvest_activity(event):
                                activity.append(entry)
                                yield {"type": "activity", "entry": entry}
                        elif etype in {"response.failed", "error"}:
                            err = event.get("error") or event.get("response") or event
                            message = ""
                            if isinstance(err, dict):
                                inner = err.get("error")
                                if isinstance(inner, dict):
                                    message = str(inner.get("message") or "")
                                else:
                                    message = str(err.get("message") or err)
                            else:
                                message = str(err)
                            yield {"type": "error", "message": message or "生成失败"}
                            return
                        else:
                            item = event.get("item") or {}
                            note = tool_status(etype, str(item.get("type") or ""))
                            if note:
                                yield {"type": "status", "text": note}
                            for entry in harvest_activity(event):
                                activity.append(entry)
                                yield {"type": "activity", "entry": entry}
                    if stalled:
                        break
    except Exception as exc:
        if not is_drop_error(exc):
            log.warning("xai_stream exception: %s", exc)
            yield {"type": "error", "message": str(exc)}
            return
        kept = visible_answer("".join(collected))
        log.warning("xai_stream dropped: %s (kept %s chars)", exc, len(kept))
        if looks_complete(kept) and not loop_detected(kept):
            yield {"type": "done", "text": kept, "response_id": response_id, "activity": compact_activity(activity)}
            return
        dropped = True
    if stalled or dropped:
        rec = next_recovery(payload, restarts)
        if rec:
            label = rec["label"]
            if dropped:
                label = (
                    "连接中断，正在重试"
                    if restarts == 0
                    else "连接仍不稳，换模型再试"
                    if restarts == 1
                    else "连接仍不稳，缩小任务再试"
                )
            yield {"type": "status", "text": label}
            yield {"type": "reset"}
            async for ev in xai_stream(token, rec["payload"], restarts=restarts + 1):
                yield ev
            return
        kept = trim_loop("".join(collected)) if stalled else visible_answer("".join(collected))
        yield {"type": "reset"}
        if kept:
            yield {"type": "delta", "text": kept}
        yield {
            "type": "done",
            "text": kept or ("连接中断，已停止。请再试一次。" if dropped else "这一轮陷入空转，已停止。请再试一次。"),
            "response_id": response_id,
            "activity": compact_activity(activity),
            "stalled": True,
        }
        return
    full = visible_answer("".join(collected))
    yield {"type": "done", "text": full, "response_id": response_id, "activity": compact_activity(activity)}


DEFAULT_ROLES = [
    ("research", "调研", "搜集事实、背景和可核对的来源"),
    ("analysis", "分析", "基于已有材料分析要点、分歧和结论"),
    ("write", "成文", "把已有成果整理成可读回答"),
    ("review", "校对", "核对事实、补缺口、标出不确定处"),
    ("expand", "展开", "补充例子、反例和可执行建议"),
    ("cite", "核源", "交叉验证关键论断和出处"),
]


def _clean_id(value: Any, fallback: str) -> str:
    aid = re.sub(r"[^a-z0-9-]+", "", str(value or "").lower())
    return aid or fallback


def _parse_worker(item: dict[str, Any], idx: int, seen: set[str]) -> dict[str, Any]:
    aid = _clean_id(item.get("id"), f"agent-{idx + 1}")
    if aid in seen:
        aid = f"{aid}-{idx + 1}"
    seen.add(aid)
    deps: list[str] = []
    for dep in item.get("depends_on") or item.get("deps") or []:
        did = _clean_id(dep, "")
        if did and did != aid and did not in deps:
            deps.append(did)
    return {
        "id": aid,
        "name": str(item.get("name") or aid)[:24],
        "brief": str(item.get("brief") or item.get("task") or "")[:500],
        "depends_on": deps,
    }


def _pad_workers(agents: list[dict[str, Any]], target: int, seen: set[str]) -> list[dict[str, Any]]:
    while len(agents) < target:
        i = len(agents)
        rid, name, brief = DEFAULT_ROLES[i] if i < len(DEFAULT_ROLES) else (f"agent-{i + 1}", f"专员 {i + 1}", "推进尚未覆盖的部分")
        if rid in seen:
            rid = f"{rid}-{i + 1}"
        seen.add(rid)
        agents.append({"id": rid, "name": name, "brief": brief, "depends_on": []})
    return agents[:target]


def _steps_from_agents(agents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    independent = [a for a in agents if not a.get("depends_on")]
    dependent = [a for a in agents if a.get("depends_on")]
    steps: list[dict[str, Any]] = []
    if independent:
        steps.append(
            {
                "id": "explore",
                "name": "并行探索",
                "brief": "互不阻塞的工作同时推进",
                "depends_on": [],
                "agents": independent,
            }
        )
    if dependent:
        steps.append(
            {
                "id": "follow",
                "name": "衔接推进",
                "brief": "读取前序进度后并行落实",
                "depends_on": ["explore"] if independent else [],
                "agents": dependent,
            }
        )
    if not steps and agents:
        steps.append({"id": "main", "name": "并行推进", "brief": "", "depends_on": [], "agents": agents})
    return steps


def _normalize_steps(data: dict[str, Any], agents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    raw_steps = data.get("steps") if isinstance(data.get("steps"), list) else []
    if not raw_steps:
        return _steps_from_agents(agents)
    seen: set[str] = set()
    steps: list[dict[str, Any]] = []
    leftover = {a["id"]: a for a in agents}
    for i, item in enumerate(raw_steps[:6]):
        if not isinstance(item, dict):
            continue
        sid = _clean_id(item.get("id"), f"step-{i + 1}")
        workers: list[dict[str, Any]] = []
        for j, raw in enumerate(item.get("agents") or []):
            if not isinstance(raw, dict):
                continue
            worker = leftover.pop(_clean_id(raw.get("id"), ""), None)
            if worker is None:
                worker = _parse_worker(raw, len(agents) + j, seen)
            workers.append(worker)
        deps = []
        for dep in item.get("depends_on") or []:
            did = _clean_id(dep, "")
            if did and did != sid and did not in deps:
                deps.append(did)
        if workers:
            steps.append(
                {
                    "id": sid,
                    "name": str(item.get("name") or sid)[:24],
                    "brief": str(item.get("brief") or "")[:400],
                    "depends_on": deps,
                    "agents": workers,
                }
            )
    used = {w["id"] for s in steps for w in s["agents"]}
    extras = [a for a in agents if a["id"] not in used]
    if extras:
        if steps:
            steps[0]["agents"].extend(extras)
        else:
            steps = _steps_from_agents(extras)
    ids = {s["id"] for s in steps}
    for step in steps:
        step["depends_on"] = [d for d in step.get("depends_on") or [] if d in ids and d != step["id"]]
    return steps or _steps_from_agents(agents)


def parse_plan(raw: str, count: int | None = None) -> dict[str, Any]:
    blob = re.search(r"\{[\s\S]*\}", strip_tool_leak(raw) or "")
    data: dict[str, Any] = {}
    if blob:
        try:
            parsed = json.loads(blob.group(0))
            if isinstance(parsed, dict):
                data = parsed
        except json.JSONDecodeError:
            data = {}
    wanted = clamp_workers(count, 0) if count is not None else 0
    agents: list[dict[str, Any]] = []
    seen: set[str] = set()
    cap = wanted or 6
    for i, item in enumerate((data.get("agents") or [])[:cap]):
        if isinstance(item, dict):
            agents.append(_parse_worker(item, i, seen))
    if not agents:
        for i, item in enumerate((data.get("steps") or [])[:6]):
            if not isinstance(item, dict):
                continue
            for raw in item.get("agents") or []:
                if isinstance(raw, dict):
                    agents.append(_parse_worker(raw, len(agents), seen))
    if wanted:
        agents = agents[:wanted]
    if len(agents) < 2:
        agents = _pad_workers(agents, 2, seen)
    ids = {a["id"] for a in agents}
    for agent in agents:
        agent["depends_on"] = [d for d in agent.get("depends_on") or [] if d in ids and d != agent["id"]]
    if agents and all(not a["depends_on"] for a in agents) and len(agents) >= 2 and not data.get("steps"):
        split = max(2, (len(agents) + 1) // 2)
        first = [a["id"] for a in agents[:split]]
        for agent in agents[split:]:
            agent["depends_on"] = list(first)
    steps = _normalize_steps(data, agents)
    flat = [w for s in steps for w in s["agents"]]
    return {"lead": str(data.get("lead") or "拆成可并行对齐的步骤")[:400], "agents": flat or agents, "steps": steps}


def _is_reviewer(spec: dict[str, Any]) -> bool:
    blob = f"{spec.get('id') or ''} {spec.get('name') or ''} {spec.get('brief') or ''}".lower()
    return any(key in blob for key in ("review", "校对", "审核", "评审", "critic"))


def parse_feedback(raw: str) -> list[dict[str, str]]:
    blob = re.search(r"\{[\s\S]*\}", strip_tool_leak(raw) or "")
    if not blob:
        return []
    try:
        data = json.loads(blob.group(0))
    except json.JSONDecodeError:
        return []
    items = data.get("feedback") or data.get("send_back") or []
    out: list[dict[str, str]] = []
    if not isinstance(items, list):
        return out
    for item in items[:8]:
        if not isinstance(item, dict):
            continue
        ask = str(item.get("ask") or item.get("need") or item.get("message") or "").strip()
        to = str(item.get("to") or item.get("agent") or "").strip()
        if ask and to:
            out.append({"to": to, "ask": ask[:400]})
    return merge_feedback(out)


def parse_review(raw: str) -> dict[str, Any]:
    blob = re.search(r"\{[\s\S]*\}", strip_tool_leak(raw) or "")
    data: dict[str, Any] = {}
    if blob:
        try:
            parsed = json.loads(blob.group(0))
            if isinstance(parsed, dict):
                data = parsed
        except json.JSONDecodeError:
            data = {}
    passed = data.get("pass")
    if passed is None:
        passed = data.get("ok")
    issues = data.get("issues") if isinstance(data.get("issues"), list) else []
    return {
        "pass": bool(passed) if passed is not None else not bool(issues),
        "explicit_pass": passed is not None,
        "issues": [str(x)[:240] for x in issues[:8]],
        "feedback": parse_feedback(raw),
        "notes": str(data.get("notes") or data.get("summary") or "")[:500],
    }


def parse_rework(raw: str) -> dict[str, Any]:
    blob = re.search(r"\{[\s\S]*\}", strip_tool_leak(raw) or "")
    data: dict[str, Any] = {}
    if blob:
        try:
            parsed = json.loads(blob.group(0))
            if isinstance(parsed, dict):
                data = parsed
        except json.JSONDecodeError:
            data = {}
    assigns: list[dict[str, str]] = []
    for item in (data.get("assigns") or data.get("tasks") or [])[:6]:
        if not isinstance(item, dict):
            continue
        aid = _clean_id(item.get("id"), "")
        brief = str(item.get("brief") or item.get("ask") or "").strip()
        if aid and brief:
            assigns.append({"id": aid, "brief": brief[:400]})
    reuse = []
    for item in data.get("reuse") or []:
        rid = _clean_id(item, "")
        if rid:
            reuse.append(rid)
    return {
        "rework": bool(data.get("rework") or data.get("continue") or assigns),
        "explicit": "rework" in data or "continue" in data,
        "notes": str(data.get("notes") or "")[:500],
        "reuse": reuse,
        "assigns": assigns,
    }


class CrewState:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.phase = "planning"
        self.running: set[str] = set()
        self.sent_back: list[str] = []
        self.failed: set[str] = set()
        self.review_round = 0
        self.max_review = 2
        self.stop_reason: str | None = None
        self.plan_version = 1
        self.plan_notes: list[str] = ["v1: initial plan"]
        self.briefs: dict[str, str] = {}
        self.steers: list[dict[str, str]] = []
        self.acceptance: list[str] = []
        self.score: dict[str, Any] = {}

    def snapshot(self) -> dict[str, Any]:
        return {
            "type": "phase",
            "phase": self.phase,
            "running": sorted(self.running),
            "sent_back": list(self.sent_back)[-8:],
            "failed": sorted(self.failed),
            "review_round": self.review_round,
            "stop": self.stop_reason,
            "plan_version": self.plan_version,
            "score": dict(self.score),
        }

    def enter(self, phase: str, running: list[str] | None = None) -> dict[str, Any]:
        self.phase = phase
        self.running = set(running or [])
        return self.snapshot()

    def bump_plan(self, note: str) -> None:
        self.plan_version += 1
        self.plan_notes.append(f"v{self.plan_version}: {note.strip()[:200]}")

    def changelog_since(self, version: int) -> str:
        rows = [line for line in self.plan_notes if line.startswith("v")]
        later = []
        for line in self.plan_notes:
            try:
                num = int(line.split(":", 1)[0].lstrip("v"))
            except ValueError:
                continue
            if num > version:
                later.append(line)
        return "\n".join(later[-6:])

    def record_steer(self, aid: str, note: str) -> None:
        text = (note or "").strip()[:400]
        if not text:
            return
        self.bump_plan(f"human steered {aid}: {text[:160]}")
        prev = self.briefs.get(aid, "")
        self.briefs[aid] = (f"{prev}；" if prev else "") + f"[v{self.plan_version} 纠偏] {text}"
        self.steers.append({"agent": aid, "note": text, "version": str(self.plan_version)})
        if len(text) <= 40 and text not in self.acceptance:
            self.acceptance.append(text)

    def mark_sent_back(self, aid: str) -> None:
        if aid and aid not in self.sent_back:
            self.sent_back.append(aid)

    def mark_failed(self, aid: str) -> None:
        if aid:
            self.failed.add(aid)

    def stop(self, reason: str) -> dict[str, Any]:
        self.phase = "done" if reason == "done" else "stopped"
        self.running = set()
        self.stop_reason = reason
        return self.snapshot()


def token_set(text: str) -> set[str]:
    blob = (text or "").lower()
    tokens = set(re.findall(r"[A-Za-z][A-Za-z0-9+\-]{2,}|\d+(?:\.\d+)?", blob))
    chars = re.findall(r"[一-龥]", blob)
    for i in range(len(chars) - 1):
        tokens.add(chars[i] + chars[i + 1])
    return tokens


def token_overlap(left: str, right: str) -> float:
    a, b = token_set(left), token_set(right)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def find_conflicts(facts: list[dict[str, Any]]) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    neg = ("不是", "并非", "并不", "没有", "无法", "不能", "不支持", "相反", "冲突", " not ", " no ", "cannot", "unlike")
    pairs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    active = [item for item in facts if item.get("status") != "superseded"]
    for i, left in enumerate(active):
        for right in active[i + 1 :]:
            if left.get("owner_id") and left.get("owner_id") == right.get("owner_id"):
                continue
            if token_overlap(str(left.get("claim") or ""), str(right.get("claim") or "")) < 0.28:
                continue
            blob_l = f" {str(left.get('claim') or '').lower()} "
            blob_r = f" {str(right.get('claim') or '').lower()} "
            hit_l = any(key in blob_l or key in str(left.get("claim") or "") for key in neg)
            hit_r = any(key in blob_r or key in str(right.get("claim") or "") for key in neg)
            if hit_l != hit_r:
                pairs.append((left, right))
    return pairs[:8]


def pick_fact_winner(left: dict[str, Any], right: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]] | None:
    rank = {"high": 3, "medium": 2, "low": 1, "hypothesis": 0}
    ra = rank.get(str(left.get("confidence") or "medium"), 1)
    rb = rank.get(str(right.get("confidence") or "medium"), 1)
    if ra != rb:
        return (left, right) if ra > rb else (right, left)
    sa, sb = bool(left.get("source")), bool(right.get("source"))
    if sa != sb:
        return (left, right) if sa else (right, left)
    return None


def arbitrate_conflicts(facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    verdicts: list[dict[str, Any]] = []
    for left, right in find_conflicts(facts):
        if left.get("status") == "superseded" or right.get("status") == "superseded":
            continue
        picked = pick_fact_winner(left, right)
        if picked is None:
            left["status"] = "contested"
            right["status"] = "contested"
            verdicts.append(
                {
                    "claim": f"冲突未决：{str(left.get('claim') or '')[:80]} vs {str(right.get('claim') or '')[:80]}",
                    "source": "brain-arbitration",
                    "confidence": "hypothesis",
                    "for": [],
                    "owner": "总控",
                    "owner_id": "lead",
                    "status": "contested",
                }
            )
            continue
        winner, loser = picked
        loser["status"] = "superseded"
        winner["status"] = winner.get("status") or "active"
        verdicts.append(
            {
                "claim": str(winner.get("claim") or ""),
                "source": f"arbitrated over {loser.get('owner') or loser.get('owner_id')}",
                "confidence": str(winner.get("confidence") or "medium"),
                "for": list(winner.get("for") or []),
                "owner": "总控",
                "owner_id": "lead",
                "status": "active",
            }
        )
    return verdicts


def merge_feedback(items: list[dict[str, str]]) -> list[dict[str, str]]:
    clusters: list[dict[str, str]] = []
    for item in items:
        placed = False
        for cluster in clusters:
            if cluster.get("to") == item.get("to") and token_overlap(cluster.get("ask") or "", item.get("ask") or "") >= 0.4:
                extra = str(item.get("ask") or "")
                if extra and extra not in cluster["ask"]:
                    cluster["ask"] = f"{cluster['ask'][:180]} / {extra[:180]}"
                placed = True
                break
        if not placed:
            clusters.append({"to": str(item.get("to") or ""), "ask": str(item.get("ask") or "")[:400]})
    return [row for row in clusters if row["to"] and row["ask"]][:4]


def merge_asks(asks: list[dict[str, Any]]) -> dict[str, Any] | None:
    valid = [item for item in asks if item and item.get("question") and item.get("options")]
    if not valid:
        return None
    if len(valid) == 1:
        return valid[0]
    labels: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in valid:
        for opt in item.get("options") or []:
            key = str(opt.get("label") or "").strip().lower()
            if not key or key in seen:
                continue
            seen.add(key)
            labels.append(opt)
            if len(labels) >= 4:
                break
        if len(labels) >= 4:
            break
    if len(labels) < 2:
        return valid[0]
    q = "；".join(str(item.get("question") or "")[:80] for item in valid[:3])
    return {"question": q[:240], "options": labels[:4]}


def coverage_score(facts: list[dict[str, Any]], step_ids: list[str], acceptance: list[str] | None = None) -> dict[str, Any]:
    active = [item for item in facts if item.get("status") != "superseded"]
    n = max(len(active), 1)
    solid = sum(1 for item in active if item.get("confidence") in {"high", "medium"})
    covered = 0
    for sid in step_ids:
        key = str(sid or "").lower()
        if any(key == str(item.get("step") or "").lower() or key in [str(x).lower() for x in (item.get("for") or [])] for item in active):
            covered += 1
    cov = covered / max(len(step_ids), 1) if step_ids else solid / n
    blob = " ".join(str(item.get("claim") or "") for item in active).lower()
    checks = [str(x).strip() for x in (acceptance or []) if str(x).strip()]
    acc = 1.0 if not checks else sum(1 for item in checks if item.lower() in blob) / len(checks)
    return {
        "coverage": round(cov, 2),
        "confidence": round(solid / n, 2),
        "conflicts": len(find_conflicts(active)),
        "facts": len(active),
        "acceptance": round(acc, 2),
    }


def decide_review(
    review: dict[str, Any],
    raw: str,
    review_round: int,
    max_review: int = 2,
    score: dict[str, Any] | None = None,
) -> str:
    if review_round >= max_review:
        return "stop"
    score = score or {}
    conflicts = int(score.get("conflicts") or 0)
    cov = float(score.get("coverage") or 1)
    conf = float(score.get("confidence") or 1)
    acc = float(score.get("acceptance") or 1)
    if conflicts > 0:
        return "rework"
    if acc < 0.5:
        return "rework"
    complained = review.get("explicit_pass") is False or bool(review.get("issues")) or bool(review.get("feedback"))
    if complained:
        if review_round >= 1 and cov >= 0.8 and conf >= 0.6 and acc >= 0.5:
            return "pass"
        return "rework"
    if review.get("explicit_pass") is True and cov >= 0.34:
        return "pass"
    if cov >= 0.67 and conf >= 0.5:
        return "pass"
    blob = raw or ""
    low = blob.lower()
    if any(key in blob or key in low for key in ("打回", "不足", "缺口", "send back", "not ready", "missing", "incomplete", "不够")):
        return "rework"
    if any(key in blob or key in low for key in ("通过", "可以交", "足够", "lgtm", "looks good")):
        return "pass"
    if cov < 0.5:
        return "rework"
    return "pass"


def machine_assigns(
    review: dict[str, Any],
    roster: list[dict[str, Any]],
    completed: dict[str, dict[str, Any]],
    sent_back: list[str],
) -> list[dict[str, str]]:
    assigns: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in review.get("feedback") or []:
        target = resolve_agent(str(item.get("to") or ""), roster)
        if not target or target.get("role") in {"lead", "reviewer"}:
            continue
        aid = str(target["id"])
        if aid in seen:
            continue
        seen.add(aid)
        assigns.append({"id": aid, "brief": str(item.get("ask") or "补齐审核指出的缺口，只写要点")[:400]})
    if assigns:
        return assigns[:4]
    prefer = set(sent_back)
    for spec in roster:
        aid = str(spec.get("id") or "")
        if not aid or spec.get("role") in {"lead", "reviewer"}:
            continue
        rec = completed.get(aid) or {}
        if rec.get("status") in {"error", "partial"} or aid in prefer:
            if aid not in seen:
                seen.add(aid)
                assigns.append({"id": aid, "brief": "只补最关键的缺口，不超过 180 字"})
    if assigns:
        return assigns[:3]
    for spec in roster:
        if spec.get("role") == "worker" and spec.get("id"):
            return [{"id": str(spec["id"]), "brief": "用已有材料写一段最短结论，不要开新调研"}]
    return []


CREW_RUNS: dict[str, dict[str, Any]] = {}


def open_crew_run() -> str:
    run_id = uuid.uuid4().hex[:12]
    CREW_RUNS[run_id] = {"notes": {}, "alive": True}
    return run_id


def close_crew_run(run_id: str) -> None:
    run = CREW_RUNS.pop(run_id, None)
    if not run:
        return
    fut = run.get("ask_future")
    if fut and not fut.done():
        fut.cancel()


def push_guidance(run_id: str, agent_id: str, text: str) -> bool:
    run = CREW_RUNS.get(run_id)
    if not run or not run.get("alive"):
        return False
    aid = str(agent_id or "").strip()
    note = str(text or "").strip()[:800]
    if not aid or not note:
        return False
    run["notes"].setdefault(aid, []).append(note)
    machine = run.get("machine")
    if isinstance(machine, CrewState):
        machine.record_steer(aid, note)
    return True


def take_guidance(run_id: str, agent_id: str) -> list[str]:
    run = CREW_RUNS.get(run_id)
    if not run:
        return []
    return list(run["notes"].pop(agent_id, []) or [])


def peek_guidance_ids(run_id: str) -> list[str]:
    run = CREW_RUNS.get(run_id)
    if not run:
        return []
    return [key for key, val in run["notes"].items() if val]


def parse_ask(raw: str) -> dict[str, Any] | None:
    blob = re.search(r"\{[\s\S]*\}", strip_tool_leak(raw) or "")
    if not blob:
        return None
    try:
        data = json.loads(blob.group(0))
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    if "steps" in data or ("agents" in data and "ask" not in data and "question" not in data):
        return None
    ask = data.get("ask") if isinstance(data.get("ask"), dict) else data
    question = str(ask.get("question") or ask.get("q") or "").strip()
    raw_opts = ask.get("options") or ask.get("choices") or []
    if not question or not isinstance(raw_opts, list):
        return None
    options: list[dict[str, str]] = []
    for i, item in enumerate(raw_opts[:4]):
        if isinstance(item, str) and item.strip():
            options.append({"id": chr(97 + i), "label": item.strip()[:80], "desc": ""})
            continue
        if not isinstance(item, dict):
            continue
        label = str(item.get("label") or item.get("text") or item.get("title") or "").strip()
        if not label:
            continue
        oid = _clean_id(item.get("id"), chr(97 + i))
        options.append({"id": oid, "label": label[:80], "desc": str(item.get("desc") or item.get("description") or "")[:160]})
    if len(options) < 2:
        return None
    return {"question": question[:240], "options": options}


def strip_ask_json(raw: str) -> str:
    text = strip_tool_leak(raw) or ""
    blob = re.search(r"\{[\s\S]*\}", text)
    if blob and parse_ask(blob.group(0)):
        return (text[: blob.start()] + text[blob.end() :]).strip()
    return text.strip()


async def wait_user_choice(run_id: str, timeout: float = 900.0) -> str | None:
    run = CREW_RUNS.get(run_id)
    if not run or not run.get("alive"):
        return None
    loop = asyncio.get_running_loop()
    fut: asyncio.Future = loop.create_future()
    run["ask_future"] = fut
    try:
        return await asyncio.wait_for(asyncio.shield(fut), timeout=timeout)
    except asyncio.TimeoutError:
        return None
    finally:
        if run.get("ask_future") is fut:
            run.pop("ask_future", None)


def resolve_ask(run_id: str, text: str) -> bool:
    run = CREW_RUNS.get(run_id)
    if not run:
        return False
    fut = run.get("ask_future")
    note = str(text or "").strip()[:800]
    if not note or not fut or fut.done():
        return False
    fut.set_result(note)
    return True


def attach_human_notes(payload: dict[str, Any], notes: list[str]) -> dict[str, Any]:
    extra = "\n".join(f"- {item}" for item in notes if str(item).strip())
    if not extra:
        return payload
    inputs = []
    for msg in payload.get("input") or []:
        if isinstance(msg, dict) and msg.get("role") == "user":
            inputs.append(
                {
                    **msg,
                    "content": f"{msg.get('content') or ''}\n\nHuman guidance — follow this now and adjust your direction:\n{extra}",
                }
            )
        else:
            inputs.append(msg)
    return {**payload, "input": inputs}


def resolve_agent(to: str, roster: list[dict[str, Any]]) -> dict[str, Any] | None:
    key = (to or "").strip().lower()
    if not key:
        return None
    cid = _clean_id(to, "")
    for spec in roster:
        if spec.get("id") == cid:
            return spec
    for spec in roster:
        name = str(spec.get("name") or "").lower()
        if key in name or key in str(spec.get("id") or ""):
            return spec
    return None


def plan_waves(agents: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    remaining = {a["id"]: a for a in agents}
    done: set[str] = set()
    waves: list[list[dict[str, Any]]] = []
    while remaining:
        ready = [a for a in remaining.values() if all(d in done for d in (a.get("depends_on") or []))]
        if not ready:
            ready = list(remaining.values())
        waves.append(ready)
        for agent in ready:
            remaining.pop(agent["id"], None)
            done.add(agent["id"])
    return waves


def report_digest(report: dict[str, Any]) -> str:
    text = re.sub(r"\s+", " ", str(report.get("content") or "").strip())
    if not text:
        return "（尚无产出）"
    return text[:280] + ("…" if len(text) > 280 else "")


def pack_ledger(reports: dict[str, dict[str, Any]]) -> tuple[str, list[dict[str, str]]]:
    entries: list[dict[str, str]] = []
    lines: list[str] = []
    for report in reports.values():
        note = report_digest(report)
        name = str(report.get("name") or report.get("id") or "代理")
        entries.append({"id": str(report.get("id") or ""), "name": name, "note": note, "status": str(report.get("status") or "done")})
        lines.append(f"- {name}: {note}")
    return ("\n".join(lines) if lines else "（进度板还是空的）"), entries


def parse_facts(raw: str) -> list[dict[str, Any]]:
    blob = re.search(r"\{[\s\S]*\}", strip_tool_leak(raw) or "")
    if not blob:
        return []
    try:
        data = json.loads(blob.group(0))
    except json.JSONDecodeError:
        return []
    if not isinstance(data, dict):
        return []
    items = data.get("facts") or data.get("claims") or []
    if not isinstance(items, list):
        return []
    out: list[dict[str, Any]] = []
    allowed = {"high", "medium", "low", "hypothesis"}
    for item in items[:12]:
        if isinstance(item, str) and item.strip():
            out.append({"claim": item.strip()[:400], "source": "", "confidence": "hypothesis", "for": []})
            continue
        if not isinstance(item, dict):
            continue
        claim = str(item.get("claim") or item.get("fact") or item.get("text") or "").strip()
        if not claim:
            continue
        conf = str(item.get("confidence") or item.get("conf") or "medium").strip().lower()
        if conf not in allowed:
            conf = "medium"
        targets = []
        for raw_for in item.get("for") or item.get("steps") or []:
            tag = str(raw_for or "").strip()
            if tag and tag not in targets:
                targets.append(tag[:40])
        out.append(
            {
                "claim": claim[:400],
                "source": str(item.get("source") or item.get("cite") or "").strip()[:240],
                "confidence": conf,
                "for": targets,
            }
        )
    return out


def harvest_facts(report: dict[str, Any]) -> list[dict[str, Any]]:
    facts = parse_facts(str(report.get("content") or ""))
    owner = str(report.get("name") or report.get("id") or "代理")
    owner_id = str(report.get("id") or "")
    step = str(report.get("step") or "")
    out = []
    for item in facts:
        out.append({**item, "owner": owner, "owner_id": owner_id, "step": step, "status": item.get("status") or "active"})
    return out


def commit_facts(board: list[dict[str, Any]], report: dict[str, Any]) -> list[dict[str, Any]]:
    aid = str(report.get("id") or "")
    board[:] = [
        item
        for item in board
        if item.get("owner_id") != aid
        and str(item.get("source") or "") != "brain-arbitration"
        and not str(item.get("source") or "").startswith("arbitrated over")
    ]
    board.extend(harvest_facts(report))
    for item in board:
        if item.get("status") in {"superseded", "contested"}:
            item["status"] = "active"
    board.extend(arbitrate_conflicts(board))
    return board


def apply_user_choice(machine: CrewState, board: list[dict[str, Any]], choice: str, note: str) -> None:
    text = (choice or "").strip()
    if not text:
        return
    machine.bump_plan(f"{note}: {text[:160]}")
    short = text[:80]
    if short not in machine.acceptance:
        machine.acceptance.append(short)
    board.append(
        {
            "claim": f"用户选定：{text[:200]}",
            "source": "user-decision",
            "confidence": "high",
            "for": [],
            "owner": "用户",
            "owner_id": "user",
            "status": "active",
        }
    )


def collect_merged_ask(texts: list[str]) -> dict[str, Any] | None:
    asks = []
    for text in texts:
        item = parse_ask(text)
        if item:
            asks.append(item)
    return merge_asks(asks)


def filter_facts(facts: list[dict[str, Any]], viewer: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    facts = [item for item in facts if item.get("status") != "superseded"]
    if not viewer:
        return list(facts)
    sid = str(viewer.get("step") or "").lower()
    role = str(viewer.get("role") or "").lower()
    name = str(viewer.get("name") or "").lower()
    bid = str(viewer.get("id") or "").lower()
    writer = any(key in f"{name}{bid}{role}" for key in ("write", "成文", "整合", "综述"))
    out: list[dict[str, Any]] = []
    for item in facts:
        if item.get("status") == "superseded":
            continue
        targets = [str(x).lower() for x in (item.get("for") or [])]
        conf = str(item.get("confidence") or "medium")
        if not targets:
            if conf in {"high", "medium"}:
                out.append(item)
            continue
        if sid and sid in targets:
            out.append(item)
            continue
        if role and role in targets:
            out.append(item)
            continue
        if any(tag in name or tag in bid or name in tag or bid in tag for tag in targets):
            out.append(item)
            continue
        if writer and conf == "high":
            out.append(item)
    return out[:16]


def format_contract(facts: list[dict[str, Any]], viewer: dict[str, Any] | None = None) -> str:
    rows = filter_facts(facts, viewer)
    if not rows:
        return "（没有与你相关的已登记条目。不要把空板当成许可去猜。）"
    lines = [
        "CONTRACT — read-only evidence. Hypothesis is not fact. Do not change the immutable goal."
    ]
    for item in rows:
        src = item.get("source") or "未标注出处"
        owner = item.get("owner") or "未知"
        mark = " [contested]" if item.get("status") == "contested" else ""
        lines.append(f"- [{item.get('confidence')}] {item.get('claim')}{mark} （{src}；{owner}）")
    return "\n".join(lines)


def pack_contract_ledger(facts: list[dict[str, Any]]) -> tuple[str, list[dict[str, str]]]:
    text = format_contract(facts)
    entries: list[dict[str, str]] = []
    visible = [item for item in facts if item.get("status") != "superseded"]
    for item in visible[-24:]:
        tag = item.get("status") if item.get("status") in {"contested"} else item.get("confidence")
        entries.append(
            {
                "id": str(item.get("owner_id") or ""),
                "name": str(item.get("owner") or "条目"),
                "note": f"[{tag}] {str(item.get('claim') or '')[:200]}",
                "status": str(item.get("status") or item.get("confidence") or ""),
            }
        )
    return text, entries


def _agent_view(spec: dict[str, Any], **extra: Any) -> dict[str, Any]:
    view = {
        "id": spec.get("id") or extra.get("id") or "agent",
        "name": spec.get("name") or extra.get("name") or spec.get("id") or "代理",
        "brief": spec.get("brief") or extra.get("brief") or "",
        "role": extra.get("role") or spec.get("role") or "worker",
        "status": extra.get("status") or spec.get("status") or "queued",
        "content": extra.get("content") if "content" in extra else spec.get("content") or "",
        "activity": extra.get("activity") if "activity" in extra else list(spec.get("activity") or []),
        "model": extra.get("model") or spec.get("model") or "",
        "effort": extra.get("effort") or spec.get("effort") or "",
        "depends_on": list(extra.get("depends_on") if "depends_on" in extra else spec.get("depends_on") or []),
        "step": extra.get("step") or spec.get("step") or "",
        "step_name": extra.get("step_name") or spec.get("step_name") or "",
    }
    feedback = extra.get("feedback") if "feedback" in extra else spec.get("feedback")
    if feedback:
        view["feedback"] = feedback
    guidance = extra.get("guidance") if "guidance" in extra else spec.get("guidance")
    if guidance:
        view["guidance"] = guidance
    return view


async def run_crew(token: str, question: str, cfg: dict[str, Any], history: str = ""):
    lead_model = cfg.get("lead_model") or "grok-4.6"
    lead_effort = cfg.get("lead_effort") or "high"
    worker_model = cfg.get("worker_model") or "grok-4.5"
    worker_effort = cfg.get("worker_effort") or "medium"
    worker_count = clamp_workers(cfg.get("worker_count"), 3)
    run_id = open_crew_run()
    machine = CrewState(run_id)
    CREW_RUNS[run_id]["machine"] = machine
    human_lead_notes: list[str] = []
    running_ids: set[str] = set()
    fact_board: list[dict[str, Any]] = []
    yield {"type": "crew-run", "run_id": run_id}
    yield machine.enter("planning", ["lead"])

    plan_effort = _soften_effort(lead_effort)
    yield {"type": "status", "text": "总控正在拆任务并对齐依赖…"}
    yield {
        "type": "agent",
        "agent": _agent_view(
            {"id": "lead", "name": "总控"},
            role="lead",
            status="planning",
            model=lead_model,
            effort=plan_effort,
        ),
    }
    brief = question
    if history:
        brief = f"Prior conversation:\n{history}\n\nCurrent request:\n{question}"
    plan_raw = ""
    plan_payload = {
        "model": lead_model,
        "stream": True,
        "store": False,
        "reasoning": {"effort": plan_effort},
        "input": [
            {
                "role": "system",
                "content": (
                    f"You are the lead orchestrator. Split the request into 2-4 STEPS. "
                    "Independent steps run at the same time. A step may have several specialist workers in parallel, "
                    "plus a step lead who aligns their progress. "
                    f"Use at most {worker_count} specialist workers (not counting leads or the reviewer). "
                    "Use fewer when the task does not need that many. Use at least 2. "
                    "Include one reviewer when the work can be checked; the reviewer may send incomplete work back to you. "
                    "Workers must route uncertainty to the right specialist instead of guessing. "
                    "Only use depends_on when a step truly cannot start without another step's output. "
                    "If the request is too ambiguous to plan without guessing, reply with ONLY "
                    '{"ask":{"question":"...","options":[{"id":"a","label":"...","desc":"..."}]}} '
                    "and 2-4 options (no Other). Otherwise reply with ONLY JSON: "
                    '{"lead":"one-line plan","steps":[{"id":"explore","name":"调研","brief":"...","depends_on":[],'
                    '"agents":[{"id":"algo","name":"算法","brief":"..."}]}],'
                    '"agents":[{"id":"algo","name":"算法","brief":"...","depends_on":[]}]} '
                    "No markdown."
                ),
            },
            {"role": "user", "content": brief},
        ],
    }
    try:
        async for ev in xai_stream(token, plan_payload):
            if ev["type"] == "delta":
                plan_raw += ev.get("text") or ""
            elif ev["type"] == "done":
                plan_raw = ev.get("text") or plan_raw
            elif ev["type"] == "error":
                log.warning("crew plan failed: %s", ev.get("message"))
                yield {"type": "status", "text": "规划未完成，改用默认分工继续"}
                plan_raw = ""
                break
    except Exception as exc:
        log.warning("crew plan exception: %s", exc)
        yield {"type": "status", "text": "规划未完成，改用默认分工继续"}
        plan_raw = ""
    plan_ask = parse_ask(plan_raw)
    if plan_ask:
        yield machine.enter("asking", ["lead"])
        yield {"type": "status", "text": "总控需要你选一下方向"}
        yield {"type": "ask", "run_id": run_id, **plan_ask}
        choice = await wait_user_choice(run_id)
        if choice:
            apply_user_choice(machine, fact_board, choice, "user chose plan direction")
            brief = f"{brief}\n\nUser decision:\n{choice}"
            yield {"type": "status", "text": "已按你的选择重新拆任务"}
            plan_payload["input"][-1] = {"role": "user", "content": brief}
            plan_raw = ""
            try:
                async for ev in xai_stream(token, plan_payload):
                    if ev["type"] == "delta":
                        plan_raw += ev.get("text") or ""
                    elif ev["type"] == "done":
                        plan_raw = ev.get("text") or plan_raw
                    elif ev["type"] == "error":
                        log.warning("crew replan failed: %s", ev.get("message"))
                        plan_raw = ""
                        break
            except Exception as exc:
                log.warning("crew replan exception: %s", exc)
                plan_raw = ""
    plan = parse_plan(plan_raw, worker_count)
    steps = plan.get("steps") or _steps_from_agents(plan["agents"])
    step_waves = plan_waves(steps)
    yield {
        "type": "agent",
        "agent": _agent_view(
            {"id": "lead", "name": "总控", "brief": plan["lead"]},
            role="lead",
            status="waiting",
            content=plan["lead"],
            model=lead_model,
            effort=lead_effort,
        ),
    }
    first_step_ids = {s["id"] for s in (step_waves[0] if step_waves else [])}
    roster_specs: list[dict[str, Any]] = []
    for step in steps:
        workers = [{**w, "step": step["id"], "step_name": step["name"]} for w in step["agents"]]
        if len(workers) >= 2:
            lead_spec = {
                "id": f"step-{step['id']}-lead",
                "name": f"{step['name']}总控",
                "brief": step.get("brief") or f"对齐「{step['name']}」内的并行进度",
                "depends_on": [],
                "step": step["id"],
                "step_name": step["name"],
                "role": "step-lead",
            }
            roster_specs.append(lead_spec)
            step["lead_spec"] = lead_spec
        step["workers"] = workers
        roster_specs.extend(workers)
    reviewers: list[dict[str, Any]] = []
    for step in steps:
        kept = []
        for worker in step.get("workers") or []:
            if _is_reviewer(worker):
                worker["role"] = "reviewer"
                worker["step"] = "review"
                worker["step_name"] = "审核"
                reviewers.append(worker)
            else:
                kept.append(worker)
        step["workers"] = kept
        if step.get("lead_spec") and len(kept) < 2:
            dropped = step.pop("lead_spec", None)
            if dropped:
                roster_specs = [spec for spec in roster_specs if spec.get("id") != dropped.get("id")]
    if not reviewers:
        reviewer_spec = {
            "id": "reviewer",
            "name": "审核",
            "brief": "审阅各步骤产出；不足则向总控打回，不要自行改写成终稿",
            "depends_on": [],
            "step": "review",
            "step_name": "审核",
            "role": "reviewer",
        }
        roster_specs.append(reviewer_spec)
        reviewers.append(reviewer_spec)
    else:
        reviewer_spec = reviewers[0]
        reviewer_spec["role"] = "reviewer"
    pending_asks: dict[str, list[str]] = {}
    links: list[dict[str, str]] = []
    routed: set[tuple[str, str, str]] = set()
    seen_version: dict[str, int] = {}
    for spec in roster_specs:
        aid = str(spec.get("id") or "")
        if aid and spec.get("brief"):
            machine.briefs.setdefault(aid, spec["brief"])
    machine.briefs.setdefault("lead", plan["lead"])
    for spec in roster_specs:
        role = spec.get("role") or "worker"
        ready = spec.get("step") in first_step_ids and role not in {"reviewer"}
        yield {
            "type": "agent",
            "agent": _agent_view(
                spec,
                role=role,
                status="queued" if ready else "blocked",
                model=worker_model if role not in {"step-lead", "reviewer"} else lead_model,
                effort=worker_effort if role not in {"step-lead", "reviewer"} else plan_effort,
            ),
        }

    completed: dict[str, dict[str, Any]] = {}
    ledger_text = ""
    ledger_entries: list[dict[str, str]] = []
    reports: list[dict[str, Any]] = []

    async def stream_once(spec: dict[str, Any], payload: dict[str, Any], queue: asyncio.Queue, role: str) -> dict[str, Any]:
        await queue.put({"type": "agent", "agent": _agent_view(spec, role=role, status="running")})
        full = ""
        activity: list[dict[str, Any]] = []
        status = "done"
        stalled = False
        model = str(payload.get("model") or worker_model)
        effort = ""
        if isinstance(payload.get("reasoning"), dict):
            effort = str(payload["reasoning"].get("effort") or worker_effort)
        try:
            async for ev in xai_stream(token, payload):
                if ev["type"] == "reset":
                    full = ""
                    await queue.put({"type": "agent-reset", "agent_id": spec["id"]})
                elif ev["type"] == "delta":
                    full += ev.get("text") or ""
                    await queue.put({"type": "agent-delta", "agent_id": spec["id"], "text": ev.get("text") or ""})
                elif ev["type"] == "activity":
                    activity.append(ev["entry"])
                    await queue.put({"type": "agent-activity", "agent_id": spec["id"], "entry": ev["entry"]})
                elif ev["type"] == "status":
                    await queue.put({"type": "status", "text": ev.get("text")})
                    await queue.put({"type": "agent-status", "agent_id": spec["id"], "text": ev.get("text")})
                elif ev["type"] == "done":
                    full = ev.get("text") or full
                    activity = ev.get("activity") or activity
                    if ev.get("stalled"):
                        stalled = True
                        status = "partial"
                elif ev["type"] == "error":
                    status = "error"
                    full = ev.get("message") or "子代理失败"
        except Exception as exc:
            status = "error"
            full = full or ("连接中断，请再试一次" if is_drop_error(exc) else f"子代理失败：{exc}")
        if status in {"error", "partial"}:
            machine.mark_failed(str(spec.get("id") or ""))
        result = _agent_view(spec, role=role, status=status, content=full, activity=activity, model=model, effort=effort)
        notes = parse_feedback(full)
        if notes:
            result["feedback"] = notes
        await queue.put({"type": "agent", "agent": result})
        return result

    async def stream_agent(spec: dict[str, Any], payload: dict[str, Any], queue: asyncio.Queue, role: str) -> dict[str, Any]:
        current = payload
        result: dict[str, Any] | None = None
        running_ids.add(str(spec.get("id") or ""))
        try:
            for _ in range(4):
                result = await stream_once(spec, current, queue, role)
                notes = take_guidance(run_id, str(spec.get("id") or ""))
                if not notes:
                    return result
                await queue.put({"type": "status", "text": f"按你的指导继续「{spec.get('name') or spec.get('id')}」"})
                await queue.put({"type": "guide", "agent_id": spec["id"], "notes": notes})
                current = attach_human_notes(current, notes)
            return result or _agent_view(spec, role=role, status="done")
        finally:
            running_ids.discard(str(spec.get("id") or ""))

    def specialist_directory() -> str:
        names = [f"{spec['name']}({spec['id']})" for spec in roster_specs if spec.get("role") != "step-lead"]
        names.append("总控(lead)")
        return "、".join(names)

    def remember_link(src: str, dst: str, kind: str) -> dict[str, str]:
        edge = {"from": src, "to": dst, "kind": kind}
        links.append(edge)
        return edge

    def stash_ask(target_id: str, origin_name: str, ask: str) -> None:
        pending_asks.setdefault(target_id, []).append(f"- {origin_name}: {ask}")

    def take_stashed(spec_id: str, extra: str = "") -> str:
        stashed = pending_asks.pop(spec_id, [])
        bits = [extra.strip()] if extra and extra.strip() else []
        bits.extend(stashed)
        return "\n".join(bits).strip()

    def upsert_report(result: dict[str, Any]) -> None:
        aid = str(result.get("id") or "")
        if not aid or result.get("role") == "lead":
            return
        completed[aid] = result
        if result.get("role") == "reviewer":
            return
        for index, item in enumerate(reports):
            if str(item.get("id") or "") == aid:
                reports[index] = result
                break
        else:
            reports.append(result)
        commit_facts(fact_board, result)

    def step_artifacts() -> list[dict[str, Any]]:
        arts: list[dict[str, Any]] = []
        seen: set[str] = set()
        for step in steps:
            lead_spec = step.get("lead_spec")
            if lead_spec and lead_spec.get("id") in completed:
                rec = completed[lead_spec["id"]]
                aid = str(rec.get("id") or "")
                if aid and aid not in seen:
                    seen.add(aid)
                    arts.append(rec)
                continue
            for worker in step.get("workers") or []:
                rec = completed.get(worker["id"])
                if not rec:
                    continue
                aid = str(rec.get("id") or "")
                if aid and aid not in seen:
                    seen.add(aid)
                    arts.append(rec)
        return arts

    def pack_artifacts() -> str:
        arts = step_artifacts()
        if not arts:
            return "（尚无步骤产物）"
        return "\n\n".join(f"### {r.get('name')}\n{r.get('content') or ''}" for r in arts)

    def build_worker_payload(spec: dict[str, Any], step: dict[str, Any], board: str, coord: str, extra: str = "") -> dict[str, Any]:
        contract = format_contract(fact_board, spec)
        aid = str(spec.get("id") or "")
        last = seen_version.get(aid, 0)
        change = machine.changelog_since(last) if last else ""
        seen_version[aid] = machine.plan_version
        brief = machine.briefs.get(aid) or spec.get("brief") or ""
        return {
            "model": worker_model,
            "stream": True,
            "store": False,
            "tools": list(DEFAULT_TOOLS),
            "reasoning": {"effort": worker_effort},
            "input": [
                {
                    "role": "system",
                    "content": (
                        f"You are sub-agent {spec['name']} in step「{step.get('name') or spec.get('step_name') or ''}」. "
                        f"{TOOL_RULE} {FEEDBACK_RULE} {GOAL_PIN} "
                        f"Plan version v{machine.plan_version}. "
                        "If a changelog is attached, those premises replaced older ones — do not keep working from stale instructions. "
                        f"Your assignment: {brief}. "
                        f"Specialists you may ask: {specialist_directory()}. "
                        "Work in parallel with your step-mates. "
                        "Use only the contract entries relevant to you — not other specialists' essays. "
                        "Do not write the final combined report."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"{GOAL_PIN}\n{question}\n\nLead plan: {machine.briefs.get('lead') or plan['lead']}\n"
                        f"Step coordination:\n{coord or '（无）'}\n"
                        f"Contract (filtered):\n{contract}"
                        + (f"\n\nUpdated assignment (authoritative):\n{brief}" if machine.briefs.get(aid) else "")
                        + (f"\n\nPlan changelog since you last ran:\n{change}" if change else "")
                        + (f"\n\nRequests routed to you:\n{extra}" if extra else "")
                    ),
                },
            ],
        }

    async def emit_route(queue: asyncio.Queue, origin: dict[str, Any], target: dict[str, Any], ask: str, kind: str) -> bool:
        key = (str(origin.get("id") or ""), str(target.get("id") or ""), ask[:80])
        if not key[0] or not key[1] or key in routed:
            return False
        routed.add(key)
        await queue.put({"type": "link", **remember_link(key[0], key[1], kind)})
        await queue.put(
            {
                "type": "status",
                "text": f"{origin.get('name') or key[0]} → {target.get('name') or key[1]}：{ask[:80]}",
            }
        )
        return True

    async def collect_routes(
        origin: dict[str, Any],
        text: str,
        scope: list[dict[str, Any]],
        queue: asyncio.Queue,
        kind: str = "feedback",
    ) -> dict[str, list[str]]:
        asks: dict[str, list[str]] = {}
        for item in parse_feedback(text):
            target = resolve_agent(item["to"], scope) or resolve_agent(item["to"], roster_specs)
            if not target or target.get("id") == origin.get("id"):
                continue
            if not await emit_route(queue, origin, target, item["ask"], kind):
                continue
            role = target.get("role") or "worker"
            tid = str(target.get("id") or "")
            in_scope = tid in {w.get("id") for w in scope}
            already = tid in completed
            if role in {"lead", "step-lead", "reviewer"} or (not in_scope and not already):
                stash_ask(tid, str(origin.get("name") or origin.get("id")), item["ask"])
                continue
            asks.setdefault(tid, []).append(f"- {origin.get('name') or origin.get('id')}: {item['ask']}")
        for tid, notes in list(asks.items()):
            merged = merge_feedback([{"to": tid, "ask": note} for note in notes])
            asks[tid] = [row["ask"] for row in merged] or notes[:1]
        return asks

    async def run_guided(spec: dict[str, Any], queue: asyncio.Queue, inflight: set[str]) -> None:
        aid = str(spec.get("id") or "")
        try:
            notes = take_guidance(run_id, aid)
            if not notes:
                return
            await queue.put({"type": "status", "text": f"按你的指导继续「{spec.get('name') or aid}」"})
            await queue.put({"type": "guide", "agent_id": aid, "notes": notes})
            role = spec.get("role") or "worker"
            if role == "lead":
                human_lead_notes.extend(notes)
                return
            extra = "\n".join(f"- {item}" for item in notes)
            step = next((item for item in steps if item.get("id") == spec.get("step")), {"name": spec.get("step_name") or "", "id": spec.get("step") or ""})
            coord = step.get("brief") or ""
            lead_spec = step.get("lead_spec") if isinstance(step, dict) else None
            if lead_spec and lead_spec.get("id") in completed:
                coord = str((completed.get(lead_spec["id"]) or {}).get("content") or coord)
            payload = build_worker_payload(spec, step, ledger_text, coord, f"Human guidance:\n{extra}")
            result = await stream_agent(spec, payload, queue, role)
            upsert_report(result)
        finally:
            inflight.discard(aid)
            await queue.put({"type": "_guide_done"})

    def kick_idle_guidance(queue: asyncio.Queue, inflight: set[str]) -> int:
        started = 0
        for aid in peek_guidance_ids(run_id):
            if aid in running_ids or aid in inflight:
                continue
            spec = resolve_agent(aid, roster_specs)
            if aid == "lead" and not spec:
                spec = {"id": "lead", "name": "总控", "role": "lead", "brief": plan["lead"]}
            if not spec:
                take_guidance(run_id, aid)
                continue
            inflight.add(aid)
            asyncio.create_task(run_guided(spec, queue, inflight))
            started += 1
        return started

    async def flush_guidance():
        queue: asyncio.Queue = asyncio.Queue()
        inflight: set[str] = set()
        extra_open = kick_idle_guidance(queue, inflight)
        while extra_open > 0:
            ev = await queue.get()
            if ev.get("type") == "_guide_done":
                extra_open = max(0, extra_open - 1)
                extra_open += kick_idle_guidance(queue, inflight)
                continue
            yield ev

    async def run_workers(
        batch: list[dict[str, Any]],
        step: dict[str, Any],
        board: str,
        coord: str,
        queue: asyncio.Queue,
        extra_by_id: dict[str, str] | None = None,
    ) -> None:
        extra_by_id = extra_by_id or {}
        for offset in range(0, len(batch), 8):
            slice_ = batch[offset : offset + 8]
            tasks = []
            for spec in slice_:
                extra = take_stashed(spec["id"], extra_by_id.get(spec["id"], ""))
                tasks.append(
                    asyncio.create_task(
                        stream_agent(spec, build_worker_payload(spec, step, board, coord, extra), queue, spec.get("role") or "worker")
                    )
                )
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for item in results:
                if isinstance(item, dict):
                    upsert_report(item)

    async def iter_agent(spec: dict[str, Any], payload: dict[str, Any], role: str):
        queue: asyncio.Queue = asyncio.Queue()
        task = asyncio.create_task(stream_agent(spec, payload, queue, role))
        while True:
            if task.done() and queue.empty():
                break
            try:
                ev = await asyncio.wait_for(queue.get(), timeout=0.15)
                yield ev
            except asyncio.TimeoutError:
                continue
        while not queue.empty():
            yield queue.get_nowait()
        result = await task
        upsert_report(result)
        yield {"type": "_done", "result": result}

    async def run_step(step: dict[str, Any], board: str, queue: asyncio.Queue) -> dict[str, Any]:
        workers = step.get("workers") or []
        lead_spec = step.get("lead_spec")
        coord = step.get("brief") or ""
        try:
            return await _run_step_body(step, board, queue, workers, lead_spec, coord)
        except Exception as exc:
            report = {
                "id": step.get("id"),
                "name": step.get("name") or step.get("id"),
                "content": f"步骤失败：{exc}",
                "status": "error",
                "role": "step-lead",
            }
            await queue.put({"type": "_step_done", "step_id": step["id"], "report": report})
            return report

    async def _run_step_body(step, board, queue, workers, lead_spec, coord):
        workers = [w for w in (workers or []) if not _is_reviewer(w)]
        if not workers and not lead_spec:
            report = {
                "id": step.get("id"),
                "name": step.get("name") or step.get("id"),
                "content": "",
                "status": "done",
                "role": "step-lead",
            }
            await queue.put({"type": "_step_done", "step_id": step["id"], "report": report})
            return report
        if lead_spec:
            coord_payload = {
                "model": lead_model,
                "stream": True,
                "store": False,
                "reasoning": {"effort": "low"},
                "input": [
                    {
                        "role": "system",
                        "content": (
                            f"You are the step lead for「{step['name']}」. {TOOL_RULE} {GOAL_PIN} "
                            "Write a short coordination note: who does what in parallel, "
                            "what contract fields they should emit, when to ask another specialist instead of guessing, "
                            "and when this step is done. No final product."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"{GOAL_PIN}\n{question}\n\nLead plan: {machine.briefs.get('lead') or plan['lead']}\n"
                            f"Plan version: v{machine.plan_version}\n"
                            f"Step: {step['name']} — {step.get('brief')}\n"
                            f"Workers: {', '.join(w['name'] + ': ' + w['brief'] for w in workers)}\n"
                            f"Contract:\n{format_contract(fact_board)}"
                        ),
                    },
                ],
            }
            lead_result = await stream_agent(lead_spec, coord_payload, queue, "step-lead")
            upsert_report(lead_result)
            coord = lead_result.get("content") or coord
        await run_workers(workers, step, board, coord, queue)
        for _ in range(2):
            follow: dict[str, list[str]] = {}
            for spec in workers:
                result = completed.get(spec["id"]) or {}
                routed_asks = await collect_routes(spec, str(result.get("content") or ""), workers, queue)
                for tid, notes in routed_asks.items():
                    follow.setdefault(tid, []).extend(notes)
            for tid, notes in list(follow.items()):
                merged = merge_feedback([{"to": tid, "ask": note} for note in notes])
                follow[tid] = [row["ask"] for row in merged] or notes[:1]
            if not follow:
                break
            extra_by_id: dict[str, str] = {}
            by_home: dict[str, list[dict[str, Any]]] = {}
            for tid, notes in follow.items():
                spec = resolve_agent(tid, workers) or resolve_agent(tid, roster_specs)
                if not spec or spec.get("role") in {"lead", "reviewer"}:
                    continue
                extra_by_id[str(spec["id"])] = "\n".join(notes[:4])
                hid = str(spec.get("step") or step.get("id") or "")
                by_home.setdefault(hid, []).append(spec)
            if not extra_by_id:
                break
            names = "、".join(spec["name"] for group in by_home.values() for spec in group)
            await queue.put({"type": "status", "text": f"「{step['name']}」转交：{names}"})
            for hid, group in by_home.items():
                home = next((item for item in steps if item.get("id") == hid), step)
                home_coord = home.get("brief") or coord
                home_lead = home.get("lead_spec")
                if home_lead and home_lead["id"] in completed:
                    home_coord = str((completed.get(home_lead["id"]) or {}).get("content") or home_coord)
                await run_workers(group, home, board, home_coord, queue, extra_by_id)
        packed = "\n\n".join(
            f"### {w['name']}\n{(completed.get(w['id']) or {}).get('content') or ''}" for w in workers
        )
        if lead_spec:
            await queue.put({"type": "agent", "agent": _agent_view(lead_spec, role="step-lead", status="writing", content="")})
            align_payload = {
                "model": lead_model,
                "stream": True,
                "store": False,
                "reasoning": {"effort": plan_effort},
                "input": [
                    {
                        "role": "system",
                        "content": (
                            f"You are the step lead for「{step['name']}」. {TOOL_RULE} {GOAL_PIN} {FEEDBACK_RULE} "
                            "Align the parallel workers: resolve conflicts, keep facts, "
                            "emit contract facts for later steps. Later specialists will NOT see these essays — only your facts. "
                            "Not the final user answer."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"{GOAL_PIN}\n{question}\nCoordination:\n{coord}\n\nWorker reports (this step only):\n{packed}"
                        ),
                    },
                ],
            }
            aligned = await stream_agent(lead_spec, align_payload, queue, "step-lead")
            upsert_report(aligned)
            report = aligned
        else:
            report = {
                "id": step["id"],
                "name": step["name"],
                "content": packed,
                "status": "done",
                "role": "step-lead",
            }
        try:
            await queue.put({"type": "_step_done", "step_id": step["id"], "report": report})
        except Exception:
            pass
        return report

    async def run_step_wave(wave: list[dict[str, Any]], board: str):
        queue: asyncio.Queue = asyncio.Queue()
        tasks = [asyncio.create_task(run_step(step, board, queue)) for step in wave]
        finished = 0
        extra_open = 0
        inflight: set[str] = set()
        while finished < len(tasks) or extra_open > 0:
            try:
                ev = await asyncio.wait_for(queue.get(), timeout=0.35)
            except asyncio.TimeoutError:
                extra_open += kick_idle_guidance(queue, inflight)
                continue
            if ev.get("type") == "_step_done":
                finished += 1
                report = ev.get("report") or {}
                if report.get("id"):
                    completed[str(report["id"])] = report
                extra_open += kick_idle_guidance(queue, inflight)
                continue
            if ev.get("type") == "_guide_done":
                extra_open = max(0, extra_open - 1)
                extra_open += kick_idle_guidance(queue, inflight)
                continue
            extra_open += kick_idle_guidance(queue, inflight)
            if ev.get("type") == "agent" and ev.get("agent", {}).get("status") in {"done", "error"}:
                agent = ev["agent"]
                completed[str(agent.get("id") or "")] = agent
            yield ev
        await asyncio.gather(*tasks, return_exceptions=True)

    for index, wave in enumerate(step_waves):
        names = [s["name"] for s in wave]
        live_ids = []
        for step in wave:
            if step.get("lead_spec"):
                live_ids.append(step["lead_spec"]["id"])
            live_ids.extend(w["id"] for w in step.get("workers") or [])
        yield machine.enter("running", live_ids)
        yield {"type": "status", "text": f"第 {index + 1}/{len(step_waves)} 波步骤并行：{'、'.join(names)}"}
        ledger_text, ledger_entries = pack_contract_ledger(fact_board)
        yield {"type": "ledger", "wave": index + 1, "waves": len(step_waves), "text": ledger_text, "entries": ledger_entries}
        later = [s for w in step_waves[index + 1 :] for s in w]
        later_ids = {s["id"] for s in later}
        for spec in roster_specs:
            if spec.get("step") in later_ids:
                yield {
                    "type": "agent",
                    "agent": _agent_view(
                        spec,
                        role=spec.get("role") or "worker",
                        status="blocked",
                        model=worker_model,
                        effort=worker_effort,
                    ),
                }
        async for ev in run_step_wave(wave, ledger_text):
            yield ev
        for step in wave:
            for spec in [step.get("lead_spec"), *step.get("workers", [])]:
                if spec and spec["id"] in completed:
                    upsert_report(completed[spec["id"]])
        machine.score = coverage_score(fact_board, [s["id"] for s in steps], machine.acceptance)
        yield machine.snapshot()
        ledger_text, ledger_entries = pack_contract_ledger(fact_board)
        yield {"type": "ledger", "wave": index + 1, "waves": len(step_waves), "text": ledger_text, "entries": ledger_entries}
        wave_texts = []
        for step in wave:
            for spec in [step.get("lead_spec"), *step.get("workers", [])]:
                if spec and spec["id"] in completed:
                    wave_texts.append(str((completed.get(spec["id"]) or {}).get("content") or ""))
        merged_ask = collect_merged_ask(wave_texts)
        if merged_ask:
            yield machine.enter("asking", ["lead"])
            yield {"type": "status", "text": "多位专员的疑问已合并，请选一次"}
            yield {"type": "ask", "run_id": run_id, **merged_ask}
            choice = await wait_user_choice(run_id)
            if choice:
                apply_user_choice(machine, fact_board, choice, "user answered merged ask")
                later_ids = {s["id"] for w in step_waves[index + 1 :] for s in w}
                for spec in roster_specs:
                    if spec.get("step") in later_ids:
                        stash_ask(str(spec["id"]), "用户", f"已选定：{choice}")
                yield {"type": "status", "text": "已按你的选择继续"}
                machine.score = coverage_score(fact_board, [s["id"] for s in steps], machine.acceptance)
                yield machine.snapshot()

    async for ev in flush_guidance():
        yield ev

    review_notes = ""
    for review_round in range(3):
        machine.review_round = review_round
        yield machine.enter("reviewing", [str(reviewer_spec.get("id") or "reviewer")])
        yield {"type": "status", "text": "审核正在检查各步骤产出…" if review_round == 0 else f"第 {review_round} 轮返工后复审…"}
        yield {
            "type": "agent",
            "agent": _agent_view(
                reviewer_spec,
                role="reviewer",
                status="running",
                model=lead_model,
                effort=plan_effort,
            ),
        }
        packed_now = pack_artifacts()
        machine.score = coverage_score(fact_board, [s["id"] for s in steps], machine.acceptance)
        yield machine.snapshot()
        score = machine.score
        review_payload = {
            "model": lead_model,
            "stream": True,
            "store": False,
            "tools": list(DEFAULT_TOOLS),
            "reasoning": {"effort": plan_effort},
            "input": [
                {
                    "role": "system",
                    "content": (
                        f"You are the reviewer. {TOOL_RULE} "
                        "You may send work back to the lead. Do not invent missing work or write the final user answer. "
                        "The score below is the stop rule: if coverage>=0.67, conflicts=0, and acceptance>=0.5, prefer pass. "
                        "After a short critique, emit control JSON: "
                        '{"pass":false,"issues":["..."],"feedback":[{"to":"lead","ask":"..."}],"notes":"..."}. '
                        'If the work is good enough: {"pass":true,"notes":"..."}.'
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"{GOAL_PIN}\n{question}\n\nLead plan: {machine.briefs.get('lead') or plan['lead']}\n"
                        f"Score: coverage={score.get('coverage')} confidence={score.get('confidence')} "
                        f"conflicts={score.get('conflicts')} acceptance={score.get('acceptance')}\n"
                        f"Plan v{machine.plan_version}\n"
                        f"Contract:\n{format_contract(fact_board)}\n\nStep artifacts:\n{packed_now}"
                    ),
                },
            ],
        }
        review_result = None
        async for ev in iter_agent(reviewer_spec, review_payload, "reviewer"):
            if ev.get("type") == "_done":
                review_result = ev.get("result")
                continue
            yield ev
        review_raw = str((review_result or {}).get("content") or "")
        review = parse_review(review_raw)
        review["feedback"] = merge_feedback(review.get("feedback") or [])
        review_notes = review.get("notes") or review_notes
        for item in review.get("feedback") or []:
            target = resolve_agent(item["to"], roster_specs) or {
                "id": "lead",
                "name": "总控",
                "role": "lead",
            }
            yield {"type": "link", **remember_link(reviewer_spec["id"], str(target.get("id") or "lead"), "review")}
            if target.get("id") and target.get("id") != "lead":
                stash_ask(str(target["id"]), str(reviewer_spec.get("name") or "审核"), item["ask"])
                machine.mark_sent_back(str(target["id"]))
        verdict = decide_review(review, review_raw, review_round, machine.max_review, machine.score)
        if verdict == "pass":
            yield {"type": "status", "text": f"审核通过（覆盖 {score.get('coverage')} / 冲突 {score.get('conflicts')}），交总控汇总"}
            break
        if verdict == "stop":
            yield machine.stop("max-rework")
            yield {"type": "status", "text": "已达返工上限，转入汇总"}
            break
        machine.bump_plan(f"review send-back: {(review_notes or 'gaps')[:160]}")
        assigns = machine_assigns(review, roster_specs, completed, machine.sent_back)
        yield {"type": "status", "text": f"审核打回（覆盖 {score.get('coverage')} / 冲突 {score.get('conflicts')}），复用已有子代理"}
        yield {"type": "link", **remember_link(reviewer_spec["id"], "lead", "review")}
        reused: list[dict[str, Any]] = []
        extra_by_id: dict[str, str] = {}
        for item in assigns[:4]:
            spec = resolve_agent(item.get("id") or "", roster_specs)
            if not spec or spec.get("role") in {"lead", "reviewer"}:
                continue
            brief = item.get("brief") or ""
            extra_by_id[str(spec["id"])] = brief
            if brief:
                prev = machine.briefs.get(str(spec["id"]), "")
                machine.briefs[str(spec["id"])] = (f"{prev}；" if prev else "") + f"[v{machine.plan_version} 返工] {brief}"
            reused.append(spec)
            machine.mark_sent_back(str(spec["id"]))
            yield {
                "type": "agent",
                "agent": _agent_view(spec, role=spec.get("role") or "worker", status="sent_back"),
            }
            yield {"type": "link", **remember_link("lead", str(spec["id"]), "rework")}
        if not reused:
            yield machine.stop("no-assignee")
            yield {"type": "status", "text": "没有可复用的子代理，转入汇总"}
            break
        names = "、".join(spec["name"] for spec in reused)
        yield machine.enter("reworking", [str(spec["id"]) for spec in reused])
        yield {"type": "status", "text": f"复用已有子代理再跑一轮：{names}"}
        by_step: dict[str, list[dict[str, Any]]] = {}
        for spec in reused:
            by_step.setdefault(str(spec.get("step") or ""), []).append(spec)
        for step in steps:
            batch = by_step.get(str(step.get("id") or "")) or []
            if not batch:
                continue
            coord = step.get("brief") or ""
            lead_spec = step.get("lead_spec")
            if lead_spec and lead_spec["id"] in completed:
                coord = str((completed.get(lead_spec["id"]) or {}).get("content") or coord)
            queue: asyncio.Queue = asyncio.Queue()
            task = asyncio.create_task(run_workers(batch, step, ledger_text, coord, queue, extra_by_id))
            while True:
                if task.done() and queue.empty():
                    break
                try:
                    ev = await asyncio.wait_for(queue.get(), timeout=0.15)
                    yield ev
                except asyncio.TimeoutError:
                    continue
            while not queue.empty():
                yield queue.get_nowait()
            await task
            if lead_spec:
                packed_step = "\n\n".join(
                    f"### {w['name']}\n{(completed.get(w['id']) or {}).get('content') or ''}"
                    for w in (step.get("workers") or [])
                )
                align_payload = {
                    "model": lead_model,
                    "stream": True,
                    "store": False,
                    "reasoning": {"effort": plan_effort},
                    "input": [
                        {
                            "role": "system",
                            "content": (
                                f"You are the step lead for「{step['name']}」. {TOOL_RULE} "
                                "Realign after a rework round. Keep facts, resolve conflicts, "
                                "write a concise step report. Not the final user answer."
                            ),
                        },
                        {
                            "role": "user",
                            "content": (
                                f"User request:\n{brief}\nRework notes: {review_notes}\n"
                                f"Worker reports:\n{packed_step}"
                            ),
                        },
                    ],
                }
                async for ev in iter_agent(lead_spec, align_payload, "step-lead"):
                    if ev.get("type") == "_done":
                        continue
                    yield ev
        ledger_text, ledger_entries = pack_contract_ledger(fact_board)
        yield {"type": "ledger", "wave": review_round + 1, "waves": 3, "text": ledger_text, "entries": ledger_entries}

    async for ev in flush_guidance():
        yield ev
    lead_notes = take_guidance(run_id, "lead")
    if lead_notes:
        human_lead_notes.extend(lead_notes)

    yield machine.enter("synthesizing", ["lead"])
    yield {"type": "status", "text": "总控正在按进度板汇总…"}
    yield {
        "type": "agent",
        "agent": _agent_view(
            {"id": "lead", "name": "总控", "brief": plan["lead"]},
            role="lead",
            status="writing",
            content="",
            model=lead_model,
            effort=lead_effort,
        ),
    }
    packed = pack_artifacts()
    reviewer_report = completed.get(str(reviewer_spec.get("id") or "reviewer")) or {}
    synth_payload = {
        "model": lead_model,
        "stream": True,
        "store": True,
        "tools": list(DEFAULT_TOOLS),
        "reasoning": {"effort": lead_effort},
        "input": [
            {"role": "system", "content": f"{MODE_PROMPTS['multi']} {TOOL_RULE} {ASK_RULE} {GOAL_PIN}"},
            {
                "role": "user",
                "content": (
                    f"{GOAL_PIN}\n{question}\n\nLead plan: {machine.briefs.get('lead') or plan['lead']}\n"
                    f"Plan version: v{machine.plan_version}\n"
                    f"{machine.changelog_since(1)}\n"
                    f"Score: {machine.score}\n\n"
                    f"Contract:\n{format_contract(fact_board)}\n\nStep artifacts:\n{packed}\n\n"
                    f"Reviewer notes: {review_notes or (reviewer_report.get('content') or '（无）')}"
                    + (
                        f"\n\nHuman guidance for the lead:\n" + "\n".join(f"- {n}" for n in human_lead_notes)
                        if human_lead_notes
                        else ""
                    )
                ),
            },
        ],
    }
    lead_activity: list[dict[str, Any]] = []
    lead_text = ""
    response_id = None
    async for ev in xai_stream(token, synth_payload):
        if ev["type"] == "reset":
            lead_text = ""
            yield ev
            yield {"type": "agent-reset", "agent_id": "lead"}
        elif ev["type"] == "delta":
            lead_text += ev.get("text") or ""
            yield ev
            yield {"type": "agent-delta", "agent_id": "lead", "text": ev.get("text") or ""}
        elif ev["type"] == "activity":
            lead_activity.append(ev["entry"])
            yield ev
            yield {"type": "agent-activity", "agent_id": "lead", "entry": ev["entry"]}
        elif ev["type"] == "status":
            yield ev
        elif ev["type"] == "done":
            lead_text = ev.get("text") or lead_text
            lead_activity = ev.get("activity") or lead_activity
            response_id = ev.get("response_id") or response_id
        elif ev["type"] == "error":
            yield ev
            return
    synth_ask = parse_ask(lead_text)
    if synth_ask:
        lead_text = strip_ask_json(lead_text)
        yield machine.enter("asking", ["lead"])
        yield {"type": "status", "text": "总控还不确定，需要你选一下"}
        yield {"type": "ask", "run_id": run_id, **synth_ask}
        choice = await wait_user_choice(run_id)
        if choice:
            apply_user_choice(machine, fact_board, choice, "user chose synthesis direction")
            yield {"type": "status", "text": "已按你的选择继续汇总"}
            yield {
                "type": "agent",
                "agent": _agent_view(
                    {"id": "lead", "name": "总控", "brief": plan["lead"]},
                    role="lead",
                    status="writing",
                    content="",
                    model=lead_model,
                    effort=lead_effort,
                ),
            }
            last = synth_payload["input"][-1]
            last["content"] = f"{last.get('content') or ''}\n\nUser decision:\n{choice}\nWrite the final answer now. Do not ask again."
            lead_text = ""
            async for ev in xai_stream(token, synth_payload):
                if ev["type"] == "reset":
                    lead_text = ""
                    yield ev
                    yield {"type": "agent-reset", "agent_id": "lead"}
                elif ev["type"] == "delta":
                    lead_text += ev.get("text") or ""
                    yield ev
                    yield {"type": "agent-delta", "agent_id": "lead", "text": ev.get("text") or ""}
                elif ev["type"] == "activity":
                    lead_activity.append(ev["entry"])
                    yield ev
                    yield {"type": "agent-activity", "agent_id": "lead", "entry": ev["entry"]}
                elif ev["type"] == "status":
                    yield ev
                elif ev["type"] == "done":
                    lead_text = ev.get("text") or lead_text
                    lead_activity = ev.get("activity") or lead_activity
                    response_id = ev.get("response_id") or response_id
                elif ev["type"] == "error":
                    yield ev
                    return
            lead_text = strip_ask_json(lead_text) or lead_text
    team = [
        _agent_view(
            {"id": "lead", "name": "总控", "brief": plan["lead"]},
            role="lead",
            status="done",
            content=lead_text,
            activity=lead_activity,
            model=lead_model,
            effort=lead_effort,
        ),
        *[
            _agent_view(
                r,
                role=r.get("role") or "worker",
                status=r.get("status") or "done",
                content=r.get("content") or "",
                activity=r.get("activity") or [],
                model=r.get("model") or worker_model,
                effort=r.get("effort") or worker_effort,
            )
            for r in reports
        ],
    ]
    if reviewer_report:
        team.append(
            _agent_view(
                reviewer_report,
                role="reviewer",
                status=reviewer_report.get("status") or "done",
                content=reviewer_report.get("content") or "",
                activity=reviewer_report.get("activity") or [],
                model=reviewer_report.get("model") or lead_model,
                effort=reviewer_report.get("effort") or plan_effort,
            )
        )
    yield machine.stop("done")
    yield {
        "type": "crew-done",
        "text": lead_text,
        "agents": team,
        "activity": lead_activity,
        "ledger": ledger_entries,
        "links": links,
        "response_id": response_id,
    }
    close_crew_run(run_id)


@app.post("/api/chat")
async def chat(body: ChatIn) -> StreamingResponse:
    token = require_token()
    text = (body.message or "").strip()
    if not text and not body.file_ids:
        raise HTTPException(400, "请输入内容或上传文件")

    model = (body.model or "grok-4.6").strip() or "grok-4.6"
    effort = (body.effort or "high").strip().lower()
    if effort not in {"low", "medium", "high", "xhigh"}:
        effort = "high"
    if body.conversation_id:
        convo = get_conversation(body.conversation_id)
    else:
        convo = {
            "id": str(uuid.uuid4()),
            "title": "新对话",
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "model": model,
            "previous_response_id": None,
            "messages": [],
        }

    user_content, public_files = await build_user_content(token, text, body.file_ids)
    user_msg = {
        "id": str(uuid.uuid4()),
        "role": "user",
        "content": text,
        "files": public_files,
        "created_at": now_iso(),
    }
    assistant_msg = {
        "id": str(uuid.uuid4()),
        "role": "assistant",
        "content": "",
        "files": [],
        "created_at": now_iso(),
    }
    convo["messages"].append(user_msg)
    convo["messages"].append(assistant_msg)
    convo["model"] = model
    convo["updated_at"] = now_iso()
    if convo.get("title") in (None, "", "新对话") and text:
        convo["title"] = title_from_text(text)
    elif convo.get("title") in (None, "", "新对话") and public_files:
        convo["title"] = title_from_text(public_files[0]["name"])
    upsert_conversation(convo)

    mode = (body.mode or "chat").strip().lower()
    if mode not in MODE_PROMPTS:
        mode = "chat"
    convo["mode"] = mode

    if mode == "multi":
        async def generate_crew():
            yield sse(
                {
                    "type": "start",
                    "conversation": public_conversation(convo),
                    "user_message": user_msg,
                    "assistant_id": assistant_msg["id"],
                }
            )
            crew_text = ""
            crew_agents: list[dict[str, Any]] = []
            crew_map: dict[str, dict[str, Any]] = {}
            crew_activity: list[dict[str, Any]] = []
            crew_ledger: list[dict[str, Any]] = []
            crew_links: list[dict[str, str]] = []
            crew_phase: dict[str, Any] | None = None
            crew_run_id = ""
            response_id = None
            failed = ""
            try:
                history = compact_history(convo.get("messages") or [], {user_msg["id"], assistant_msg["id"]})
                async for ev in run_crew(token, text, agent_settings(), history):
                    kind = ev.get("type")
                    if kind == "crew-run":
                        crew_run_id = str(ev.get("run_id") or "")
                    if kind == "crew-done":
                        crew_text = ev.get("text") or ""
                        crew_agents = ev.get("agents") or []
                        crew_activity = ev.get("activity") or []
                        crew_ledger = ev.get("ledger") or crew_ledger
                        crew_links = ev.get("links") or crew_links
                        response_id = ev.get("response_id") or response_id
                        by_id = {str(a.get("id") or ""): a for a in crew_agents if a.get("id")}
                        for aid, cur in crew_map.items():
                            if cur.get("guidance") and aid in by_id:
                                by_id[aid]["guidance"] = cur["guidance"]
                    else:
                        if kind == "phase":
                            crew_phase = ev
                        if kind == "link" and ev.get("from") and ev.get("to"):
                            crew_links.append({"from": str(ev["from"]), "to": str(ev["to"]), "kind": str(ev.get("kind") or "feedback")})
                        if kind == "guide" and ev.get("agent_id"):
                            aid = str(ev.get("agent_id") or "")
                            cur = crew_map.setdefault(aid, {"id": aid, "guidance": []})
                            cur["guidance"] = [*(cur.get("guidance") or []), *(ev.get("notes") or [])]
                        if kind == "agent" and isinstance(ev.get("agent"), dict):
                            agent = ev["agent"]
                            aid = str(agent.get("id") or "")
                            if aid:
                                crew_map[aid] = {**crew_map.get(aid, {}), **agent}
                        elif kind == "reset":
                            if "lead" in crew_map:
                                crew_map["lead"]["content"] = ""
                        elif kind == "agent-reset":
                            aid = str(ev.get("agent_id") or "")
                            if aid:
                                cur = crew_map.setdefault(aid, {"id": aid, "content": ""})
                                cur["content"] = ""
                        elif kind == "agent-delta":
                            aid = str(ev.get("agent_id") or "")
                            if aid:
                                cur = crew_map.setdefault(aid, {"id": aid, "content": ""})
                                cur["content"] = (cur.get("content") or "") + (ev.get("text") or "")
                        elif kind == "agent-activity":
                            aid = str(ev.get("agent_id") or "")
                            if aid:
                                cur = crew_map.setdefault(aid, {"id": aid, "activity": []})
                                cur.setdefault("activity", []).append(ev.get("entry"))
                        elif kind == "ledger":
                            crew_ledger = ev.get("entries") or crew_ledger
                        elif kind == "done":
                            response_id = ev.get("response_id") or response_id
                        elif kind == "error":
                            failed = ev.get("message") or "生成失败"
                        yield sse(ev)
            except HTTPException as exc:
                failed = str(exc.detail)
                yield sse({"type": "error", "message": failed})
            except asyncio.CancelledError:
                failed = failed or "已停止"
            except Exception as exc:
                failed = f"请求失败：{exc}"
                yield sse({"type": "error", "message": failed})
            finally:
                if crew_run_id:
                    close_crew_run(crew_run_id)

            if not crew_agents:
                crew_agents = list(crew_map.values())
            if failed == "已停止":
                live = {"running", "planning", "writing", "queued", "blocked", "waiting", "sent_back"}
                crew_agents = [
                    {**a, "status": "stopped"} if (a.get("status") or "") in live else a for a in crew_agents
                ]
                if crew_phase:
                    crew_phase = {**crew_phase, "phase": "stopped", "running": [], "stop": "aborted"}
            if not crew_text:
                lead = crew_map.get("lead") or {}
                crew_text = str(lead.get("content") or "")
            if not str(crew_text).strip():
                parts = [
                    f"### {a.get('name')}\n{a.get('content')}"
                    for a in crew_agents
                    if a.get("id") != "lead" and str(a.get("content") or "").strip()
                ]
                if parts:
                    crew_text = "\n\n".join(parts)
            if failed and not str(crew_text).strip():
                crew_text = failed
            latest = get_conversation(convo["id"])
            for msg in latest["messages"]:
                if msg["id"] == assistant_msg["id"]:
                    msg["content"] = crew_text or (failed or "这一轮没有形成可读回答。请再试一次。")
                    if crew_agents:
                        msg["agents"] = crew_agents
                    if crew_activity:
                        msg["activity"] = crew_activity
                    if crew_ledger:
                        msg["ledger"] = crew_ledger
                    if crew_links:
                        msg["links"] = crew_links
                    if crew_phase:
                        msg["phase"] = crew_phase
                    if failed == "已停止":
                        msg["status"] = "已停止"
                    if failed and not crew_text:
                        msg["error"] = failed
                    break
            if response_id:
                latest["previous_response_id"] = response_id
            latest["updated_at"] = now_iso()
            upsert_conversation(latest)
            yield sse(
                {
                    "type": "done",
                    "text": crew_text,
                    "agents": crew_agents,
                    "activity": crew_activity,
                    "ledger": crew_ledger,
                    "links": crew_links,
                    "phase": crew_phase,
                    "conversation": public_conversation(latest),
                }
            )

        return StreamingResponse(
            generate_crew(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    system_prompt = f"{MODE_PROMPTS[mode]} {TOOL_RULE} {ASK_RULE}"
    payload: dict[str, Any] = {
        "model": model,
        "stream": True,
        "store": True,
        "tools": list(DEFAULT_TOOLS),
        "reasoning": {"effort": effort},
        "input": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
    }
    if convo.get("previous_response_id"):
        payload["previous_response_id"] = convo["previous_response_id"]
        payload["input"] = [
            {"role": "system", "content": TOOL_RULE},
            {"role": "user", "content": user_content},
        ]
    else:
        history = compact_history(convo.get("messages") or [], {user_msg["id"], assistant_msg["id"]})
        if history:
            payload["input"] = [
                {"role": "system", "content": system_prompt + "\n\nPrior conversation:\n\n" + history},
                {"role": "user", "content": user_content},
            ]

    async def generate():
        yield sse(
            {
                "type": "start",
                "conversation": public_conversation(convo),
                "user_message": user_msg,
                "assistant_id": assistant_msg["id"],
            }
        )
        response_id = None
        activity: list[dict[str, Any]] = []
        full = ""
        wants_search = bool(
            body.web_search
            or mode in {"research", "web"}
            or re.search(r"搜|search|查一下|联网|最新", text, re.I)
        )
        if wants_search:
            yield sse({"type": "status", "text": "正在搜索…"})
        try:
            async for ev in xai_stream(token, payload):
                kind = ev.get("type")
                if kind == "reset":
                    full = ""
                    yield sse(ev)
                elif kind == "delta":
                    full += ev.get("text") or ""
                    yield sse(ev)
                elif kind == "activity":
                    activity.append(ev["entry"])
                    yield sse(ev)
                elif kind == "status":
                    yield sse(ev)
                elif kind == "done":
                    full = ev.get("text") or full
                    response_id = ev.get("response_id") or response_id
                    activity = ev.get("activity") or activity
                elif kind == "error":
                    yield sse(ev)
                    return
        except asyncio.CancelledError:
            return
        except Exception as exc:
            yield sse({"type": "error", "message": f"请求失败：{exc}"})
            return

        ask = parse_ask(full)
        if ask:
            full = strip_ask_json(full) or ask["question"]
        if not full.strip():
            full = "这一轮没有形成可读回答。请再试一次。"
        latest = get_conversation(convo["id"])
        trail = compact_activity(activity)
        for msg in latest["messages"]:
            if msg["id"] == assistant_msg["id"]:
                msg["content"] = full
                if trail:
                    msg["activity"] = trail
                if ask:
                    msg["ask"] = ask
                break
        if response_id:
            latest["previous_response_id"] = response_id
        latest["updated_at"] = now_iso()
        upsert_conversation(latest)
        if ask:
            yield sse({"type": "ask", **ask})
        yield sse(
            {
                "type": "done",
                "response_id": response_id,
                "text": full,
                "activity": trail,
                "ask": ask,
                "conversation": public_conversation(latest),
            }
        )

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.exception_handler(HTTPException)
async def http_error(_, exc: HTTPException) -> JSONResponse:
    return JSONResponse({"error": exc.detail}, status_code=exc.status_code)


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8787"))
    uvicorn.run(
        "server:app",
        host="127.0.0.1",
        port=port,
        reload=False,
        log_level="info",
    )
