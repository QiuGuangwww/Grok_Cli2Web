const $ = (id) => document.getElementById(id);

const MODELS = [
  { id: "grok-4.6", name: "Grok 4.6", desc: "最强推理，适合难问题和长任务" },
  { id: "grok-4.5", name: "Grok 4.5", desc: "更均衡，日常对话更快一些" },
  { id: "grok-4.3", name: "Grok 4.3", desc: "超长上下文，适合大文档" },
];

const MODE_IDS = new Set(["research", "web", "think", "code", "write", "chat"]);

const SLASH = [
  { id: "research", name: "深度研究", desc: "多步检索，交叉验证，输出结构化报告", icon: "◎", group: "模式" },
  { id: "web", name: "联网搜索", desc: "查最新网页、新闻和事实", icon: "⌕", group: "模式" },
  { id: "think", name: "深度思考", desc: "更慢、更严谨地推理", icon: "✦", group: "模式" },
  { id: "code", name: "编程", desc: "写代码、读仓库、改 bug", icon: "</>", group: "模式" },
  { id: "write", name: "写作", desc: "润色、改写、长文", icon: "✎", group: "模式" },
  { id: "chat", name: "普通对话", desc: "回到默认聊天", icon: "○", group: "模式" },
  { id: "plan", name: "计划模式", desc: "先列方案再动手", icon: "☰", group: "模式" },
  { id: "deep-research", name: "深度研究工作流", desc: "后台调研并交叉验证来源", icon: "◎", group: "模式", aliases: ["deepresearch"] },

  { id: "new", name: "新对话", desc: "清空当前页，开始空白对话", icon: "+", group: "会话", aliases: ["clear"] },
  { id: "home", name: "回到首页", desc: "离开当前对话，回到欢迎页", icon: "⌂", group: "会话", aliases: ["welcome"] },
  { id: "resume", name: "恢复对话", desc: "在侧栏搜索并打开历史对话", icon: "↩", group: "会话" },
  { id: "rename", name: "重命名", desc: "给当前对话起个名字", icon: "✎", group: "会话", aliases: ["title"] },
  { id: "delete", name: "删除对话", desc: "删除当前网页对话", icon: "×", group: "会话" },
  { id: "copy", name: "复制回复", desc: "复制最近一条助手回复", icon: "⧉", group: "会话" },
  { id: "export", name: "导出对话", desc: "下载当前对话为 Markdown", icon: "↓", group: "会话" },
  { id: "compact", name: "压缩上下文", desc: "丢掉过旧轮次，腾出上下文", icon: "▣", group: "会话" },
  { id: "context", name: "上下文占用", desc: "看看当前对话用了多少内容", icon: "▤", group: "会话" },
  { id: "session-info", name: "会话信息", desc: "模型、轮次和来源", icon: "ℹ", group: "会话", aliases: ["status", "info"] },

  { id: "model", name: "切换模型", desc: "打开模型选择器", icon: "◆", group: "模型", aliases: ["m"] },
  { id: "effort", name: "推理强度", desc: "网页里由模型自己把握；可切到深度思考", icon: "▲", group: "模型" },

  { id: "workflow", name: "运行工作流", desc: "查看并启动本机 .rhai 工作流", icon: "▷", group: "工作流" },
  { id: "workflows", name: "工作流面板", desc: "列出已保存的 workflow", icon: "☰", group: "工作流" },
  { id: "goal", name: "目标", desc: "设定一个跨多轮的自主目标", icon: "★", group: "工作流" },
  { id: "loop", name: "定时循环", desc: "按间隔重复执行一句提示", icon: "↻", group: "工作流" },

  { id: "imagine", name: "生成图片", desc: "用文字描述生成图片", icon: "◈", group: "媒体" },
  { id: "imagine-video", name: "生成视频", desc: "用文字描述生成视频", icon: "▶", group: "媒体" },

  { id: "usage", name: "用量与账单", desc: "打开 xAI 控制台查看额度", icon: "$", group: "账户", aliases: ["cost"] },
  { id: "login", name: "重新登录", desc: "说明如何刷新 Grok 登录", icon: "→", group: "账户" },
  { id: "logout", name: "退出登录", desc: "清除网页里保存的自定义密钥", icon: "←", group: "账户" },
  { id: "privacy", name: "隐私设置", desc: "打开编码数据与保留相关说明", icon: "◌", group: "账户" },

  { id: "settings", name: "设置", desc: "打开本页设置", icon: "⚙", group: "配置", aliases: ["config", "preferences", "prefs"] },
  { id: "theme", name: "切换外观", desc: "浅色 / 深色", icon: "◐", group: "配置", aliases: ["t"] },
  { id: "docs", name: "文档", desc: "打开 Grok Build 文档", icon: "▤", group: "配置", aliases: ["howto", "guides"] },
  { id: "release-notes", name: "更新说明", desc: "查看 Grok 发行说明", icon: "✦", group: "配置", aliases: ["changelog"] },
  { id: "tutorial", name: "新手教程", desc: "打开入门指南", icon: "?", group: "配置", aliases: ["tour", "onboarding"] },
  { id: "feedback", name: "反馈", desc: "给这次体验留一句意见", icon: "✎", group: "配置" },
  { id: "doctor", name: "诊断", desc: "检查本页登录和接口是否正常", icon: "+", group: "配置", aliases: ["terminal-setup", "terminal-check"] },

  { id: "dashboard", name: "仪表盘", desc: "打开侧栏里的历史对话列表", icon: "▦", group: "智能体", aliases: ["sessions", "agents-dashboard"] },
  { id: "config-agents", name: "Agents", desc: "智能体定义在 CLI 里管理", icon: "♟", group: "智能体", aliases: ["agents"] },
  { id: "personas", name: "Personas", desc: "人设在 CLI 里管理", icon: "☺", group: "智能体" },
  { id: "skills", name: "Skills", desc: "查看已安装技能说明", icon: "⚒", group: "扩展" },
  { id: "plugins", name: "插件", desc: "插件在 CLI 的 /plugins 管理", icon: "▣", group: "扩展" },
  { id: "marketplace", name: "市场", desc: "打开官方插件市场说明", icon: "▣", group: "扩展" },
  { id: "hooks", name: "Hooks", desc: "钩子在 CLI 的 /hooks 管理", icon: "⤷", group: "扩展" },
  { id: "mcps", name: "MCP", desc: "MCP 服务器在 CLI 里配置", icon: "⬡", group: "扩展" },
  { id: "memory", name: "记忆", desc: "跨会话记忆需在 CLI 开启", icon: "◉", group: "扩展", aliases: ["mem"] },
  { id: "remember", name: "记住", desc: "记下一条笔记，写在下一句里", icon: "◉", group: "扩展" },
];

