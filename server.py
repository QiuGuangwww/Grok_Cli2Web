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
}

TOOL_RULE = (
    "You have real server-side tools (web_search, x_search, code_interpreter). "
    "Call those tools instead of writing tool invocations as text. "
    "Never output tool names, XML, HTML, JSON stubs, function_call blocks, "
    "or chain-of-thought. The user only sees your final answer."
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


class ConversationPatch(BaseModel):
    title: str | None = None


class SettingsIn(BaseModel):
    api_key: str | None = None
    clear_api_key: bool = False


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


@app.get("/api/health")
async def health() -> dict[str, Any]:
    auth = resolve_auth()
    return {
        "ok": bool(auth["token"]) and not auth["expired"],
        "source": auth["source"],
        "expired": auth["expired"],
        "user": auth["user"],
        "has_custom_key": bool(str(load_settings().get("api_key") or "").strip()),
    }


@app.post("/api/settings")
async def update_settings(body: SettingsIn) -> dict[str, Any]:
    if body.clear_api_key:
        settings = load_settings()
        settings.pop("api_key", None)
        write_json(SETTINGS_PATH, settings)
    elif body.api_key is not None:
        key = body.api_key.strip()
        if key:
            save_settings({"api_key": key})
        else:
            settings = load_settings()
            settings.pop("api_key", None)
            write_json(SETTINGS_PATH, settings)
    return await health()


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


@app.post("/api/chat")
async def chat(body: ChatIn) -> StreamingResponse:
    token = require_token()
    text = (body.message or "").strip()
    if not text and not body.file_ids:
        raise HTTPException(400, "请输入内容或上传文件")

    model = (body.model or "grok-4.6").strip() or "grok-4.6"
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
    system_prompt = f"{MODE_PROMPTS[mode]} {TOOL_RULE}"
    payload: dict[str, Any] = {
        "model": model,
        "stream": True,
        "store": True,
        "tools": list(DEFAULT_TOOLS),
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
        collected: list[str] = []
        visible_len = 0
        response_id = None
        status_sent = False
        wants_search = bool(
            body.web_search
            or mode in {"research", "web"}
            or re.search(r"搜|search|查一下|联网|最新", text, re.I)
        )
        if wants_search:
            yield sse({"type": "status", "text": "正在搜索…"})
            status_sent = True
        try:
            async with async_client(timeout=httpx.Timeout(3600.0, connect=30.0)) as client:
                async with client.stream(
                    "POST",
                    f"{XAI_BASE}/responses",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                ) as resp:
                    if resp.status_code >= 400:
                        raw = (await resp.aread()).decode("utf-8", errors="replace")
                        yield sse({"type": "error", "message": extract_error_message(raw)})
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
                                    if len(visible) > visible_len:
                                        yield sse({"type": "delta", "text": visible[visible_len:]})
                                        visible_len = len(visible)
                            elif etype == "response.completed":
                                response = event.get("response") or {}
                                response_id = response.get("id") or event.get("id")
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
                                yield sse({"type": "error", "message": message or "生成失败"})
                                return
                            else:
                                item = event.get("item") or {}
                                note = tool_status(etype, str(item.get("type") or ""))
                                if note:
                                    yield sse({"type": "status", "text": note})
        except asyncio.CancelledError:
            return
        except Exception as exc:
            yield sse({"type": "error", "message": f"请求失败：{exc}"})
            return

        full = visible_answer("".join(collected))
        if not full.strip():
            full = "这一轮没有形成可读回答。请再试一次。"
        latest = get_conversation(convo["id"])
        for msg in latest["messages"]:
            if msg["id"] == assistant_msg["id"]:
                msg["content"] = full
                break
        if response_id:
            latest["previous_response_id"] = response_id
        latest["updated_at"] = now_iso()
        upsert_conversation(latest)
        yield sse(
            {
                "type": "done",
                "response_id": response_id,
                "text": full,
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