const state = {
  conversations: [],
  current: null,
  pendingFiles: [],
  sending: false,
  abort: null,
  model: localStorage.getItem("grok-model") || "grok-4.6",
  mode: localStorage.getItem("grok-mode") || "chat",
  slashOpen: false,
  slashIndex: 0,
  theme: localStorage.getItem("grok-theme") || "light",
  renameId: null,
  inspectId: null,
  leftW: Number(localStorage.getItem("grok-left-w")) || 280,
  rightW: Number(localStorage.getItem("grok-right-w")) || 340,
};

const els = {
  recents: $("recents"),
  search: $("search"),
  messages: $("messages"),
  hero: $("hero"),
  thread: $("thread"),
  input: $("input"),
  send: $("sendBtn"),
  chips: $("chips"),
  fileInput: $("fileInput"),
  greeting: $("greeting"),
  userName: $("userName"),
  userSub: $("userSub"),
  avatar: $("avatar"),
  modelBtn: $("modelBtn"),
  modelLabel: $("modelLabel"),
  modelMenu: $("modelMenu"),
  modelPicker: $("modelPicker"),
  composer: $("composer"),
  settings: $("settings"),
  slash: $("slash"),
  modeBar: $("modeBar"),
  authStatus: $("authStatus"),
  apiKey: $("apiKey"),
  sidebar: $("sidebar"),
  backdrop: $("sidebarBackdrop"),
  renameDialog: $("renameDialog"),
  renameInput: $("renameInput"),
  cmdDialog: $("cmdDialog"),
  cmdTitle: $("cmdTitle"),
  cmdBody: $("cmdBody"),
  inspect: $("inspect"),
  inspectBody: $("inspectBody"),
  gutterLeft: $("gutterLeft"),
  gutterRight: $("gutterRight"),
};

function applyWidths() {
  const app = $("app");
  if (!app) return;
  app.style.setProperty("--sidebar", `${state.leftW}px`);
  app.style.setProperty("--inspect", `${state.rightW}px`);
}

function bindGutter(el, side) {
  if (!el) return;
  el.addEventListener("pointerdown", (e) => {
    e.preventDefault();
    el.classList.add("dragging");
    const startX = e.clientX;
    const start = side === "left" ? state.leftW : state.rightW;
    const move = (ev) => {
      const dx = ev.clientX - startX;
      if (side === "left") state.leftW = Math.min(440, Math.max(200, start + dx));
      else state.rightW = Math.min(560, Math.max(260, start - dx));
      applyWidths();
    };
    const up = () => {
      el.classList.remove("dragging");
      window.removeEventListener("pointermove", move);
      localStorage.setItem(side === "left" ? "grok-left-w" : "grok-right-w", String(side === "left" ? state.leftW : state.rightW));
    };
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", up, { once: true });
  });
}

async function truncateBefore(id) {
  if (!state.current?.id) return;
  const updated = await api(`/api/conversations/${state.current.id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ truncate_before: id }),
  });
  state.current.messages = updated.messages || [];
  state.current.previous_response_id = updated.previous_response_id;
  renderMessages();
  renderRecents();
}

async function editUserMessage(id) {
  const msgs = state.current?.messages || [];
  const idx = msgs.findIndex((m) => m.id === id);
  if (idx < 0) return;
  const msg = msgs[idx];
  if (msg.source === "cli") return toast("CLI 原话只能复制");
  await truncateBefore(id);
  els.input.value = msg.content || "";
  resizeInput();
  syncSendButton();
  els.input.focus();
}

async function regenerateMessage(id) {
  const msgs = state.current?.messages || [];
  const idx = msgs.findIndex((m) => m.id === id);
  if (idx < 0) return;
  const user = [...msgs.slice(0, idx)].reverse().find((m) => m.role === "user");
  if (!user || user.source === "cli") return toast("这条不能重新生成");
  await truncateBefore(user.id);
  els.input.value = user.content || "";
  resizeInput();
  await send();
}

function openInspect(id) {
  state.inspectId = id;
  if (els.inspect) els.inspect.hidden = false;
  if (els.gutterRight) els.gutterRight.hidden = false;
  renderInspect();
}

function closeInspect() {
  state.inspectId = null;
  if (els.inspect) els.inspect.hidden = true;
  if (els.gutterRight) els.gutterRight.hidden = true;
}

function renderInspect() {
  if (!els.inspectBody) return;
  const msg = (state.current?.messages || []).find((m) => m.id === state.inspectId);
  const items = msg?.activity || [];
  if (!items.length) {
    els.inspectBody.innerHTML = `<div class="inspect-card"><span class="k">状态</span>${escapeHtml(msg?.status || "还没有可展示的工具过程")}</div>`;
    return;
  }
  els.inspectBody.innerHTML = items
    .map((item) => {
      if (item.kind === "think") {
        return `<div class="inspect-card"><span class="k">思考</span>${escapeHtml(item.text || "")}</div>`;
      }
      if (item.kind === "search") {
        return `<div class="inspect-card"><span class="k">搜索</span>${escapeHtml(item.query || "")}</div>`;
      }
      if (item.kind === "page") {
        const href = item.url || "";
        return `<div class="inspect-card"><span class="k">网页</span><a href="${escapeHtml(href)}" target="_blank" rel="noreferrer">${escapeHtml(item.title || href)}</a></div>`;
      }
      if (item.kind === "code") {
        return `<div class="inspect-card"><span class="k">代码</span><pre>${escapeHtml(item.text || "")}</pre></div>`;
      }
      return `<div class="inspect-card"><span class="k">步骤</span>${escapeHtml(item.text || item.query || "")}</div>`;
    })
    .join("");
}

function applyTheme() {
  document.documentElement.dataset.theme = state.theme;
  const light = $("hl-light");
  const dark = $("hl-dark");
  if (light) light.disabled = state.theme === "dark";
  if (dark) dark.disabled = state.theme !== "dark";
}

function greetingFor(name) {
  const hour = new Date().getHours();
  const hello = hour < 5 ? "夜深了" : hour < 12 ? "早上好" : hour < 18 ? "下午好" : "晚上好";
  return name ? `${hello}，${name}` : "今天想聊点什么？";
}

function fmtSize(n) {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / 1024 / 1024).toFixed(1)} MB`;
}

function extOf(name) {
  const parts = (name || "").split(".");
  return (parts.length > 1 ? parts.pop() : "FILE").slice(0, 4).toUpperCase();
}

function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function stripToolLeak(text) {
  return String(text || "")
    .replace(/```(?:html|xml|json|text|tool)?\s*(?:web_search|x_search|code_interpreter|code_execution|image_generation|view_image|file_search|attachment_search)\b[\s\S]*?```/gi, "")
    .replace(/<(?:web_search|x_search|code_interpreter|function_call|tool_call)\b[\s\S]*?<\/(?:web_search|x_search|code_interpreter|function_call|tool_call)>/gi, "")
    .replace(/(?:^|\n)\s*(?:web_search|x_search|code_interpreter)\s*\n\s*(?:query|arguments|code)\s*\n[\s\S]*?(?=\n\n|\n```|$)/gi, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

function extractMath(src) {
  const slots = [];
  const stash = (display, body) => {
    const key = `@@MATH${slots.length}@@`;
    slots.push({ display, body: body.trim() });
    return key;
  };
  const text = String(src || "")
    .replace(/\$\$([\s\S]+?)\$\$/g, (_, body) => stash(true, body))
    .replace(/\\\[([\s\S]+?)\\\]/g, (_, body) => stash(true, body))
    .replace(/\\\(([\s\S]+?)\\\)/g, (_, body) => stash(false, body))
    .replace(/\$([^$\n]+?)\$/g, (_, body) => stash(false, body));
  return { text, slots };
}

function renderMath(html, slots) {
  return html.replace(/@@MATH(\d+)@@/g, (_, i) => {
    const slot = slots[Number(i)];
    if (!slot) return "";
    if (window.katex) {
      try {
        return katex.renderToString(slot.body, {
          displayMode: slot.display,
          throwOnError: false,
          output: "html",
        });
      } catch {
        /* fall through */
      }
    }
    const tag = slot.display ? "div" : "span";
    return `<${tag} class="katex-fallback">${escapeHtml(slot.body)}</${tag}>`;
  });
}

function renderMarkdown(text) {
  const { text: stripped, slots } = extractMath(stripToolLeak(text || ""));
  if (!window.marked) {
    return renderMath(`<p>${escapeHtml(stripped).replace(/\n/g, "<br>")}</p>`, slots);
  }
  const raw = marked.parse(stripped, { async: false, gfm: true, breaks: false });
  const html = renderMath(
    window.DOMPurify
      ? DOMPurify.sanitize(raw, {
          USE_PROFILES: { html: true },
          ADD_TAGS: ["math", "annotation", "semantics", "mrow", "mi", "mo", "mn", "msup", "msub"],
        })
      : raw,
    slots
  );
  const wrap = document.createElement("div");
  wrap.innerHTML = html;
  wrap.querySelectorAll("table").forEach((table) => {
    const scroller = document.createElement("div");
    scroller.className = "table-wrap";
    scroller.innerHTML = `<div class="code-head"><span>table</span><button type="button" data-copy="table">复制</button></div><div class="table-scroll"></div>`;
    table.replaceWith(scroller);
    scroller.querySelector(".table-scroll").appendChild(table);
  });
  wrap.querySelectorAll("pre > code").forEach((code) => {
    const lang = [...code.classList].find((c) => c.startsWith("language-"))?.slice(9) || "";
    if (window.hljs) {
      try {
        if (lang && hljs.getLanguage(lang)) code.innerHTML = hljs.highlight(code.textContent, { language: lang }).value;
        else code.innerHTML = hljs.highlightAuto(code.textContent).value;
      } catch {
        /* keep raw */
      }
    }
    const pre = code.parentElement;
    const block = document.createElement("div");
    block.className = "code-block";
    block.innerHTML = `<div class="code-head"><span>${escapeHtml(lang || "code")}</span><button type="button" data-copy="code">复制</button></div>`;
    pre.replaceWith(block);
    block.appendChild(pre);
  });
  return wrap.innerHTML;
}

function tableToText(table) {
  return [...table.querySelectorAll("tr")]
    .map((row) =>
      [...row.children]
        .map((cell) => cell.innerText.replace(/\s+/g, " ").trim())
        .join("\t")
    )
    .join("\n");
}

async function copyText(text) {
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
      return true;
    }
  } catch {
    /* fallback */
  }
  const ta = document.createElement("textarea");
  ta.value = text;
  ta.setAttribute("readonly", "");
  ta.style.cssText = "position:fixed;left:-9999px;top:0";
  document.body.appendChild(ta);
  ta.select();
  ta.setSelectionRange(0, ta.value.length);
  const ok = document.execCommand("copy");
  ta.remove();
  return ok;
}

async function api(path, options = {}) {
  const res = await fetch(path, options);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || res.statusText || "请求失败");
  return data;
}

async function refreshHealth() {
  try {
    const health = await api("/api/health");
    const name = health.user?.name || "";
    els.greeting.textContent = greetingFor(name);
    els.userName.textContent = name || "本地用户";
    els.avatar.textContent = (name || "G").slice(0, 1).toUpperCase();
    if (!health.ok) {
      els.userSub.textContent = health.expired ? "登录已过期" : "未登录";
      els.authStatus.textContent = health.expired
        ? "Grok 登录已过期，请在终端运行 grok login。"
        : "未找到凭证。请运行 grok login，或在下方填入 XAI_API_KEY。";
    } else {
      const src =
        health.source === "grok" ? "已使用当前 Grok 登录" : health.source === "env" ? "使用环境变量密钥" : "使用自定义密钥";
      els.userSub.textContent = src;
      els.authStatus.textContent = `${src}${health.user?.email ? ` · ${health.user.email}` : ""}`;
    }
    return health;
  } catch (err) {
    els.authStatus.textContent = err.message;
    return null;
  }
}

function dateGroup(iso) {
  if (!iso) return "更早";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "更早";
  const start = (x) => new Date(x.getFullYear(), x.getMonth(), x.getDate()).getTime();
  const diff = (start(new Date()) - start(d)) / 86400000;
  if (diff < 1) return "今天";
  if (diff < 2) return "昨天";
  if (diff < 7) return "近 7 天";
  if (diff < 30) return "近 30 天";
  return "更早";
}

function renderRecents() {
  const q = els.search.value.trim().toLowerCase();
  const items = state.conversations.filter(
    (c) => !q || (c.title || "").toLowerCase().includes(q) || (c.preview || "").toLowerCase().includes(q)
  );
  if (!items.length) {
    els.recents.innerHTML = `<div class="empty-recents">${q ? "没有匹配的对话" : "还没有对话"}</div>`;
    return;
  }
  const groups = [];
  for (const c of items) {
    const label = dateGroup(c.updated_at || c.created_at);
    if (!groups.length || groups[groups.length - 1].label !== label) groups.push({ label, items: [] });
    groups[groups.length - 1].items.push(c);
  }
  els.recents.innerHTML = groups
    .map(
      (g) =>
        `<div class="group-label">${g.label}</div>` +
        g.items
          .map(
            (c) => `
      <div class="conv ${state.current?.id === c.id ? "active" : ""}" data-id="${c.id}">
        <span class="conv-title">${escapeHtml(c.title || "新对话")}</span>
        ${c.source === "cli" ? `<span class="badge">CLI</span>` : ""}
        <button class="conv-menu" data-menu="${c.id}" type="button" aria-label="更多">
          <svg viewBox="0 0 24 24" fill="currentColor"><circle cx="6" cy="12" r="1.4"/><circle cx="12" cy="12" r="1.4"/><circle cx="18" cy="12" r="1.4"/></svg>
        </button>
      </div>`
          )
          .join("")
    )
    .join("");
}

function fileChipHtml(file, removable) {
  if (file.kind === "image") {
    return `<div class="chip" data-id="${file.id}">
      <img src="${file.url}" alt="">
      <span>${escapeHtml(file.name)}</span>
      ${removable ? `<button type="button" data-remove="${file.id}" aria-label="移除">×</button>` : ""}
    </div>`;
  }
  return `<div class="chip" data-id="${file.id}">
    <span class="ext">${escapeHtml(extOf(file.name))}</span>
    <span>${escapeHtml(file.name)}${file.size ? ` · ${fmtSize(file.size)}` : ""}</span>
    ${removable ? `<button type="button" data-remove="${file.id}" aria-label="移除">×</button>` : ""}
  </div>`;
}

function renderPendingFiles() {
  if (!state.pendingFiles.length) {
    els.chips.hidden = true;
    els.chips.innerHTML = "";
    return;
  }
  els.chips.hidden = false;
  els.chips.innerHTML = state.pendingFiles.map((f) => fileChipHtml(f, true)).join("");
}

function renderAttachments(files) {
  if (!files?.length) return "";
  return `<div class="attachments">${files
    .map((f) =>
      f.kind === "image"
        ? `<a class="thumb" href="${f.url}" target="_blank" rel="noreferrer"><img src="${f.url}" alt="${escapeHtml(f.name)}"></a>`
        : `<a class="file-chip" href="${f.url}" target="_blank" rel="noreferrer"><span class="ext">${escapeHtml(extOf(f.name))}</span><span>${escapeHtml(f.name)}</span></a>`
    )
    .join("")}</div>`;
}

function renderTools(tools) {
  if (!tools?.length) return "";
  return tools.map((t) => `<span class="tool-row">${escapeHtml(t.title || "工具")}</span>`).join("");
}

function setWelcome(empty) {
  $("main")?.classList.toggle("welcome", empty);
}

function renderMessages() {
  const messages = state.current?.messages || [];
  if (!messages.length) {
    els.hero.hidden = false;
    els.messages.hidden = true;
    els.messages.innerHTML = "";
    setWelcome(true);
    return;
  }
  setWelcome(false);
  els.hero.hidden = true;
  els.messages.hidden = false;
  const origin =
    state.current?.source === "cli"
      ? `<div class="origin">来自 Grok CLI${state.current.cwd ? ` · ${escapeHtml(state.current.cwd)}` : ""}，可以在这里继续聊</div>`
      : "";
  els.messages.innerHTML =
    origin +
    messages
      .map((m) => {
        if (m.role === "user") {
          return `<div class="turn user" data-id="${m.id}">
          <div>
            ${renderAttachments(m.files)}
            ${m.content ? `<div class="bubble">${escapeHtml(m.content)}</div>` : ""}
            <div class="msg-actions right">
              <button type="button" data-msg="copy" data-id="${m.id}">复制</button>
              ${m.source === "cli" ? "" : `<button type="button" data-msg="edit" data-id="${m.id}">编辑</button>`}
            </div>
          </div>
        </div>`;
        }
        const pending = m.pending && !m.content;
        return `<div class="turn assistant" data-id="${m.id}">
        ${renderTools(m.tools)}
        ${m.status || pending || m.activity?.length ? `<button class="status" type="button" data-inspect="${m.id}">${pending ? `<span class="dots"><i></i><i></i><i></i></span>` : ""}<span>${escapeHtml(m.status || (m.activity?.length ? "查看过程" : "思考中"))}</span></button>` : ""}
        ${m.content ? `<div class="md">${renderMarkdown(m.content)}</div>` : ""}
        ${m.error ? `<div class="error-banner">${escapeHtml(m.error)}</div>` : ""}
        ${m.content || m.error ? `<div class="msg-actions">
          <button type="button" data-msg="copy" data-id="${m.id}">复制</button>
          ${m.source === "cli" || pending ? "" : `<button type="button" data-msg="regen" data-id="${m.id}">重新生成</button>`}
        </div>` : ""}
      </div>`;
      })
      .join("");
  if (state.stickToBottom !== false) {
    els.thread.scrollTop = els.thread.scrollHeight;
  }
  if (state.inspectId) renderInspect();
}

function syncSendButton() {
  const has = els.input.value.trim() || state.pendingFiles.length;
  els.send.disabled = !state.sending && !has;
  els.send.classList.toggle("busy", state.sending);
  els.send.setAttribute("aria-label", state.sending ? "停止" : "发送");
}

function resizeInput() {
  const el = els.input;
  el.style.height = "36px";
  if (!el.value) return;
  el.style.height = `${Math.min(Math.max(el.scrollHeight, 36), 220)}px`;
}

async function loadConversations() {
  const data = await api("/api/conversations");
  state.conversations = data.conversations || [];
  renderRecents();
}

async function openConversation(id) {
  if (!id) {
    state.current = null;
    renderMessages();
    renderRecents();
    closeSidebar();
    els.input.focus();
    return;
  }
  const item = await api(`/api/conversations/${id}`);
  state.current = item;
  if (item.model) setModel(item.model, false);
  renderMessages();
  renderRecents();
  closeSidebar();
  els.thread.scrollTop = els.thread.scrollHeight;
}

async function newChat() {
  state.current = null;
  state.pendingFiles = [];
  renderPendingFiles();
  renderMessages();
  renderRecents();
  closeSidebar();
  els.input.value = "";
  resizeInput();
  syncSendButton();
  els.input.focus();
}

async function addFiles(fileList) {
  for (const file of [...fileList]) {
    const body = new FormData();
    body.append("file", file);
    const uploaded = await api("/api/upload", { method: "POST", body });
    state.pendingFiles.push(uploaded);
  }
  renderPendingFiles();
  syncSendButton();
}

async function send() {
  if (state.sending) {
    state.abort?.abort();
    return;
  }
  let text = els.input.value.trim();
  if (text.startsWith("/")) {
    const parts = text.slice(1).trim().split(/\s+/);
    const cmd = findSlash(parts[0] || "");
    const arg = parts.slice(1).join(" ");
    if (cmd) {
      const asChat = {
        imagine: arg && `请生成一张图，画面是：${arg}`,
        "imagine-video": arg && `请构想一段短视频并写出分镜：${arg}`,
        goal: arg && `把这件事当作跨多轮目标来推进：${arg}`,
        loop: arg && `请按这个循环任务执行：${arg}`,
        remember: arg && `请记住：${arg}`,
        feedback: arg && `产品反馈：${arg}`,
        workflow: arg && `请按这个 workflow 的目标来做：${arg}`,
      };
      if (asChat[cmd.id]) {
        text = asChat[cmd.id];
        if (cmd.id === "imagine" || cmd.id === "imagine-video") setMode("write");
        if (cmd.id === "goal" || cmd.id === "workflow") setMode("think");
      } else {
        els.input.value = "";
        resizeInput();
        hideSlash();
        runSlash(cmd, arg);
        return;
      }
    }
  }
  if (!text && !state.pendingFiles.length) return;

  const files = [...state.pendingFiles];
  els.input.value = "";
  state.pendingFiles = [];
  renderPendingFiles();
  resizeInput();

  const tempUser = {
    id: `tmp-user-${Date.now()}`,
    role: "user",
    content: text,
    files,
    created_at: new Date().toISOString(),
  };
  const tempAsst = {
    id: `tmp-asst-${Date.now()}`,
    role: "assistant",
    content: "",
    pending: true,
    status: "思考中",
    activity: [],
    files: [],
  };
  if (!state.current) {
    state.current = { id: null, title: "新对话", messages: [] };
  }
  state.current.messages.push(tempUser, tempAsst);
  renderMessages();

  state.sending = true;
  syncSendButton();
  const controller = new AbortController();
  state.abort = controller;

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        conversation_id: state.current.id,
        message: text,
        file_ids: files.map((f) => f.id),
        model: state.model,
        mode: state.mode,
        web_search: state.mode === "web" || state.mode === "research",
      }),
      signal: controller.signal,
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.error || "发送失败");
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const chunks = buffer.split("\n\n");
      buffer = chunks.pop() || "";
      for (const chunk of chunks) {
        const line = chunk.split("\n").find((l) => l.startsWith("data:"));
        if (!line) continue;
        const event = JSON.parse(line.slice(5).trim());
        if (event.type === "start") {
          tempUser.id = event.user_message.id;
          tempUser.files = event.user_message.files || files;
          tempAsst.id = event.assistant_id;
          state.current.id = event.conversation.id;
          state.current.title = event.conversation.title;
        } else if (event.type === "status") {
          tempAsst.status = event.text;
        } else if (event.type === "activity") {
          tempAsst.activity = tempAsst.activity || [];
          tempAsst.activity.push(event.entry);
          if (state.inspectId === tempAsst.id) renderInspect();
        } else if (event.type === "delta") {
          tempAsst.content += event.text;
        } else if (event.type === "error") {
          tempAsst.error = event.message;
          tempAsst.pending = false;
        } else if (event.type === "done") {
          tempAsst.content = event.text || tempAsst.content;
          tempAsst.pending = false;
          if (event.activity) tempAsst.activity = event.activity;
          tempAsst.status = tempAsst.activity?.length ? "查看过程" : "";
          if (event.conversation) {
            state.current.title = event.conversation.title;
            state.current.id = event.conversation.id;
          }
        }
        renderMessages();
      }
    }
  } catch (err) {
    if (err.name !== "AbortError") {
      tempAsst.error = err.message;
    } else if (!tempAsst.content) {
      tempAsst.error = "已停止";
    }
    tempAsst.pending = false;
    tempAsst.status = "";
    renderMessages();
  } finally {
    state.sending = false;
    state.abort = null;
    syncSendButton();
    await loadConversations();
    renderRecents();
    els.input.focus();
  }
}

function findSlash(id) {
  const key = (id || "").toLowerCase();
  return SLASH.find((m) => m.id === key || (m.aliases || []).includes(key));
}

function slashNeedle(item) {
  return [item.id, item.name, ...(item.aliases || [])].join(" ").toLowerCase();
}

function filteredSlash() {
  const raw = els.input.value;
  if (!raw.startsWith("/")) return [];
  const q = raw.slice(1).trim().toLowerCase();
  if (!q) return SLASH;
  return SLASH.filter((m) => slashNeedle(m).includes(q) || m.id.startsWith(q));
}

function toast(text) {
  document.querySelector(".toast")?.remove();
  const el = document.createElement("div");
  el.className = "toast";
  el.textContent = text;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 2200);
}

function showPanel(title, html) {
  if (!els.cmdDialog) return toast(title);
  els.cmdTitle.textContent = title;
  els.cmdBody.innerHTML = html;
  els.cmdDialog.showModal();
}

function draftCommand(prefix, hint) {
  els.input.value = prefix.endsWith(" ") ? prefix : `${prefix} `;
  hideSlash();
  resizeInput();
  syncSendButton();
  els.input.focus();
  if (hint) toast(hint);
}

function setMode(id) {
  if (!MODE_IDS.has(id) && id !== "plan" && id !== "deep-research") return;
  const mapped = id === "deep-research" || id === "plan" ? (id === "plan" ? "think" : "research") : id;
  state.mode = mapped === "chat" ? "chat" : mapped;
  if (id === "plan") state.mode = "think";
  if (id === "deep-research") state.mode = "research";
  localStorage.setItem("grok-mode", state.mode);
  renderModeBar();
  hideSlash();
  if (els.input.value.startsWith("/")) {
    els.input.value = "";
    resizeInput();
    syncSendButton();
  }
  els.input.focus();
}

function renderModeBar() {
  const mode = SLASH.find((m) => m.id === state.mode && MODE_IDS.has(m.id) && m.id !== "chat");
  if (!mode) {
    els.modeBar.hidden = true;
    els.modeBar.innerHTML = "";
    return;
  }
  els.modeBar.hidden = false;
  els.modeBar.innerHTML = `<span class="mode-chip">${escapeHtml(mode.icon)} ${escapeHtml(mode.name)}<button type="button" data-clear-mode aria-label="取消模式">×</button></span>`;
}

async function runSlash(item, arg = "") {
  hideSlash();
  const id = item.id;
  if (MODE_IDS.has(id) || id === "plan" || id === "deep-research") {
    setMode(id);
    if (id === "deep-research" && arg) {
      els.input.value = arg;
      resizeInput();
      send();
    }
    return;
  }
  if (id === "new" || id === "home") return newChat();
  if (id === "resume" || id === "dashboard") {
    openSidebar();
    els.search.focus();
    toast("在侧栏搜索或点开一段对话");
    return;
  }
  if (id === "rename") {
    if (!state.current?.id) return toast("先打开一段对话");
    state.renameId = state.current.id;
    els.renameInput.value = state.current.title || "";
    els.renameDialog.showModal();
    els.renameInput.focus();
    return;
  }
  if (id === "delete") {
    if (!state.current?.id || String(state.current.id).startsWith("cli:")) return toast("只能删除网页对话");
    await api(`/api/conversations/${state.current.id}`, { method: "DELETE" });
    await newChat();
    await loadConversations();
    return;
  }
  if (id === "copy") {
    const last = [...(state.current?.messages || [])].reverse().find((m) => m.role === "assistant" && m.content);
    if (!last) return toast("还没有可复制的回复");
    await navigator.clipboard.writeText(last.content);
    toast("已复制");
    return;
  }
  if (id === "export") {
    const msgs = state.current?.messages || [];
    if (!msgs.length) return toast("当前没有对话");
    const md = msgs.map((m) => `## ${m.role === "user" ? "User" : "Grok"}\n\n${m.content || ""}`).join("\n\n");
    const blob = new Blob([md], { type: "text/markdown" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `${(state.current.title || "chat").replace(/[^\w\u4e00-\u9fff-]+/g, "_")}.md`;
    a.click();
    return;
  }
  if (id === "compact") {
    toast("网页对话会按轮次发送，无需手动 compact");
    return;
  }
  if (id === "context" || id === "session-info") {
    const msgs = state.current?.messages || [];
    const chars = msgs.reduce((n, m) => n + (m.content || "").length, 0);
    showPanel(item.name, `<p class="status-line">标题：${escapeHtml(state.current?.title || "新对话")}<br>来源：${escapeHtml(state.current?.source || "web")}<br>模型：${escapeHtml(state.model)}<br>模式：${escapeHtml(state.mode)}<br>消息：${msgs.length} 条<br>大约 ${chars} 字</p>`);
    return;
  }
  if (id === "model") {
    openModelMenu();
    return;
  }
  if (id === "effort") {
    setMode("think");
    toast("已切到深度思考");
    return;
  }
  if (id === "theme") {
    state.theme = state.theme === "dark" ? "light" : "dark";
    localStorage.setItem("grok-theme", state.theme);
    applyTheme();
    toast(state.theme === "dark" ? "已切换到深色" : "已切换到浅色");
    return;
  }
  if (id === "settings") {
    refreshHealth();
    els.settings.showModal();
    return;
  }
  if (id === "usage") {
    const extra = await api("/api/extras").catch(() => ({ usage_url: "https://console.x.ai" }));
    showPanel("用量与账单", `<p class="status-line">额度、账单和发票在 xAI 控制台里。</p><div class="actions"><a class="primary-btn" href="${extra.usage_url || "https://console.x.ai"}" target="_blank" rel="noreferrer">打开 Usage</a></div>`);
    return;
  }
  if (id === "docs" || id === "tutorial" || id === "release-notes") {
    const extra = await api("/api/extras").catch(() => ({}));
    const url =
      id === "docs" || id === "tutorial"
        ? extra.docs_url || "https://docs.x.ai/build/overview"
        : "https://docs.x.ai";
    window.open(url, "_blank", "noopener");
    return;
  }
  if (id === "privacy") {
    window.open("https://docs.x.ai/developers/faq/security", "_blank", "noopener");
    return;
  }
  if (id === "login") {
    showPanel("重新登录", `<p class="status-line">在终端运行 <code>grok login</code>，然后刷新这个页面。网页会自动使用新的 Grok 会话。</p>`);
    return;
  }
  if (id === "logout") {
    await api("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ clear_api_key: true }),
    });
    await refreshHealth();
    toast("已清除自定义密钥。CLI 登录仍可用");
    return;
  }
  if (id === "workflow" || id === "workflows") {
    const extra = await api("/api/extras").catch(() => ({ workflows: [] }));
    const rows = (extra.workflows || [])
      .map((w) => `<div class="slash-item" style="pointer-events:none"><span><span class="slash-name">${escapeHtml(w.name)}</span><span class="slash-desc">${escapeHtml(w.path)}</span></span></div>`)
      .join("");
    showPanel(
      "工作流",
      `${rows || `<p class="status-line">还没有保存的 workflow。把 .rhai 放到 ~/.grok/workflows/。</p>`}
      <p class="help">网页可以浏览这些定义。真正跑 workflow / goal 请在终端用 <code>grok</code> 的 /workflow。</p>`
    );
    return;
  }
  if (id === "goal") return draftCommand("/goal", "补上目标内容后发送，会按目标模式继续聊");
  if (id === "loop") return draftCommand("/loop", "格式：/loop 30m 检查部署状态");
  if (id === "imagine") return draftCommand("/imagine", "补上画面描述后发送");
  if (id === "imagine-video") return draftCommand("/imagine-video", "补上镜头描述后发送");
  if (id === "remember") return draftCommand("/remember", "补上要记住的内容");
  if (id === "feedback") return draftCommand("/feedback", "补上一句反馈");
  if (id === "doctor") {
    const health = await refreshHealth();
    showPanel(
      "诊断",
      `<p class="status-line">服务：${health?.ok ? "正常" : "未登录或凭证失效"}<br>凭证来源：${escapeHtml(health?.source || "unknown")}<br>地址：http://127.0.0.1:8787</p>`
    );
    return;
  }
  if (id === "skills" || id === "plugins" || id === "marketplace" || id === "hooks" || id === "mcps" || id === "memory" || id === "config-agents" || id === "personas") {
    showPanel(
      item.name,
      `<p class="status-line">/${escapeHtml(id)} 属于 Grok CLI 的智能体能力。在终端里打开 <code>grok</code> 再输入 /${escapeHtml(id)}。</p>`
    );
    return;
  }
  toast(`/${id} 还不能在网页里执行`);
}

function currentModel() {
  return MODELS.find((m) => m.id === state.model) || MODELS[0];
}

function renderModelMenu() {
  els.modelLabel.textContent = currentModel().name;
  els.modelMenu.innerHTML = MODELS.map(
    (m) => `<button type="button" class="model-option ${m.id === state.model ? "active" : ""}" data-model="${m.id}" role="option">
      <span><span class="name">${escapeHtml(m.name)}</span><span class="desc">${escapeHtml(m.desc)}</span></span>
      <span class="check">${m.id === state.model ? "✓" : ""}</span>
    </button>`
  ).join("");
}

function setModel(id, persist = true) {
  if (!MODELS.some((m) => m.id === id)) return;
  state.model = id;
  if (persist) localStorage.setItem("grok-model", id);
  renderModelMenu();
  closeModelMenu();
}

function openModelMenu() {
  renderModelMenu();
  els.modelMenu.hidden = false;
  els.modelPicker.classList.add("open");
  els.modelBtn.setAttribute("aria-expanded", "true");
}

function closeModelMenu() {
  els.modelMenu.hidden = true;
  els.modelPicker.classList.remove("open");
  els.modelBtn.setAttribute("aria-expanded", "false");
}

function hideSlash() {
  state.slashOpen = false;
  els.slash.hidden = true;
  els.slash.innerHTML = "";
  els.composer?.classList.remove("has-slash");
}

function renderSlash() {
  const items = filteredSlash();
  if (!els.input.value.startsWith("/") || !items.length) {
    hideSlash();
    return;
  }
  state.slashOpen = true;
  if (state.slashIndex >= items.length) state.slashIndex = 0;
  els.slash.hidden = false;
  els.composer?.classList.add("has-slash");
  let lastGroup = "";
  const rows = items
    .map((m, i) => {
      const head = m.group !== lastGroup ? `<div class="slash-group">${escapeHtml(m.group)}</div>` : "";
      lastGroup = m.group;
      return `${head}<button type="button" class="slash-item ${i === state.slashIndex ? "active" : ""}" data-cmd="${m.id}">
        <span class="slash-icon">${escapeHtml(m.icon)}</span>
        <span><span class="slash-name">/${escapeHtml(m.id)} · ${escapeHtml(m.name)}</span><span class="slash-desc">${escapeHtml(m.desc)}</span></span>
      </button>`;
    })
    .join("");
  els.slash.innerHTML = `<div class="slash-head">命令</div>${rows}`;
}

function closeMenu() {
  document.querySelector(".menu")?.remove();
  document.querySelectorAll(".conv-menu.open").forEach((el) => el.classList.remove("open"));
}

function openMenu(btn, id) {
  closeMenu();
  btn.classList.add("open");
  const menu = document.createElement("div");
  menu.className = "menu";
  const isCli = String(id).startsWith("cli:");
  menu.innerHTML = isCli
    ? `<button type="button" data-act="rename">重命名</button>`
    : `<button type="button" data-act="rename">重命名</button>
    <button type="button" data-act="delete" class="danger">删除</button>`;
  document.body.appendChild(menu);
  const rect = btn.getBoundingClientRect();
  menu.style.top = `${rect.bottom + 4}px`;
  menu.style.left = `${Math.min(rect.right - 148, window.innerWidth - 160)}px`;
  menu.addEventListener("click", async (e) => {
    const act = e.target.closest("button")?.dataset.act;
    closeMenu();
    if (act === "rename") {
      state.renameId = id;
      const item = state.conversations.find((c) => c.id === id);
      els.renameInput.value = item?.title || "";
      els.renameDialog.showModal();
      els.renameInput.focus();
      els.renameInput.select();
    } else if (act === "delete") {
      await api(`/api/conversations/${id}`, { method: "DELETE" });
      if (state.current?.id === id) await newChat();
      await loadConversations();
    }
  });
}

function openSidebar() {
  els.sidebar.classList.add("open");
  els.backdrop.hidden = false;
}

function closeSidebar() {
  els.sidebar.classList.remove("open");
  els.backdrop.hidden = true;
}

function bindEvents() {
  $("newChat").addEventListener("click", newChat);
  $("brandBtn").addEventListener("click", newChat);
  $("openSidebar").addEventListener("click", openSidebar);
  $("closeSidebar").addEventListener("click", closeSidebar);
  els.backdrop.addEventListener("click", closeSidebar);
  $("themeBtn").addEventListener("click", () => {
    state.theme = state.theme === "dark" ? "light" : "dark";
    localStorage.setItem("grok-theme", state.theme);
    applyTheme();
  });
  $("attachBtn").addEventListener("click", () => els.fileInput.click());
  els.fileInput.addEventListener("change", async () => {
    if (els.fileInput.files.length) await addFiles(els.fileInput.files);
    els.fileInput.value = "";
  });
  els.chips.addEventListener("click", (e) => {
    const id = e.target.dataset.remove;
    if (!id) return;
    state.pendingFiles = state.pendingFiles.filter((f) => f.id !== id);
    renderPendingFiles();
    syncSendButton();
  });
  els.recents.addEventListener("click", (e) => {
    const menuBtn = e.target.closest("[data-menu]");
    if (menuBtn) {
      e.stopPropagation();
      openMenu(menuBtn, menuBtn.dataset.menu);
      return;
    }
    const row = e.target.closest(".conv");
    if (row) openConversation(row.dataset.id);
  });
  document.addEventListener("click", (e) => {
    if (!e.target.closest(".menu") && !e.target.closest(".conv-menu")) closeMenu();
    if (!e.target.closest("#modelPicker")) closeModelMenu();
  });
  els.modelBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    if (els.modelMenu.hidden) openModelMenu();
    else closeModelMenu();
  });
  els.modelMenu.addEventListener("click", (e) => {
    const id = e.target.closest("[data-model]")?.dataset.model;
    if (id) setModel(id);
  });
  els.search.addEventListener("input", renderRecents);
  els.input.addEventListener("input", () => {
    resizeInput();
    syncSendButton();
    if (els.input.value.startsWith("/")) renderSlash();
    else hideSlash();
  });
  let composing = false;
  let composeEndedAt = 0;
  els.input.addEventListener("compositionstart", () => {
    composing = true;
  });
  els.input.addEventListener("compositionend", () => {
    composing = false;
    composeEndedAt = Date.now();
  });
  els.input.addEventListener("keydown", (e) => {
    if (composing || e.isComposing || e.keyCode === 229 || Date.now() - composeEndedAt < 80) {
      return;
    }
    if (state.slashOpen) {
      const items = filteredSlash();
      if (e.key === "ArrowDown") {
        e.preventDefault();
        state.slashIndex = (state.slashIndex + 1) % Math.max(items.length, 1);
        renderSlash();
        return;
      }
      if (e.key === "ArrowUp") {
        e.preventDefault();
        state.slashIndex = (state.slashIndex - 1 + items.length) % Math.max(items.length, 1);
        renderSlash();
        return;
      }
      if (e.key === "Enter" || e.key === "Tab") {
        e.preventDefault();
        if (items[state.slashIndex]) runSlash(items[state.slashIndex]);
        return;
      }
      if (e.key === "Escape") {
        e.preventDefault();
        hideSlash();
        return;
      }
    }
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  });
  els.send.addEventListener("click", send);
  els.slash.addEventListener("click", (e) => {
    const id = e.target.closest("[data-cmd]")?.dataset.cmd;
    const item = id && findSlash(id);
    if (item) runSlash(item);
  });
  els.modeBar.addEventListener("click", (e) => {
    if (e.target.closest("[data-clear-mode]")) setMode("chat");
  });
  $("starters")?.addEventListener("click", (e) => {
    const id = e.target.closest("[data-mode]")?.dataset.mode;
    if (id) {
      setMode(id);
      els.input.focus();
    }
  });
  $("openSettings").addEventListener("click", () => {
    refreshHealth();
    els.settings.showModal();
  });
  $("saveKey").addEventListener("click", async () => {
    await api("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ api_key: els.apiKey.value }),
    });
    els.apiKey.value = "";
    await refreshHealth();
  });
  $("clearKey").addEventListener("click", async () => {
    await api("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ clear_api_key: true }),
    });
    els.apiKey.value = "";
    await refreshHealth();
  });
  $("renameConfirm").addEventListener("click", async (e) => {
    e.preventDefault();
    if (state.renameId) {
      await api(`/api/conversations/${state.renameId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: els.renameInput.value }),
      });
      if (state.current?.id === state.renameId) state.current.title = els.renameInput.value;
      await loadConversations();
    }
    els.renameDialog.close();
  });

  els.thread.addEventListener("click", async (e) => {
    const inspectBtn = e.target.closest("[data-inspect]");
    if (inspectBtn) {
      openInspect(inspectBtn.dataset.inspect);
      return;
    }
    const act = e.target.closest("[data-msg]");
    if (act) {
      const kind = act.dataset.msg;
      const id = act.dataset.id;
      if (kind === "copy") {
        const msg = (state.current?.messages || []).find((m) => m.id === id);
        if (!msg?.content) return toast("没有可复制的内容");
        const ok = await copyText(msg.content);
        act.textContent = ok ? "已复制" : "复制失败";
        setTimeout(() => {
          act.textContent = "复制";
        }, 1200);
      } else if (kind === "edit") {
        await editUserMessage(id);
      } else if (kind === "regen") {
        await regenerateMessage(id);
      }
      return;
    }
    const btn = e.target.closest("[data-copy]");
    if (!btn) return;
    e.preventDefault();
    const box = btn.closest(".code-block, .table-wrap");
    let text = "";
    if (box?.classList.contains("code-block")) {
      text = box.querySelector("pre")?.innerText || "";
    } else if (box?.classList.contains("table-wrap")) {
      const table = box.querySelector("table");
      text = table ? tableToText(table) : "";
    }
    if (!text.trim()) {
      toast("没有可复制的内容");
      return;
    }
    const ok = await copyText(text);
    const prev = btn.textContent;
    btn.textContent = ok ? "已复制" : "复制失败";
    setTimeout(() => {
      btn.textContent = prev;
    }, 1400);
  });
  els.thread.addEventListener("scroll", () => {
    const nearBottom = els.thread.scrollHeight - els.thread.scrollTop - els.thread.clientHeight < 80;
    state.stickToBottom = nearBottom;
  });

  window.addEventListener("keydown", (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "n") {
      e.preventDefault();
      newChat();
    }
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      els.search.focus();
    }
  });

  els.input.addEventListener("paste", async (e) => {
    const files = [...(e.clipboardData?.files || [])];
    if (files.length) {
      e.preventDefault();
      await addFiles(files);
    }
  });

  const isFileDrag = (e) => [...(e.dataTransfer?.types || [])].includes("Files");
  window.addEventListener("dragover", (e) => {
    if (isFileDrag(e)) e.preventDefault();
  });
  window.addEventListener("drop", async (e) => {
    if (!isFileDrag(e)) return;
    e.preventDefault();
    const files = [...(e.dataTransfer?.files || [])];
    if (files.length) await addFiles(files);
  });
}

async function init() {
  applyTheme();
  if (window.marked?.setOptions) marked.setOptions({ gfm: true, breaks: false });
  bindEvents();
  applyWidths();
  bindGutter(els.gutterLeft, "left");
  bindGutter(els.gutterRight, "right");
  $("closeInspect")?.addEventListener("click", closeInspect);
  renderModelMenu();
  renderModeBar();
  syncSendButton();
  await refreshHealth();
  await loadConversations();
  els.input.focus();
}

init();
