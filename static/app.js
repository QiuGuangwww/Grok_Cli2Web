const $ = (id) => document.getElementById(id);

const MODELS = [
  { id: "grok-4.6", name: "Grok 4.6", desc: "最强推理，适合难问题和长任务" },
  { id: "grok-4.5", name: "Grok 4.5", desc: "更均衡，日常对话更快一些" },
  { id: "grok-4.3", name: "Grok 4.3", desc: "超长上下文，适合大文档" },
];

const EFFORTS = [
  { id: "low", name: "Low", desc: "更快，适合简单问题和工具调用" },
  { id: "medium", name: "Medium", desc: "更均衡，适合分析和长上下文" },
  { id: "high", name: "High", desc: "默认。更深，适合难题和多步推理" },
  { id: "xhigh", name: "Extra high", desc: "最深，更慢，适合最难的问题" },
];

const THEMES = [
  { id: "light", key: "theme.light", dark: false },
  { id: "paper", key: "theme.paper", dark: false },
  { id: "moss", key: "theme.moss", dark: false },
  { id: "azure", key: "theme.azure", dark: false },
  { id: "dark", key: "theme.dark", dark: true },
  { id: "midnight", key: "theme.midnight", dark: true },
  { id: "dusk", key: "theme.dusk", dark: true },
  { id: "cyber", key: "theme.cyber", dark: true },
];

const GREET = {
  zh: {
    late: ["夜深了", "夜已深", "夜色正好"],
    morning: ["早上好", "早安", "新的一天"],
    afternoon: ["下午好", "午安"],
    evening: ["晚上好", "傍晚好", "夜色渐起"],
    named: ["{hello}，{name}", "{name}，{hello}", "{hello}，{name}。"],
    plain: ["今天想聊点什么？", "有什么想开始的？", "我们聊点什么？", "想做点什么？"],
  },
  en: {
    late: ["Still up", "Late night", "Quiet hours"],
    morning: ["Good morning", "Morning", "Hello"],
    afternoon: ["Good afternoon", "Afternoon", "Hello"],
    evening: ["Good evening", "Evening", "Hello"],
    named: ["{hello}, {name}", "{hello}, {name}."],
    plain: ["What's next?", "Shall we begin?", "What's on your mind?", "What shall we do?"],
  },
  ja: {
    late: ["夜ですね", "夜更かしです", "静かな時間です"],
    morning: ["おはよう", "おはようございます"],
    afternoon: ["こんにちは"],
    evening: ["こんばんは", "夕方ですね"],
    named: ["{hello}、{name}", "{hello}、{name}。"],
    plain: ["何をしますか？", "始めましょうか？", "何を話しますか？"],
  },
};

const LANGS = [
  { id: "zh", name: "中文", short: "中文" },
  { id: "en", name: "English", short: "EN" },
  { id: "ja", name: "日本語", short: "日本語" },
];

const I18N = {
  zh: {
    brand: "Grok",
    newChat: "新对话",
    "search.placeholder": "搜索对话",
    "user.localChat": "本地对话",
    "user.local": "本地用户",
    appearance: "外观",
    "greeting.plain": "今天想聊点什么？",
    "greeting.late": "夜深了",
    "greeting.morning": "早上好",
    "greeting.afternoon": "下午好",
    "greeting.evening": "晚上好",
    attach: "上传文件",
    "input.placeholder": "问任何问题，或输入 / 选择模式",
    send: "发送",
    stop: "停止",
    close: "关闭",
    "aria.closeSidebar": "关闭侧栏",
    "aria.openSidebar": "打开侧栏",
    "starter.research": "深度研究",
    "starter.code": "写代码",
    "starter.write": "帮我写作",
    "starter.web": "查一下网页",
    "starter.multi": "多 Agent",
    "inspect.process": "过程",
    "inspect.team": "团队",
    "inspect.think": "思考",
    "inspect.search": "搜索",
    "inspect.page": "网页",
    "inspect.code": "代码",
    "inspect.step": "步骤",
    "inspect.ledger": "进度板",
    "inspect.phase": "状态机",
    "phase.planning": "拆任务",
    "phase.running": "专员工作中",
    "phase.aligning": "步骤对齐",
    "phase.reviewing": "审核中",
    "phase.reworking": "打回重做",
    "phase.asking": "等你选择",
    "phase.synthesizing": "总控汇总",
    "phase.done": "完成",
    "phase.stopped": "已停止",
    "phase.runningNow": "正在跑",
    "phase.sentBack": "已打回",
    "phase.stop": "停止原因",
    "phase.planVer": "计划版本",
    "phase.score": "收敛",
    "inspect.task": "任务",
    "inspect.deps": "依赖",
    "inspect.depsOf": "基于 {names} 继续",
    "inspect.plan": "计划",
    "inspect.output": "产出",
    "inspect.status": "状态",
    "inspect.empty": "还没有可展示的工具过程",
    "inspect.graph": "关系",
    "inspect.graphLive": "工作中",
    "inspect.graphLink": "对齐中",
    "inspect.graphAsk": "反馈",
    "inspect.feedback": "转交",
    "inspect.guide": "指导",
    "inspect.guideTo": "指导「{name}」",
    "inspect.guidePh": "补一句方向或下一步",
    "inspect.guideSend": "送出",
    "inspect.guideHint": "结束后会按你的话继续",
    "inspect.guideSent": "已送出，代理会按这个方向继续",
    "inspect.guideLate": "这一轮已经结束",
    "inspect.wait": "等{names}",
    settings: "设置",
    "tab.account": "账号",
    "tab.agents": "多 Agent",
    "tab.appearance": "外观",
    "tab.language": "语言",
    "lang.help": "选择界面语言。",
    "auth.status": "登录状态",
    "auth.checking": "检查中…",
    "auth.keyLabel": "API 密钥（可选）",
    "auth.keyPh": "留空则沿用当前登录",
    "auth.keyHelp": "密钥仅保存在此设备，可用于覆盖当前登录。",
    "auth.clear": "清除自定义密钥",
    "auth.save": "保存密钥",
    "auth.expiredSub": "登录已过期",
    "auth.noneSub": "未登录",
    "auth.expired": "Grok 登录已过期，请在终端运行 grok login。",
    "auth.missing": "未找到凭证。请运行 grok login，或在下方填入 XAI_API_KEY。",
    "auth.grok": "已使用当前 Grok 登录",
    "auth.env": "使用环境变量密钥",
    "auth.custom": "使用自定义密钥",
    "agents.lead": "总控模型",
    "agents.leadHelp": "用于拆分任务并生成最终回答。",
    "agents.worker": "子代理模型",
    "agents.workerHelp": "用于执行各项子任务。滑块是上限，实际人数按任务需要决定。",
    "agents.count": "子代理上限",
    "agents.warn": "上限较高时响应可能变慢，费用也会增加。建议不超过 8。",
    "agents.warnUse8": "改为 8",
    "theme.label": "主题",
    "theme.light": "浅色",
    "theme.paper": "素纸",
    "theme.moss": "松绿",
    "theme.azure": "青空",
    "theme.dark": "深色",
    "theme.midnight": "午夜",
    "theme.dusk": "暮色",
    "theme.cyber": "赛博",
    "theme.hint": "预览并选择外观。",
    "lang.label": "语言",
    cmd: "命令",
    "ask.head": "需要你选一下",
    "ask.other": "其他",
    "ask.otherDesc": "自己写方向",
    "ask.otherPh": "写下你的选择",
    "rename.title": "重命名对话",
    cancel: "取消",
    save: "保存",
    copy: "复制",
    copied: "已复制",
    copyFail: "复制失败",
    edit: "编辑",
    regen: "重新生成",
    "date.today": "今天",
    "date.yesterday": "昨天",
    "date.week": "近 7 天",
    "date.month": "近 30 天",
    "date.older": "更早",
    "empty.none": "还没有对话",
    "empty.miss": "没有匹配的对话",
    "origin.cli": "来自 Grok CLI",
    "origin.cont": "，可在此继续",
    thinking: "思考中",
    "view.process": "查看过程",
    "view.team": "查看团队",
    "agent.planning": "拆任务",
    "agent.waiting": "等待中",
    "agent.queued": "排队",
    "agent.blocked": "对齐中",
    "agent.stepLead": "步骤总控",
    "agent.running": "工作中",
    "agent.stopped": "已停止",
    "agent.writing": "汇总中",
    "agent.done": "完成",
    "agent.error": "失败",
    "agent.lead": "总控",
    "agent.worker": "子代理",
    "agent.reviewer": "审核",
    "agent.sent_back": "已打回",
    "agent.partial": "部分完成",
    "req.fail": "请求失败",
    "toast.saved": "已保存",
    "toast.fillKey": "请先输入 API 密钥。",
    "theme.lightOn": "已切换到浅色",
    "theme.darkOn": "已切换到深色",
    "group.mode": "模式",
    "group.session": "会话",
    "group.model": "模型",
    "group.workflow": "工作流",
    "group.media": "媒体",
    "group.account": "账户",
    "group.config": "配置",
    "group.agent": "智能体",
    "group.ext": "扩展",
    "model.grok-4.6.desc": "最强推理，适合难问题和长任务",
    "model.grok-4.5.desc": "更均衡，日常对话更快一些",
    "model.grok-4.3.desc": "超长上下文，适合大文档",
    "effort.low.desc": "更快，适合简单问题和工具调用",
    "effort.medium.desc": "更均衡，适合分析和长上下文",
    "effort.high.desc": "默认。更深，适合难题和多步推理",
    "effort.xhigh.desc": "最深，更慢，适合最难的问题",
  },
  en: {
    brand: "Grok",
    newChat: "New chat",
    "search.placeholder": "Search chats",
    "user.localChat": "Local chat",
    "user.local": "Local user",
    appearance: "Appearance",
    "greeting.plain": "What do you want to talk about?",
    "greeting.late": "Still up",
    "greeting.morning": "Good morning",
    "greeting.afternoon": "Good afternoon",
    "greeting.evening": "Good evening",
    attach: "Upload file",
    "input.placeholder": "Ask anything, or type / for modes",
    send: "Send",
    stop: "Stop",
    close: "Close",
    "aria.closeSidebar": "Close sidebar",
    "aria.openSidebar": "Open sidebar",
    "starter.research": "Deep research",
    "starter.code": "Write code",
    "starter.write": "Help me write",
    "starter.web": "Search the web",
    "starter.multi": "Multi-agent",
    "inspect.process": "Process",
    "inspect.team": "Team",
    "inspect.think": "Thinking",
    "inspect.search": "Search",
    "inspect.page": "Page",
    "inspect.code": "Code",
    "inspect.step": "Step",
    "inspect.ledger": "Progress board",
    "inspect.phase": "State",
    "phase.planning": "Planning",
    "phase.running": "Workers running",
    "phase.aligning": "Aligning",
    "phase.reviewing": "Reviewing",
    "phase.reworking": "Reworking",
    "phase.asking": "Waiting on you",
    "phase.synthesizing": "Synthesizing",
    "phase.done": "Done",
    "phase.stopped": "Stopped",
    "phase.runningNow": "Running",
    "phase.sentBack": "Sent back",
    "phase.stop": "Stop reason",
    "phase.planVer": "Plan version",
    "phase.score": "Convergence",
    "inspect.task": "Task",
    "inspect.deps": "Depends on",
    "inspect.depsOf": "Continues from {names}",
    "inspect.plan": "Plan",
    "inspect.output": "Output",
    "inspect.status": "Status",
    "inspect.empty": "Nothing to show yet",
    "inspect.graph": "Graph",
    "inspect.graphLive": "Working",
    "inspect.graphLink": "Aligning",
    "inspect.graphAsk": "Feedback",
    "inspect.feedback": "Routed",
    "inspect.guide": "Guidance",
    "inspect.guideTo": "Guide {name}",
    "inspect.guidePh": "A direction or next step",
    "inspect.guideSend": "Send",
    "inspect.guideHint": "Applies after this turn",
    "inspect.guideSent": "Sent. This agent will follow that direction.",
    "inspect.guideLate": "This run has already finished",
    "inspect.wait": "Waiting on {names}",
    settings: "Settings",
    "tab.account": "Account",
    "tab.agents": "Multi-agent",
    "tab.appearance": "Appearance",
    "tab.language": "Language",
    "lang.help": "Choose the language for the interface.",
    "auth.status": "Sign-in",
    "auth.checking": "Checking…",
    "auth.keyLabel": "API key (optional)",
    "auth.keyPh": "Leave blank to keep the current sign-in",
    "auth.keyHelp": "The key is stored only on this device and can override the current sign-in.",
    "auth.clear": "Clear custom key",
    "auth.save": "Save key",
    "auth.expiredSub": "Login expired",
    "auth.noneSub": "Not signed in",
    "auth.expired": "Grok login expired. Run grok login in a terminal.",
    "auth.missing": "No credentials. Run grok login, or paste an XAI_API_KEY below.",
    "auth.grok": "Using current Grok login",
    "auth.env": "Using environment key",
    "auth.custom": "Using custom key",
    "agents.lead": "Lead model",
    "agents.leadHelp": "Plans the work and writes the final answer.",
    "agents.worker": "Sub-agent model",
    "agents.workerHelp": "Carries out individual subtasks. The slider is a maximum, not a fixed team size.",
    "agents.count": "Sub-agent limit",
    "agents.warn": "A higher limit can be slower and cost more. 8 is a good ceiling.",
    "agents.warnUse8": "Use 8",
    "theme.label": "Theme",
    "theme.light": "Light",
    "theme.paper": "Paper",
    "theme.moss": "Moss",
    "theme.azure": "Azure",
    "theme.dark": "Dark",
    "theme.midnight": "Midnight",
    "theme.dusk": "Dusk",
    "theme.cyber": "Cyber",
    "theme.hint": "Preview and choose an appearance.",
    "lang.label": "Language",
    cmd: "Commands",
    "ask.head": "Pick one",
    "ask.other": "Other",
    "ask.otherDesc": "Write your own",
    "ask.otherPh": "Type your choice",
    "rename.title": "Rename chat",
    cancel: "Cancel",
    save: "Save",
    copy: "Copy",
    copied: "Copied",
    copyFail: "Copy failed",
    edit: "Edit",
    regen: "Regenerate",
    "date.today": "Today",
    "date.yesterday": "Yesterday",
    "date.week": "Past 7 days",
    "date.month": "Past 30 days",
    "date.older": "Older",
    "empty.none": "No chats yet",
    "empty.miss": "No matching chats",
    "origin.cli": "From Grok CLI",
    "origin.cont": ". You can continue here",
    thinking: "Thinking",
    "view.process": "View process",
    "view.team": "View team",
    "agent.planning": "Planning",
    "agent.waiting": "Waiting",
    "agent.queued": "Queued",
    "agent.blocked": "Aligning",
    "agent.stepLead": "Step lead",
    "agent.running": "Working",
    "agent.stopped": "Stopped",
    "agent.writing": "Synthesizing",
    "agent.done": "Done",
    "agent.error": "Failed",
    "agent.lead": "Lead",
    "agent.worker": "Sub-agent",
    "agent.reviewer": "Reviewer",
    "agent.sent_back": "Sent back",
    "agent.partial": "Partial",
    "req.fail": "Request failed",
    "toast.saved": "Saved",
    "toast.fillKey": "Enter an API key first.",
    "theme.lightOn": "Switched to light",
    "theme.darkOn": "Switched to dark",
    "group.mode": "Modes",
    "group.session": "Chat",
    "group.model": "Model",
    "group.workflow": "Workflows",
    "group.media": "Media",
    "group.account": "Account",
    "group.config": "Config",
    "group.agent": "Agents",
    "group.ext": "Extensions",
    "model.grok-4.6.desc": "Strongest reasoning for hard, long tasks",
    "model.grok-4.5.desc": "More balanced, a bit faster day to day",
    "model.grok-4.3.desc": "Very long context for large documents",
    "effort.low.desc": "Faster, good for simple questions and tools",
    "effort.medium.desc": "Balanced, good for analysis and long context",
    "effort.high.desc": "Default. Deeper, for hard multi-step work",
    "effort.xhigh.desc": "Deepest and slowest, for the hardest problems",
  },
  ja: {
    brand: "Grok",
    newChat: "新しい会話",
    "search.placeholder": "会話を検索",
    "user.localChat": "ローカル会話",
    "user.local": "ローカルユーザー",
    appearance: "外観",
    "greeting.plain": "今日は何を話しますか？",
    "greeting.late": "夜更かしですね",
    "greeting.morning": "おはようございます",
    "greeting.afternoon": "こんにちは",
    "greeting.evening": "こんばんは",
    attach: "ファイルをアップロード",
    "input.placeholder": "何でも聞くか、/ でモードを選ぶ",
    send: "送信",
    stop: "停止",
    close: "閉じる",
    "aria.closeSidebar": "サイドバーを閉じる",
    "aria.openSidebar": "サイドバーを開く",
    "starter.research": "深掘り調査",
    "starter.code": "コードを書く",
    "starter.write": "文章を頼む",
    "starter.web": "ウェブを調べる",
    "starter.multi": "マルチエージェント",
    "inspect.process": "過程",
    "inspect.team": "チーム",
    "inspect.think": "思考",
    "inspect.search": "検索",
    "inspect.page": "ページ",
    "inspect.code": "コード",
    "inspect.step": "手順",
    "inspect.ledger": "進捗ボード",
    "inspect.phase": "状態機械",
    "phase.planning": "分割中",
    "phase.running": "作業中",
    "phase.aligning": "同期中",
    "phase.reviewing": "レビュー中",
    "phase.reworking": "差戻し",
    "phase.asking": "選択待ち",
    "phase.synthesizing": "まとめ中",
    "phase.done": "完了",
    "phase.stopped": "停止",
    "phase.runningNow": "実行中",
    "phase.sentBack": "差戻し",
    "phase.stop": "停止理由",
    "phase.planVer": "計画版",
    "phase.score": "収束",
    "inspect.task": "任務",
    "inspect.deps": "依存",
    "inspect.depsOf": "{names} を引き継いで続行",
    "inspect.plan": "計画",
    "inspect.output": "出力",
    "inspect.status": "状態",
    "inspect.empty": "まだ表示できる過程がありません",
    "inspect.graph": "関係",
    "inspect.graphLive": "作業中",
    "inspect.graphLink": "同期中",
    "inspect.graphAsk": "依頼",
    "inspect.feedback": "回送",
    "inspect.guide": "指導",
    "inspect.guideTo": "「{name}」を指導",
    "inspect.guidePh": "方向や次の一手を書く",
    "inspect.guideSend": "送る",
    "inspect.guideHint": "今の一巡のあとで反映",
    "inspect.guideSent": "送りました。この方向で続けます",
    "inspect.guideLate": "このラウンドは終了しています",
    "inspect.wait": "{names} 待ち",
    settings: "設定",
    "tab.account": "アカウント",
    "tab.agents": "マルチエージェント",
    "tab.appearance": "外観",
    "tab.language": "言語",
    "lang.help": "表示言語を選択します。",
    "auth.status": "ログイン状態",
    "auth.checking": "確認中…",
    "auth.keyLabel": "API キー（任意）",
    "auth.keyPh": "空欄なら現在のログインを継続",
    "auth.keyHelp": "キーはこのデバイスにのみ保存され、現在のログインを上書きできます。",
    "auth.clear": "カスタムキーを消す",
    "auth.save": "キーを保存",
    "auth.expiredSub": "ログイン期限切れ",
    "auth.noneSub": "未ログイン",
    "auth.expired": "Grok ログインの期限が切れました。端末で grok login を実行してください。",
    "auth.missing": "認証情報が見つかりません。grok login するか、下に XAI_API_KEY を入れてください。",
    "auth.grok": "現在の Grok ログインを使用中",
    "auth.env": "環境変数のキーを使用中",
    "auth.custom": "カスタムキーを使用中",
    "agents.lead": "リードモデル",
    "agents.leadHelp": "任務の分割と最終回答を担当します。",
    "agents.worker": "サブエージェントモデル",
    "agents.workerHelp": "各サブタスクを実行します。スライダーは上限であり、必ずその人数になるわけではありません。",
    "agents.count": "サブエージェント上限",
    "agents.warn": "上限を上げると遅くなり、費用も増えます。8 以下を推奨します。",
    "agents.warnUse8": "8 にする",
    "theme.label": "テーマ",
    "theme.light": "ライト",
    "theme.paper": "紙",
    "theme.moss": "モス",
    "theme.azure": "青空",
    "theme.dark": "ダーク",
    "theme.midnight": "ミッドナイト",
    "theme.dusk": "黄昏",
    "theme.cyber": "サイバー",
    "theme.hint": "外観をプレビューして選択します。",
    "lang.label": "言語",
    cmd: "コマンド",
    "ask.head": "選んでください",
    "ask.other": "その他",
    "ask.otherDesc": "自分で書く",
    "ask.otherPh": "選択を入力",
    "rename.title": "会話名を変更",
    cancel: "キャンセル",
    save: "保存",
    copy: "コピー",
    copied: "コピーしました",
    copyFail: "コピーに失敗",
    edit: "編集",
    regen: "再生成",
    "date.today": "今日",
    "date.yesterday": "昨日",
    "date.week": "過去 7 日",
    "date.month": "過去 30 日",
    "date.older": "それ以前",
    "empty.none": "まだ会話がありません",
    "empty.miss": "一致する会話がありません",
    "origin.cli": "Grok CLI から",
    "origin.cont": "。ここで続行できます",
    thinking: "考え中",
    "view.process": "過程を見る",
    "view.team": "チームを見る",
    "agent.planning": "分割中",
    "agent.waiting": "待機",
    "agent.queued": "待機列",
    "agent.blocked": "同期中",
    "agent.stepLead": "ステップリード",
    "agent.running": "作業中",
    "agent.stopped": "停止",
    "agent.writing": "まとめ中",
    "agent.done": "完了",
    "agent.error": "失敗",
    "agent.lead": "リード",
    "agent.worker": "サブエージェント",
    "agent.reviewer": "レビュー",
    "agent.sent_back": "差戻し",
    "agent.partial": "一部完了",
    "req.fail": "リクエスト失敗",
    "toast.saved": "保存しました",
    "toast.fillKey": "先に API キーを入力してください。",
    "theme.lightOn": "ライトに切り替えました",
    "theme.darkOn": "ダークに切り替えました",
    "group.mode": "モード",
    "group.session": "会話",
    "group.model": "モデル",
    "group.workflow": "ワークフロー",
    "group.media": "メディア",
    "group.account": "アカウント",
    "group.config": "設定",
    "group.agent": "エージェント",
    "group.ext": "拡張",
    "model.grok-4.6.desc": "最も強い推論。難しい長時間タスク向け",
    "model.grok-4.5.desc": "バランス型。日常はもう少し速い",
    "model.grok-4.3.desc": "超長文脈。大きな文書向け",
    "effort.low.desc": "速い。簡単な質問とツール向け",
    "effort.medium.desc": "均衡。分析と長文脈向け",
    "effort.high.desc": "既定。難しい多段推論向け",
    "effort.xhigh.desc": "最も深く遅い。最難問向け",
  },
};

const MODE_IDS = new Set(["research", "web", "think", "code", "write", "chat", "multi"]);

const SLASH = [
  { id: "research", name: "深度研究", desc: "多步检索，交叉验证，输出结构化报告", icon: "◎", group: "模式" },
  { id: "web", name: "联网搜索", desc: "查最新网页、新闻和事实", icon: "⌕", group: "模式" },
  { id: "think", name: "深度思考", desc: "更慢、更严谨地推理", icon: "✦", group: "模式" },
  { id: "code", name: "编程", desc: "写代码、读仓库、改 bug", icon: "</>", group: "模式" },
  { id: "write", name: "写作", desc: "润色、改写、长文", icon: "✎", group: "模式" },
  { id: "chat", name: "普通对话", desc: "回到默认聊天", icon: "○", group: "模式" },
  { id: "plan", name: "计划模式", desc: "先列方案再动手", icon: "☰", group: "模式" },
  { id: "deep-research", name: "深度研究工作流", desc: "后台调研并交叉验证来源", icon: "◎", group: "模式", aliases: ["deepresearch"] },
  { id: "multi", name: "多 Agent", desc: "总控拆任务，子代理并行，再汇总", icon: "♟", group: "模式", aliases: ["agents", "crew"] },

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
  { id: "effort", name: "推理强度", desc: "Low / Medium / High / Extra high", icon: "▲", group: "模型" },

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
  { id: "config-agents", name: "Agents 设置", desc: "打开设置里的总控 / 子代理模型", icon: "♟", group: "智能体" },
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
  effort: localStorage.getItem("grok-effort") || "high",
  mode: localStorage.getItem("grok-mode") || "chat",
  slashOpen: false,
  slashIndex: 0,
  theme: localStorage.getItem("grok-theme") || "light",
  renameId: null,
  lang: localStorage.getItem("grok-lang") || "zh",
  userName: "",
  inspectId: null,
  inspectAgent: "lead",
  crewRunId: null,
  ask: null,
  askIndex: 0,
  askOther: false,
  graphDrag: null,
  agentSettings: {
    lead_model: "grok-4.6",
    lead_effort: "high",
    worker_model: "grok-4.5",
    worker_effort: "medium",
    worker_count: 3,
  },
  settingsTab: "account",
  leftW: Number(localStorage.getItem("grok-left-w")) || 280,
  rightW: Number(localStorage.getItem("grok-right-w")) || 340,
  graphH: Number(localStorage.getItem("grok-graph-h")) || 220,
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
  effortBtn: $("effortBtn"),
  effortLabel: $("effortLabel"),
  effortMenu: $("effortMenu"),
  effortPicker: $("effortPicker"),
  composer: $("composer"),
  settings: $("settings"),
  slash: $("slash"),
  modeChip: $("modeChip"),
  themePanel: $("themePanel"),
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
  inspectRoster: $("inspectRoster"),
  inspectDetail: $("inspectDetail"),
  inspectGraph: $("inspectGraph"),
  inspectGuide: $("inspectGuide"),
  inspectGuideLabel: $("inspectGuideLabel"),
  inspectGuideInput: $("inspectGuideInput"),
  inspectGuideSend: $("inspectGuideSend"),
  inspectGuideHint: $("inspectGuideHint"),
  agentGraph: $("agentGraph"),
  gutterLeft: $("gutterLeft"),
  gutterRight: $("gutterRight"),
  gutterGraph: $("gutterGraph"),
};

function t(key, vars) {
  const pack = I18N[state.lang] || I18N.zh;
  let s = pack[key] ?? I18N.zh[key] ?? I18N.en[key] ?? key;
  if (vars) {
    for (const [k, v] of Object.entries(vars)) s = String(s).replaceAll(`{${k}}`, String(v));
  }
  return s;
}

const SLASH_I18N = {
  en: {
    research: ["Deep research", "Multi-step retrieval and a structured report"],
    web: ["Web search", "Latest pages, news, and facts"],
    think: ["Think harder", "Slower, more careful reasoning"],
    code: ["Code", "Write, read, and fix code"],
    write: ["Write", "Edit, rewrite, long form"],
    chat: ["Chat", "Back to normal chat"],
    plan: ["Plan mode", "Outline first, then act"],
    "deep-research": ["Deep research workflow", "Background research with source checks"],
    multi: ["Multi-agent", "Lead splits work, specialists run, then merge"],
    new: ["New chat", "Clear this page and start over"],
    home: ["Home", "Leave this chat and go to the welcome screen"],
    resume: ["Resume", "Search the sidebar and open a past chat"],
    rename: ["Rename", "Name this chat"],
    delete: ["Delete chat", "Delete this web chat"],
    copy: ["Copy reply", "Copy the latest assistant reply"],
    export: ["Export", "Download this chat as Markdown"],
    compact: ["Compact", "Drop older turns to free context"],
    context: ["Context use", "See how much this chat is using"],
    "session-info": ["Session info", "Model, turns, and source"],
    model: ["Switch model", "Open the model picker"],
    effort: ["Reasoning effort", "Low / Medium / High / Extra high"],
    workflow: ["Run workflow", "Browse local .rhai workflows"],
    workflows: ["Workflows", "List saved workflows"],
    goal: ["Goal", "Set a goal that spans turns"],
    loop: ["Loop", "Repeat a prompt on an interval"],
    imagine: ["Image", "Generate an image from text"],
    "imagine-video": ["Video", "Describe a short video"],
    usage: ["Usage & billing", "Open the xAI console"],
    login: ["Sign in again", "How to refresh Grok login"],
    logout: ["Sign out", "Clear the custom key saved in this page"],
    privacy: ["Privacy", "Data retention notes"],
    settings: ["Settings", "Open this page’s settings"],
    theme: ["Appearance", "Light / dark"],
    docs: ["Docs", "Open Grok Build docs"],
    "release-notes": ["Release notes", "See what’s new"],
    tutorial: ["Tutorial", "Open the getting-started guide"],
    feedback: ["Feedback", "Leave a note about this session"],
    doctor: ["Doctor", "Check login and this page’s API"],
    dashboard: ["Dashboard", "Open the sidebar chat list"],
    "config-agents": ["Agent settings", "Lead / worker models in settings"],
    personas: ["Personas", "Managed in the CLI"],
    skills: ["Skills", "Installed skill notes"],
    plugins: ["Plugins", "Managed with /plugins in the CLI"],
    marketplace: ["Marketplace", "Official plugin marketplace notes"],
    hooks: ["Hooks", "Managed with /hooks in the CLI"],
    mcps: ["MCP", "Configure MCP servers in the CLI"],
    memory: ["Memory", "Cross-chat memory is in the CLI"],
    remember: ["Remember", "Write a note in the next message"],
  },
  ja: {
    research: ["深掘り調査", "多段検索と構造化レポート"],
    web: ["ウェブ検索", "最新のページ・ニュース・事実"],
    think: ["深く考える", "より遅く、慎重に推論する"],
    code: ["コード", "書く、読む、直す"],
    write: ["執筆", "推敲、書き換え、長文"],
    chat: ["通常会話", "デフォルトのチャットに戻る"],
    plan: ["計画モード", "先に方針、それから実行"],
    "deep-research": ["深掘りワークフロー", "裏で調べて出典を照合"],
    multi: ["マルチエージェント", "リードが分割し、専門家が走り、まとめる"],
    new: ["新しい会話", "このページを空にして始める"],
    home: ["ホーム", "会話を離れて歓迎画面へ"],
    resume: ["再開", "サイドバーから過去の会話を開く"],
    rename: ["名前を変更", "この会話に名前を付ける"],
    delete: ["会話を削除", "このウェブ会話を削除"],
    copy: ["返信をコピー", "最新のアシスタント返信をコピー"],
    export: ["書き出し", "Markdown でダウンロード"],
    compact: ["圧縮", "古いターンを捨てて文脈を空ける"],
    context: ["文脈", "この会話の使用量を見る"],
    "session-info": ["セッション情報", "モデル、ターン、出典"],
    model: ["モデル切替", "モデル選択を開く"],
    effort: ["推論の強さ", "Low / Medium / High / Extra high"],
    workflow: ["ワークフロー", "ローカルの .rhai を見る"],
    workflows: ["ワークフロー一覧", "保存済みを列挙"],
    goal: ["目標", "複数ターンにまたがる目標"],
    loop: ["ループ", "間隔を置いて同じ指示を繰り返す"],
    imagine: ["画像", "文章から画像を生成"],
    "imagine-video": ["動画", "短い動画を構想"],
    usage: ["利用量と請求", "xAI コンソールを開く"],
    login: ["再ログイン", "Grok ログインの更新方法"],
    logout: ["ログアウト", "このページのカスタムキーを消す"],
    privacy: ["プライバシー", "保持に関する説明"],
    settings: ["設定", "このページの設定を開く"],
    theme: ["外観", "ライト / ダーク"],
    docs: ["ドキュメント", "Grok Build を開く"],
    "release-notes": ["リリースノート", "更新内容"],
    tutorial: ["チュートリアル", "入門ガイド"],
    feedback: ["フィードバック", "今回の感想を残す"],
    doctor: ["診断", "ログインと API を確認"],
    dashboard: ["ダッシュボード", "サイドバーの履歴"],
    "config-agents": ["エージェント設定", "設定のリード / ワーカー"],
    personas: ["ペルソナ", "CLI で管理"],
    skills: ["スキル", "導入済みの説明"],
    plugins: ["プラグイン", "CLI の /plugins"],
    marketplace: ["マーケット", "公式プラグインの説明"],
    hooks: ["Hooks", "CLI の /hooks"],
    mcps: ["MCP", "CLI で MCP を設定"],
    memory: ["記憶", "横断記憶は CLI"],
    remember: ["覚える", "次の文にメモを書く"],
  },
};

const GROUP_KEY = {
  模式: "group.mode",
  会话: "group.session",
  模型: "group.model",
  工作流: "group.workflow",
  媒体: "group.media",
  账户: "group.account",
  配置: "group.config",
  智能体: "group.agent",
  扩展: "group.ext",
};

function slashName(item) {
  const row = (SLASH_I18N[state.lang] || {})[item.id];
  return row ? row[0] : item.name;
}

function slashDesc(item) {
  const row = (SLASH_I18N[state.lang] || {})[item.id];
  return row ? row[1] : item.desc;
}

function setLang(id, persist = true) {
  if (!LANGS.some((l) => l.id === id)) return;
  state.lang = id;
  if (persist) localStorage.setItem("grok-lang", id);
  applyI18n();
  refreshHealth();
}

function cycleLang() {
  setLang(state.lang === "zh" ? "en" : "zh");
}

function applyI18n() {
  const htmlLang = state.lang === "en" ? "en" : state.lang === "ja" ? "ja" : "zh-CN";
  document.documentElement.lang = htmlLang;
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(el.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    el.placeholder = t(el.dataset.i18nPlaceholder);
  });
  document.querySelectorAll("[data-i18n-title]").forEach((el) => {
    el.title = t(el.dataset.i18nTitle);
  });
  document.querySelectorAll("[data-i18n-aria]").forEach((el) => {
    el.setAttribute("aria-label", t(el.dataset.i18nAria));
  });
  const langMeta = LANGS.find((l) => l.id === state.lang) || LANGS[0];
  if ($("langBtn")) {
    $("langBtn").textContent = langMeta.short;
    $("langBtn").title = state.lang === "zh" ? "Switch to English" : "切换到中文";
  }
  document.querySelectorAll("[data-lang-set]").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.langSet === state.lang);
  });
  document.querySelectorAll("[data-theme-set]").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.themeSet === state.theme);
  });
  if (els.greeting && (!state.current?.messages || !state.current.messages.length)) {
    refreshGreeting();
  }
  renderThemeCards();
  renderModeChip();
  renderModelMenu();
  renderEffortMenu();
  fillAgentSelects();
  setSettingsTab(state.settingsTab || "account");
  renderRecents();
  if (state.current?.messages?.length) renderMessages();
  if (state.slashOpen) renderSlash();
}

function syncRightPane() {
  const inspectOn = els.inspect && !els.inspect.hidden;
  const themeOn = els.themePanel && !els.themePanel.hidden;
  if (els.gutterRight) els.gutterRight.hidden = !(inspectOn || themeOn);
}

function openThemePanel() {
  closeInspect();
  if (els.themePanel) els.themePanel.hidden = false;
  document.querySelectorAll("[data-theme-set]").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.themeSet === state.theme);
  });
  syncRightPane();
}

function closeThemePanel() {
  if (els.themePanel) els.themePanel.hidden = true;
  syncRightPane();
}

function applyWidths() {
  const app = $("app");
  if (!app) return;
  app.style.setProperty("--sidebar", `${state.leftW}px`);
  app.style.setProperty("--inspect", `${state.rightW}px`);
  if (els.inspect) els.inspect.style.setProperty("--graph", `${state.graphH}px`);
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
      if (side === "left") state.leftW = Math.min(520, Math.max(180, start + dx));
      else state.rightW = Math.min(640, Math.max(240, start - dx));
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

function bindGraphGutter(el) {
  if (!el) return;
  el.addEventListener("pointerdown", (e) => {
    e.preventDefault();
    el.classList.add("dragging");
    const startY = e.clientY;
    const start = state.graphH;
    const box = els.inspect?.clientHeight || 640;
    const move = (ev) => {
      const max = Math.max(140, box - 160);
      state.graphH = Math.min(max, Math.max(120, start - (ev.clientY - startY)));
      applyWidths();
    };
    const up = () => {
      el.classList.remove("dragging");
      window.removeEventListener("pointermove", move);
      localStorage.setItem("grok-graph-h", String(state.graphH));
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

function openInspect(id, agentId) {
  const msg = (state.current?.messages || []).find((m) => m.id === id);
  if (!msg) {
    closeInspect();
    return;
  }
  closeThemePanel();
  state.inspectId = id;
  state.inspectAgent = agentId || "";
  if (els.inspect) els.inspect.hidden = false;
  syncRightPane();
  renderInspect();
}

function closeInspect() {
  state.inspectId = null;
  state.inspectAgent = "";
  state.inspectRosterKey = "";
  stopAgentGraph();
  if (els.inspect) els.inspect.hidden = true;
  if (els.inspectGraph) els.inspectGraph.hidden = true;
  if (els.gutterGraph) els.gutterGraph.hidden = true;
  if (els.inspectGuide) els.inspectGuide.hidden = true;
  syncRightPane();
}

function messageInCurrent(id) {
  return Boolean(id && (state.current?.messages || []).some((m) => m.id === id));
}

function agentLabel(status, role) {
  if (role === "step-lead" && (!status || status === "queued" || status === "waiting")) return t("agent.stepLead");
  if (role === "reviewer" && (!status || status === "queued" || status === "waiting" || status === "blocked")) return t("agent.reviewer");
  const key = `agent.${status}`;
  const label = t(key);
  return label === key ? status || "" : label;
}

function modelName(id) {
  return (MODELS.find((m) => m.id === id) || {}).name || id || "";
}

function effortName(id) {
  return (EFFORTS.find((e) => e.id === id) || {}).name || id || "";
}

function upsertAgent(msg, patch) {
  if (!msg || !patch?.id) return;
  msg.agents = msg.agents || [];
  const i = msg.agents.findIndex((a) => a.id === patch.id);
  if (i >= 0) msg.agents[i] = { ...msg.agents[i], ...patch };
  else msg.agents.push({ content: "", activity: [], ...patch });
}

function findAgent(msg, id) {
  return (msg?.agents || []).find((a) => a.id === id);
}

const LIVE_AGENT = new Set(["running", "planning", "writing", "queued", "blocked", "waiting"]);

function stopCrewMessage(msg) {
  if (!msg) return;
  msg.pending = false;
  msg.status = t("agent.stopped");
  if (msg.phase) {
    msg.phase = { ...msg.phase, phase: "stopped", running: [], stop: "aborted" };
  }
  for (const agent of msg.agents || []) {
    if (LIVE_AGENT.has(agent.status) || agent.status === "sent_back") {
      agent.status = "stopped";
    }
  }
}

function visibleActivity(items) {
  return (items || []).filter((item) => item && item.kind !== "think");
}

function hasInspectableProcess(msg) {
  if (!msg) return false;
  if (msg.pending) return true;
  if ((msg.agents || []).length) return true;
  if (visibleActivity(msg.activity).length) return true;
  if ((msg.ledger || []).length) return true;
  return false;
}

function crewStatus(msg) {
  const agents = msg?.agents || [];
  if (agents.some((a) => a.status === "stopped") && !agents.some((a) => LIVE_AGENT.has(a.status))) {
    return t("agent.stopped");
  }
  const live = agents.filter((a) => ["running", "planning", "writing"].includes(a.status));
  if (live.length) return live.map((a) => `${a.name} · ${agentLabel(a.status)}`).join(" · ");
  if (agents.length) return t("view.team");
  if (visibleActivity(msg?.activity).length) return t("view.process");
  return "";
}

function renderActivityCards(items) {
  return (items || [])
    .filter((item) => item && item.kind !== "think")
    .map((item) => {
      if (item.kind === "search") {
        return `<div class="inspect-card"><span class="k">${t("inspect.search")}</span>${escapeHtml(item.query || "")}</div>`;
      }
      if (item.kind === "page") {
        const href = item.url || "";
        return `<div class="inspect-card"><span class="k">${t("inspect.page")}</span><a href="${escapeHtml(href)}" target="_blank" rel="noreferrer">${escapeHtml(item.title || href)}</a></div>`;
      }
      if (item.kind === "code") {
        return `<div class="inspect-card"><span class="k">${t("inspect.code")}</span><pre>${escapeHtml(item.text || "")}</pre></div>`;
      }
      return `<div class="inspect-card"><span class="k">${t("inspect.step")}</span>${escapeHtml(item.text || item.query || "")}</div>`;
    })
    .join("");
}

function fillAgentSelects() {
  const setLabel = (id, items, value) => {
    const el = $(id);
    if (!el) return;
    el.textContent = (items.find((item) => item.id === value) || items[0] || {}).name || value;
  };
  setLabel("leadModelLabel", MODELS, state.agentSettings.lead_model);
  setLabel("leadEffortLabel", EFFORTS, state.agentSettings.lead_effort);
  setLabel("workerModelLabel", MODELS, state.agentSettings.worker_model);
  setLabel("workerEffortLabel", EFFORTS, state.agentSettings.worker_effort);
  const slider = $("workerCount");
  const count = Number(state.agentSettings.worker_count) || 3;
  if (slider) slider.value = String(count);
  if ($("workerCountVal")) $("workerCountVal").textContent = String(count);
  syncWorkerCountWarn(count);
  document.querySelectorAll("[data-theme-set]").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.themeSet === state.theme);
  });
}

function syncWorkerCountWarn(count) {
  const box = $("workerCountWarn");
  const text = $("workerCountWarnText");
  if (!box) return;
  const n = Number(count);
  box.hidden = !(n > 8);
  if (text) text.textContent = t("agents.warn");
  const btn = $("workerCountSuggest");
  if (btn) btn.textContent = t("agents.warnUse8");
}

function applyAgentSettings(agents) {
  if (!agents) return;
  state.agentSettings = { ...state.agentSettings, ...agents };
  fillAgentSelects();
}

async function persistAgentSettings(partial = {}) {
  state.agentSettings = { ...state.agentSettings, ...partial };
  fillAgentSelects();
  const health = await api("/api/settings", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      lead_model: state.agentSettings.lead_model,
      lead_effort: state.agentSettings.lead_effort,
      worker_model: state.agentSettings.worker_model,
      worker_effort: state.agentSettings.worker_effort,
      worker_count: Number(state.agentSettings.worker_count) || 3,
    }),
  });
  if (health?.agents) applyAgentSettings(health.agents);
}

function setSettingsTab(tab) {
  state.settingsTab = tab || "account";
  const titles = { account: "tab.account", agents: "tab.agents", appearance: "tab.appearance", language: "tab.language" };
  if ($("settingsTitle")) $("settingsTitle").textContent = t(titles[state.settingsTab] || "settings");
  document.querySelectorAll("[data-set-tab]").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.setTab === state.settingsTab);
  });
  document.querySelectorAll("[data-set-pane]").forEach((pane) => {
    pane.hidden = pane.dataset.setPane !== state.settingsTab;
  });
}

function openSettings(tab = "account") {
  fillAgentSelects();
  refreshHealth();
  setSettingsTab(tab);
  els.settings.showModal();
}

function closeSetMenus() {
  document.querySelectorAll(".set-picker").forEach((el) => el.classList.remove("open"));
  document.querySelectorAll(".set-picker .model-menu").forEach((el) => {
    el.hidden = true;
  });
}

function renderSetMenu(menu, items, value, kind) {
  if (!menu) return;
  menu.innerHTML = items
    .map((item) => {
      const desc = kind === "effort" ? t(`effort.${item.id}.desc`) : kind === "model" ? t(`model.${item.id}.desc`) : item.desc || "";
      return `<button type="button" class="model-option ${item.id === value ? "active" : ""}" data-pick="${item.id}" role="option">
      <span><span class="name">${escapeHtml(item.name)}</span><span class="desc">${escapeHtml(desc)}</span></span>
      <span class="check">${item.id === value ? "✓" : ""}</span>
    </button>`;
    })
    .join("");
}

function agentChipHtml(a, selectedId) {
  const st = agentLabel(a.status, a.role);
  return `<button type="button" class="agent-chip ${a.id === selectedId ? "active" : ""} ${escapeHtml(a.status || "")} ${a.role === "step-lead" || a.role === "reviewer" ? "lead" : ""}" data-agent="${escapeHtml(a.id)}">
          <i></i>
          <span class="agent-chip-name">${escapeHtml(a.name || a.id)}</span>
          <span class="agent-chip-st">${escapeHtml(st)}</span>
        </button>`;
}

function phaseCard(phase) {
  if (!phase?.phase) return "";
  const label = t(`phase.${phase.phase}`);
  const lines = [label === `phase.${phase.phase}` ? phase.phase : label];
  if (phase.running?.length) lines.push(`${t("phase.runningNow")}：${phase.running.join("、")}`);
  if (phase.sent_back?.length) lines.push(`${t("phase.sentBack")}：${phase.sent_back.join("、")}`);
  if (phase.plan_version) lines.push(`${t("phase.planVer")}：v${phase.plan_version}`);
  const sc = phase.score;
  if (sc && (sc.coverage != null || sc.conflicts != null)) {
    lines.push(
      `${t("phase.score")}：cov ${sc.coverage ?? "—"} · conf ${sc.confidence ?? "—"} · conflict ${sc.conflicts ?? "—"} · accept ${sc.acceptance ?? "—"}`
    );
  }
  if (phase.stop && phase.phase === "stopped") lines.push(`${t("phase.stop")}：${phase.stop}`);
  return `<div class="inspect-card"><span class="k">${t("inspect.phase")}</span>${lines
    .map((line) => `<div class="ledger-line">${escapeHtml(line)}</div>`)
    .join("")}</div>`;
}

function inspectDetailHtml(msg, selected) {
  if (!msg) {
    return `<div class="inspect-card"><span class="k">${t("inspect.status")}</span>${escapeHtml(t("inspect.empty"))}</div>`;
  }
  const ledger = msg.ledger || [];
  const ledgerHtml =
    phaseCard(msg.phase) +
    (ledger.length
      ? `<div class="inspect-card"><span class="k">${t("inspect.ledger")}</span>${ledger
          .map((entry) => `<div class="ledger-line"><b>${escapeHtml(entry.name || entry.id)}</b> ${escapeHtml(entry.note || "")}</div>`)
          .join("")}</div>`
      : "");
  if (!selected) {
    const items = msg.activity || [];
    const body = items.length
      ? renderActivityCards(items)
      : `<div class="inspect-card"><span class="k">${t("inspect.status")}</span>${escapeHtml(msg.status || t("inspect.empty"))}</div>`;
    return ledgerHtml + body;
  }
  const model = selected.model || (selected.role === "lead" ? state.agentSettings.lead_model : state.agentSettings.worker_model);
  const effort = selected.effort || (selected.role === "lead" ? state.agentSettings.lead_effort : state.agentSettings.worker_effort);
  const bits = [
    selected.role === "lead"
      ? t("agent.lead")
      : selected.role === "step-lead"
        ? t("agent.stepLead")
        : selected.role === "reviewer"
          ? t("agent.reviewer")
          : t("agent.worker"),
    modelName(model),
    effortName(effort),
  ].filter(Boolean);
  return `${ledgerHtml}<div class="agent-detail">
      <div class="agent-meta">${escapeHtml(bits.join(" · "))}</div>
      ${selected.brief ? `<div class="inspect-card"><span class="k">${t("inspect.task")}</span>${escapeHtml(selected.brief)}</div>` : ""}
      ${
        (selected.guidance || []).length
          ? `<div class="inspect-card"><span class="k">${t("inspect.guide")}</span>${(selected.guidance || [])
              .map((item) => `<div class="ledger-line">${escapeHtml(item)}</div>`)
              .join("")}</div>`
          : ""
      }
      ${
        (selected.feedback || []).length
          ? `<div class="inspect-card"><span class="k">${t("inspect.feedback")}</span>${(selected.feedback || [])
              .map((item) => `<div class="ledger-line"><b>${escapeHtml(item.to || "")}</b> ${escapeHtml(item.ask || "")}</div>`)
              .join("")}</div>`
          : ""
      }
      ${renderActivityCards(selected.activity)}
      ${
        selected.content
          ? `<div class="inspect-card inspect-output"><span class="k">${selected.role === "lead" && selected.status === "waiting" ? t("inspect.plan") : t("inspect.output")}</span><div class="md">${renderMarkdown(selected.content)}</div></div>`
          : `<div class="inspect-card"><span class="k">${t("inspect.status")}</span>${escapeHtml(
              agentLabel(selected.status, selected.role) || selected.note || t("inspect.empty")
            )}</div>`
      }
    </div>`;
}

function renderInspectRoster(agents, selectedId) {
  const box = els.inspectRoster || els.inspectBody;
  if (!box) return;
  const lead = agents.filter((a) => a.role === "lead");
  const rest = agents.filter((a) => a.role !== "lead");
  const groups = [];
  const seen = new Set();
  for (const a of rest) {
    const key = a.step || a.step_name || "";
    if (!seen.has(key)) {
      seen.add(key);
      groups.push({ key, name: a.step_name || key, items: rest.filter((x) => (x.step || x.step_name || "") === key) });
    }
  }
  box.innerHTML = `<div class="agent-roster">${lead.map((a) => agentChipHtml(a, selectedId)).join("")}${groups
    .map((g) => `${g.name ? `<div class="agent-step-label">${escapeHtml(g.name)}</div>` : ""}${g.items.map((a) => agentChipHtml(a, selectedId)).join("")}`)
    .join("")}</div>`;
}

function patchInspectRoster(agents, selectedId) {
  const root = els.inspectRoster || els.inspectBody;
  if (!root) return;
  root.querySelectorAll(".agent-chip").forEach((btn) => {
    const agent = agents.find((a) => a.id === btn.dataset.agent);
    if (!agent) return;
    btn.className = `agent-chip ${agent.id === selectedId ? "active" : ""} ${agent.status || ""} ${agent.role === "step-lead" || agent.role === "reviewer" ? "lead" : ""}`;
    const st = btn.querySelector(".agent-chip-st");
    if (st) st.textContent = agentLabel(agent.status, agent.role);
    const name = btn.querySelector(".agent-chip-name");
    if (name && agent.name && name.textContent !== agent.name) name.textContent = agent.name;
  });
}

function renderInspect() {
  if (!els.inspectBody) return;
  if (!state.inspectId || !messageInCurrent(state.inspectId)) {
    closeInspect();
    return;
  }
  const msg = (state.current?.messages || []).find((m) => m.id === state.inspectId);
  const agents = msg?.agents || [];
  const title = $("inspectTitle");
  if (title) title.textContent = agents.length && state.inspectAgent ? t("inspect.team") : t("inspect.process");
  const selected = (state.inspectAgent && agents.find((a) => a.id === state.inspectAgent)) || null;
  const key = agents.map((a) => a.id).join("\0");
  const rosterRoot = els.inspectRoster;
  if (rosterRoot && state.inspectRosterKey === key && rosterRoot.querySelector(".agent-chip")) {
    patchInspectRoster(agents, selected?.id);
  } else {
    state.inspectRosterKey = key;
    if (rosterRoot) renderInspectRoster(agents, selected?.id);
    else if (els.inspectBody) {
      els.inspectBody.innerHTML = `<div id="inspectRoster"></div><div id="inspectDetail"></div>`;
      els.inspectRoster = $("inspectRoster");
      els.inspectDetail = $("inspectDetail");
      renderInspectRoster(agents, selected?.id);
    }
  }
  const detail = els.inspectDetail;
  if (detail) detail.innerHTML = inspectDetailHtml(msg, selected);
  syncAgentGraph(agents, msg?.links || []);
  syncGuideBox(selected);
}

function syncGuideBox(selected) {
  const box = els.inspectGuide;
  if (!box) return;
  const live = Boolean(state.crewRunId && state.sending && selected);
  box.hidden = !live;
  if (!live) return;
  const name = selected.name || selected.id || "";
  if (els.inspectGuideLabel) els.inspectGuideLabel.textContent = t("inspect.guideTo", { name });
  if (els.inspectGuideInput) els.inspectGuideInput.placeholder = t("inspect.guidePh", { name });
  if (els.inspectGuideHint && !els.inspectGuideHint.dataset.sticky) {
    els.inspectGuideHint.textContent = t("inspect.guideHint");
  }
}

function resizeGuideInput() {
  const el = els.inspectGuideInput;
  if (!el) return;
  el.style.height = "auto";
  el.style.height = `${Math.min(88, Math.max(36, el.scrollHeight))}px`;
}

async function sendGuide() {
  const text = (els.inspectGuideInput?.value || "").trim();
  if (!text || !state.crewRunId || !state.inspectAgent) return;
  if (els.inspectGuideSend) els.inspectGuideSend.disabled = true;
  try {
    const res = await fetch("/api/crew/guide", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ run_id: state.crewRunId, agent_id: state.inspectAgent, text }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || t("inspect.guideLate"));
    }
    const msg = (state.current?.messages || []).find((m) => m.id === state.inspectId);
    const agent = findAgent(msg, state.inspectAgent);
    if (agent) {
      agent.guidance = [...(agent.guidance || []), text];
      upsertAgent(msg, agent);
    }
    if (els.inspectGuideInput) els.inspectGuideInput.value = "";
    resizeGuideInput();
    if (els.inspectGuideHint) {
      els.inspectGuideHint.dataset.sticky = "1";
      els.inspectGuideHint.textContent = t("inspect.guideSent");
      setTimeout(() => {
        if (!els.inspectGuideHint) return;
        delete els.inspectGuideHint.dataset.sticky;
        els.inspectGuideHint.textContent = t("inspect.guideHint");
      }, 1800);
    }
    renderInspect();
  } catch (err) {
    if (els.inspectGuideHint) {
      els.inspectGuideHint.dataset.sticky = "1";
      els.inspectGuideHint.textContent = err.message || t("inspect.guideLate");
    }
  } finally {
    if (els.inspectGuideSend) els.inspectGuideSend.disabled = false;
  }
}

function agentGraphEdges(agents, extra) {
  const edges = [];
  const lead = agents.find((a) => a.role === "lead");
  const stepLeads = agents.filter((a) => a.role === "step-lead");
  const reviewer = agents.find((a) => a.role === "reviewer");
  if (lead) {
    const kids = stepLeads.length ? stepLeads : agents.filter((a) => a.role !== "lead" && a.role !== "reviewer");
    for (const k of kids) edges.push({ from: lead.id, to: k.id });
    if (reviewer) edges.push({ from: reviewer.id, to: lead.id, kind: "review" });
  }
  for (const sl of stepLeads) {
    for (const w of agents.filter((a) => a.role === "worker" && (a.step || "") === (sl.step || ""))) {
      edges.push({ from: sl.id, to: w.id });
    }
  }
  const ids = new Set(agents.map((a) => a.id));
  for (const a of agents) {
    for (const d of a.depends_on || []) {
      if (ids.has(d)) edges.push({ from: d, to: a.id });
    }
  }
  for (const e of extra || []) {
    if (e.from && e.to && ids.has(e.from) && ids.has(e.to)) {
      edges.push({ from: e.from, to: e.to, kind: e.kind || "feedback" });
    }
  }
  return edges;
}

function agentIsLive(a) {
  return ["running", "writing", "planning"].includes(a.status);
}

function edgeIsLive(edge, byId) {
  const a = byId[edge.from];
  const b = byId[edge.to];
  if (!a || !b) return false;
  if (edge.kind === "feedback" || edge.kind === "review" || edge.kind === "rework") {
    return agentIsLive(a) || agentIsLive(b);
  }
  if (agentIsLive(a) && agentIsLive(b)) return true;
  if (a.role === "step-lead" && agentIsLive(a) && (b.step || "") === (a.step || "")) return true;
  if (b.role === "step-lead" && agentIsLive(b) && (a.step || "") === (b.step || "")) return true;
  return false;
}

function stopAgentGraph() {
  if (state.graphRaf) {
    cancelAnimationFrame(state.graphRaf);
    state.graphRaf = 0;
  }
}

function syncAgentGraph(agents, extraLinks) {
  const wrap = els.inspectGraph;
  const canvas = els.agentGraph;
  if (!wrap || !canvas) return;
  if (!agents.length || (els.inspect && els.inspect.hidden)) {
    wrap.hidden = true;
    if (els.gutterGraph) els.gutterGraph.hidden = true;
    stopAgentGraph();
    return;
  }
  wrap.hidden = false;
  if (els.gutterGraph) els.gutterGraph.hidden = false;
  if (!state.graphNodes) state.graphNodes = new Map();
  const keep = new Set(agents.map((a) => a.id));
  for (const id of [...state.graphNodes.keys()]) {
    if (!keep.has(id)) state.graphNodes.delete(id);
  }
  const w = canvas.clientWidth || wrap.clientWidth - 20;
  const h = canvas.clientHeight || 180;
  agents.forEach((a, i) => {
    let node = state.graphNodes.get(a.id);
    if (!node) {
      const n = agents.length || 1;
      const col = (i % Math.min(4, n)) - Math.min(1.5, (n - 1) / 2);
      const row = a.role === "lead" ? 0 : a.role === "reviewer" ? 0 : a.role === "step-lead" ? 1 : 2;
      const spread = Math.min(72, Math.max(36, (w - 72) / 4));
      node = {
        x: w / 2 + col * spread + (a.role === "reviewer" ? 28 : 0) + (i % 3) * 4,
        y: 30 + row * (h / 3.35) + (i % 2) * 6,
        vx: 0,
        vy: 0,
        pinned: false,
        dragged: false,
      };
      state.graphNodes.set(a.id, node);
    }
    node.agent = a;
  });
  state.graphAgents = agents;
  state.graphEdges = agentGraphEdges(agents, extraLinks);
  if (!state.graphRaf) tickAgentGraph();
}

function graphPalette() {
  const cs = getComputedStyle(document.documentElement);
  const dark = document.documentElement.dataset.scheme === "dark";
  return {
    text: cs.getPropertyValue("--text").trim() || "#1c1915",
    muted: cs.getPropertyValue("--text-muted").trim() || "#6b675f",
    faint: cs.getPropertyValue("--text-faint").trim() || "#9a948a",
    accent: cs.getPropertyValue("--accent").trim() || "#c96442",
    elevated: cs.getPropertyValue("--bg-elevated").trim() || "#fffdf8",
    live: "#2f9d63",
    liveGlow: "rgba(47, 157, 99, 0.28)",
    ask: "#d08a2f",
    askGlow: "rgba(208, 138, 47, 0.28)",
    idle: dark ? "rgba(243,239,230,0.22)" : "rgba(42,36,28,0.16)",
    edge: dark ? "rgba(243,239,230,0.14)" : "rgba(42,36,28,0.12)",
    done: dark ? "#8aa888" : "#6d8a6a",
    error: "#c45c4a",
    labelBg: dark ? "rgba(28,27,25,0.72)" : "rgba(255,253,248,0.82)",
    select: dark ? "rgba(246,242,234,0.9)" : "rgba(36,32,28,0.55)",
    selectHalo: dark ? "rgba(246,242,234,0.12)" : "rgba(36,32,28,0.08)",
  };
}

function nodeRadius(agent, selected) {
  const base = agent?.role === "lead" ? 8 : agent?.role === "step-lead" || agent?.role === "reviewer" ? 6.5 : 5.2;
  return selected ? base + 1.4 : base;
}

function tickAgentGraph() {
  const canvas = els.agentGraph;
  if (!canvas || !els.inspectGraph || els.inspectGraph.hidden || els.inspect?.hidden) {
    state.graphRaf = 0;
    return;
  }
  const dpr = window.devicePixelRatio || 1;
  const cssW = canvas.clientWidth || 280;
  const cssH = canvas.clientHeight || 180;
  if (canvas.width !== Math.floor(cssW * dpr) || canvas.height !== Math.floor(cssH * dpr)) {
    canvas.width = Math.floor(cssW * dpr);
    canvas.height = Math.floor(cssH * dpr);
  }
  const ctx = canvas.getContext("2d");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  const agents = state.graphAgents || [];
  const nodes = state.graphNodes || new Map();
  const edges = state.graphEdges || [];
  const byId = Object.fromEntries(agents.map((a) => [a.id, a]));
  const list = agents.map((a) => nodes.get(a.id)).filter(Boolean);
  const cx = cssW / 2;
  const pad = 30;
  const rest = 54;
  const dragId = state.graphDrag?.id;
  const dragged = dragId ? nodes.get(dragId) : null;
  if (dragged && (dragged.px != null)) {
    const mx = dragged.x - dragged.px;
    const my = dragged.y - dragged.py;
    if (mx || my) {
      for (const n of list) {
        if (n === dragged || n.pinned) continue;
        const d = Math.hypot(n.x - dragged.x, n.y - dragged.y);
        if (d > 110) continue;
        const fall = (1 - d / 110) * 0.22;
        n.x += mx * fall;
        n.y += my * fall;
      }
    }
  }
  for (const n of list) {
    n.px = n.x;
    n.py = n.y;
  }
  for (let i = 0; i < list.length; i++) {
    for (let j = i + 1; j < list.length; j++) {
      const a = list[i];
      const b = list[j];
      let dx = a.x - b.x;
      let dy = a.y - b.y;
      let dist = Math.hypot(dx, dy) || 0.01;
      if (dist >= rest) continue;
      const nx = dx / dist;
      const ny = dy / dist;
      const overlap = (rest - dist) * 0.28;
      const am = a.pinned || a.dragged ? 8 : 1;
      const bm = b.pinned || b.dragged ? 8 : 1;
      const total = am + bm;
      if (!a.pinned) {
        a.x += nx * overlap * (bm / total);
        a.y += ny * overlap * (bm / total);
      }
      if (!b.pinned) {
        b.x -= nx * overlap * (am / total);
        b.y -= ny * overlap * (am / total);
      }
    }
  }
  for (const n of list) {
    if (n.pinned) {
      n.x = Math.min(cssW - pad, Math.max(pad, n.x));
      n.y = Math.min(cssH - 24, Math.max(20, n.y));
      continue;
    }
    if (!n.dragged) {
      n.x += (cx - n.x) * 0.001;
    }
    n.x = Math.min(cssW - pad, Math.max(pad, n.x));
    n.y = Math.min(cssH - 24, Math.max(20, n.y));
  }
  const pal = graphPalette();
  const pulse = 0.55 + 0.45 * Math.sin(Date.now() / 380);
  ctx.clearRect(0, 0, cssW, cssH);
  ctx.save();
  ctx.globalAlpha = 0.35;
  for (let i = 0; i < 18; i++) {
    const px = ((i * 73) % cssW) + 8;
    const py = ((i * 47) % cssH) + 6;
    ctx.beginPath();
    ctx.arc(px, py, 0.7, 0, Math.PI * 2);
    ctx.fillStyle = pal.faint;
    ctx.fill();
  }
  ctx.restore();
  for (const e of edges) {
    const a = nodes.get(e.from);
    const b = nodes.get(e.to);
    if (!a || !b) continue;
    const live = edgeIsLive(e, byId);
    const ask = e.kind === "feedback" || e.kind === "review" || e.kind === "rework";
    const mx = (a.x + b.x) / 2;
    const my = (a.y + b.y) / 2 + (a.x < b.x ? -12 : 12);
    ctx.beginPath();
    ctx.moveTo(a.x, a.y);
    ctx.quadraticCurveTo(mx, my, b.x, b.y);
    if (live && ask) {
      ctx.strokeStyle = `rgba(208, 138, 47, ${0.5 + 0.35 * pulse})`;
      ctx.lineWidth = 2;
      ctx.shadowColor = pal.askGlow;
      ctx.shadowBlur = 10;
    } else if (live) {
      ctx.strokeStyle = `rgba(47, 157, 99, ${0.45 + 0.35 * pulse})`;
      ctx.lineWidth = 2;
      ctx.shadowColor = pal.liveGlow;
      ctx.shadowBlur = 10;
    } else if (ask) {
      ctx.strokeStyle = "rgba(208, 138, 47, 0.28)";
      ctx.lineWidth = 1.35;
      ctx.shadowBlur = 0;
    } else {
      ctx.strokeStyle = pal.edge;
      ctx.lineWidth = 1.15;
      ctx.shadowBlur = 0;
    }
    ctx.stroke();
    ctx.shadowBlur = 0;
  }
  ctx.font = "500 11px Newsreader, Noto Serif SC, Noto Serif JP, serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  for (const n of list) {
    const agent = n.agent || {};
    const live = agentIsLive(agent);
    const selected = agent.id === state.inspectAgent;
    const r = nodeRadius(agent, selected);
    const label = (agent.name || agent.id || "").slice(0, 10);
    if (live) {
      ctx.beginPath();
      ctx.arc(n.x, n.y, r + 7 + pulse * 3, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(47, 157, 99, ${0.08 + 0.08 * pulse})`;
      ctx.fill();
    }
    if (selected) {
      ctx.beginPath();
      ctx.arc(n.x, n.y, r + 6, 0, Math.PI * 2);
      ctx.fillStyle = pal.selectHalo;
      ctx.fill();
    }
    ctx.beginPath();
    ctx.arc(n.x, n.y, r, 0, Math.PI * 2);
    ctx.fillStyle = live ? pal.live : agent.status === "error" ? pal.error : agent.status === "done" ? pal.done : pal.idle;
    ctx.fill();
    if (selected) {
      ctx.lineWidth = 1.6;
      ctx.strokeStyle = pal.select;
      ctx.stroke();
    } else if (agent.role === "lead") {
      ctx.lineWidth = 1.15;
      ctx.strokeStyle = pal.muted;
      ctx.globalAlpha = 0.55;
      ctx.stroke();
      ctx.globalAlpha = 1;
    }
    const tw = ctx.measureText(label).width;
    const lx = n.x;
    const ly = n.y + r + 12;
    ctx.beginPath();
    const padX = 6;
    const pillW = tw + padX * 2;
    const pillH = 16;
    const rx = lx - pillW / 2;
    const ry = ly - pillH / 2;
    const rr = 8;
    ctx.moveTo(rx + rr, ry);
    ctx.arcTo(rx + pillW, ry, rx + pillW, ry + pillH, rr);
    ctx.arcTo(rx + pillW, ry + pillH, rx, ry + pillH, rr);
    ctx.arcTo(rx, ry + pillH, rx, ry, rr);
    ctx.arcTo(rx, ry, rx + pillW, ry, rr);
    ctx.fillStyle = pal.labelBg;
    ctx.fill();
    ctx.fillStyle = selected || live ? pal.text : pal.muted;
    ctx.fillText(label, lx, ly + 0.5);
  }
  state.graphRaf = requestAnimationFrame(tickAgentGraph);
}

function graphPoint(ev) {
  const canvas = els.agentGraph;
  const rect = canvas.getBoundingClientRect();
  return { x: ev.clientX - rect.left, y: ev.clientY - rect.top };
}

function hitAgentNode(x, y) {
  if (!state.graphNodes) return null;
  let best = null;
  let bestD = 26;
  for (const [id, n] of state.graphNodes) {
    const d = Math.hypot(n.x - x, n.y - y);
    const labelD = Math.hypot(n.x - x, n.y + 16 - y);
    const score = Math.min(d, labelD + 4);
    if (score < bestD) {
      bestD = score;
      best = id;
    }
  }
  return best;
}

function onGraphPointerDown(ev) {
  if (ev.button) return;
  const canvas = els.agentGraph;
  if (!canvas || !state.graphNodes) return;
  const { x, y } = graphPoint(ev);
  const id = hitAgentNode(x, y);
  if (!id) return;
  const node = state.graphNodes.get(id);
  if (!node) return;
  ev.preventDefault();
  node.pinned = true;
  node.vx = 0;
  node.vy = 0;
  state.graphDrag = {
    id,
    dx: node.x - x,
    dy: node.y - y,
    startX: x,
    startY: y,
    lastX: x,
    lastY: y,
    lastT: performance.now(),
    moved: false,
  };
  canvas.classList.add("dragging");
  canvas.setPointerCapture?.(ev.pointerId);
}

function onGraphPointerMove(ev) {
  const drag = state.graphDrag;
  const canvas = els.agentGraph;
  if (!drag) {
    if (!canvas || !state.graphNodes) return;
    const { x, y } = graphPoint(ev);
    canvas.style.cursor = hitAgentNode(x, y) ? "grab" : "default";
    return;
  }
  const node = state.graphNodes.get(drag.id);
  if (!node) return;
  const { x, y } = graphPoint(ev);
  if (Math.hypot(x - drag.startX, y - drag.startY) > 3) drag.moved = true;
  node.x = x + drag.dx;
  node.y = y + drag.dy;
  node.vx = 0;
  node.vy = 0;
  node.pinned = true;
  node.dragged = true;
  drag.lastX = x;
  drag.lastY = y;
}

function onGraphPointerUp(ev) {
  const drag = state.graphDrag;
  const canvas = els.agentGraph;
  if (canvas) canvas.classList.remove("dragging");
  if (!drag) return;
  const node = state.graphNodes.get(drag.id);
  if (node) {
    node.pinned = false;
    node.vx = 0;
    node.vy = 0;
    if (drag.moved) node.dragged = true;
  }
  state.graphDrag = null;
  if (!drag.moved) {
    state.inspectAgent = drag.id;
    renderInspect();
    els.inspectGuideInput?.focus();
  }
}

function currentTheme() {
  return THEMES.find((item) => item.id === state.theme) || THEMES[0];
}

function renderThemeCards() {
  const html = THEMES.map(
    (item) => `<button type="button" class="theme-card ${item.id === state.theme ? "active" : ""}" data-theme-set="${item.id}">
      <div class="theme-preview tp-${item.id}" aria-hidden="true">
        <div class="tp-side"></div>
        <div class="tp-main">
          <div class="tp-bar"></div>
          <div class="tp-line"></div>
          <div class="tp-bubble"></div>
        </div>
      </div>
      <span>${escapeHtml(t(item.key))}</span>
    </button>`
  ).join("");
  document.querySelectorAll("[data-theme-grid]").forEach((el) => {
    el.innerHTML = html;
  });
}

function applyTheme() {
  if (!THEMES.some((item) => item.id === state.theme)) state.theme = "light";
  const dark = Boolean(currentTheme().dark);
  document.documentElement.dataset.theme = state.theme;
  document.documentElement.dataset.scheme = dark ? "dark" : "light";
  const light = $("hl-light");
  const darkHl = $("hl-dark");
  if (light) light.disabled = dark;
  if (darkHl) darkHl.disabled = !dark;
  renderThemeCards();
}

function pickGreeting(list, slot) {
  const items = list.filter(Boolean);
  if (!items.length) return "";
  const key = `grok-greet-${state.lang}-${slot}`;
  const last = sessionStorage.getItem(key);
  const pool = items.length > 1 ? items.filter((item) => item !== last) : items;
  const chosen = pool[Math.floor(Math.random() * pool.length)];
  sessionStorage.setItem(key, chosen);
  return chosen;
}

function greetingFor(name) {
  const pack = GREET[state.lang] || GREET.zh;
  const hour = new Date().getHours();
  const slot = hour < 5 ? "late" : hour < 12 ? "morning" : hour < 18 ? "afternoon" : "evening";
  const hello = pickGreeting(pack[slot], slot);
  if (!name) return pickGreeting(pack.plain, "plain");
  const tmpl = pickGreeting(pack.named, "named");
  return tmpl.replaceAll("{hello}", hello).replaceAll("{name}", name);
}

function refreshGreeting() {
  if (els.greeting) els.greeting.textContent = greetingFor(state.userName);
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
    scroller.innerHTML = `<div class="code-head"><span>table</span><button type="button" data-copy="table">${t("copy")}</button></div><div class="table-scroll"></div>`;
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
    block.innerHTML = `<div class="code-head"><span>${escapeHtml(lang || "code")}</span><button type="button" data-copy="code">${t("copy")}</button></div>`;
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
    state.userName = name;
    refreshGreeting();
    els.userName.textContent = name || t("user.local");
    els.avatar.textContent = (name || "G").slice(0, 1).toUpperCase();
    if (!health.ok) {
      els.userSub.textContent = health.expired ? t("auth.expiredSub") : t("auth.noneSub");
      els.authStatus.textContent = health.expired ? t("auth.expired") : t("auth.missing");
    } else {
      const src = health.source === "grok" ? t("auth.grok") : health.source === "env" ? t("auth.env") : t("auth.custom");
      els.userSub.textContent = src;
      els.authStatus.textContent = `${src}${health.user?.email ? ` · ${health.user.email}` : ""}`;
    }
    if (health.agents) applyAgentSettings(health.agents);
    return health;
  } catch (err) {
    els.authStatus.textContent = err.message;
    return null;
  }
}

function dateGroup(iso) {
  if (!iso) return t("date.older");
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return t("date.older");
  const start = (x) => new Date(x.getFullYear(), x.getMonth(), x.getDate()).getTime();
  const diff = (start(new Date()) - start(d)) / 86400000;
  if (diff < 1) return t("date.today");
  if (diff < 2) return t("date.yesterday");
  if (diff < 7) return t("date.week");
  if (diff < 30) return t("date.month");
  return t("date.older");
}

function renderRecents() {
  const q = els.search.value.trim().toLowerCase();
  const items = state.conversations.filter(
    (c) => !q || (c.title || "").toLowerCase().includes(q) || (c.preview || "").toLowerCase().includes(q)
  );
  if (!items.length) {
    els.recents.innerHTML = `<div class="empty-recents">${q ? t("empty.miss") : t("empty.none")}</div>`;
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
      ? `<div class="origin">${t("origin.cli")}${state.current.cwd ? ` · ${escapeHtml(state.current.cwd)}` : ""}${t("origin.cont")}</div>`
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
              <button type="button" data-msg="copy" data-id="${m.id}">${t("copy")}</button>
              ${m.source === "cli" ? "" : `<button type="button" data-msg="edit" data-id="${m.id}">${t("edit")}</button>`}
            </div>
          </div>
        </div>`;
        }
        const pending = m.pending && !m.content;
        const agents = m.agents || [];
        const showProcess = hasInspectableProcess(m);
        const crew = agents.length
          ? `<div class="crew">${agents
              .map(
                (a) =>
                  `<button type="button" class="crew-chip ${escapeHtml(a.status || "")}" data-inspect="${m.id}" data-agent="${escapeHtml(a.id)}"><i></i>${escapeHtml(a.name || a.id)}</button>`
              )
              .join("")}</div>`
          : "";
        return `<div class="turn assistant" data-id="${m.id}">
        ${renderTools(m.tools)}
        ${showProcess ? `<button class="status" type="button" data-inspect="${m.id}">${pending ? `<span class="dots"><i></i><i></i><i></i></span>` : ""}<span>${escapeHtml(crewStatus(m) || (pending ? t("thinking") : t("view.process")))}</span></button>` : ""}
        ${crew}
        ${m.content ? `<div class="md">${renderMarkdown(m.content)}</div>` : ""}
        ${m.error ? `<div class="error-banner">${escapeHtml(m.error)}</div>` : ""}
        ${m.content || m.error ? `<div class="msg-actions">
          <button type="button" data-msg="copy" data-id="${m.id}">${t("copy")}</button>
          ${m.source === "cli" || pending ? "" : `<button type="button" data-msg="regen" data-id="${m.id}">${t("regen")}</button>`}
        </div>` : ""}
      </div>`;
      })
      .join("");
  if (state.stickToBottom !== false) {
    els.thread.scrollTop = els.thread.scrollHeight;
  }
  if (state.inspectId && messageInCurrent(state.inspectId)) renderInspect();
  else if (state.inspectId) closeInspect();
}

function syncSendButton() {
  const asking = Boolean(state.ask);
  const has = els.input.value.trim() || state.pendingFiles.length;
  els.send.disabled = !state.sending && !asking && !has;
  els.send.classList.toggle("busy", state.sending && !asking);
  els.send.setAttribute("aria-label", state.sending && !asking ? t("stop") : t("send"));
}

function resizeInput() {
  const el = els.input;
  if (!el) return;
  if (!el.value) {
    el.style.height = "36px";
    el.scrollTop = 0;
    return;
  }
  el.style.height = "auto";
  el.style.height = `${Math.min(Math.max(el.scrollHeight, 36), 220)}px`;
  el.scrollTop = 0;
}

async function loadConversations() {
  const data = await api("/api/conversations");
  state.conversations = data.conversations || [];
  renderRecents();
}

async function openConversation(id) {
  if (state.sending) state.abort?.abort();
  closeInspect();
  closeAsk();
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
  closeThemePanel();
  if (item.model) setModel(item.model, false);
  renderMessages();
  renderRecents();
  closeSidebar();
  els.thread.scrollTop = els.thread.scrollHeight;
}

async function newChat() {
  if (state.sending) state.abort?.abort();
  state.current = null;
  closeAsk();
  closeInspect();
  closeThemePanel();
  state.pendingFiles = [];
  renderPendingFiles();
  renderMessages();
  refreshGreeting();
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
  if (state.ask) {
    const items = askItems();
    const cur = items[state.askIndex];
    if (state.askOther || cur?.id === "other") await submitAsk(null, els.input.value);
    else await submitAsk(cur);
    return;
  }
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
    status: state.mode === "multi" ? t("agent.planning") : t("thinking"),
    activity: [],
    agents: [],
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
  let autoInspect = true;

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        conversation_id: state.current.id,
        message: text,
        file_ids: files.map((f) => f.id),
        model: state.model,
        effort: state.effort,
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
        const live = messageInCurrent(tempAsst.id) || messageInCurrent(tempUser.id);
        if (!live && event.type !== "start") continue;
        if (event.type === "crew-run") {
          state.crewRunId = event.run_id || null;
          if (state.inspectId) renderInspect();
        } else if (event.type === "start") {
          const prevId = tempAsst.id;
          const stillHere = messageInCurrent(prevId) || messageInCurrent(tempUser.id);
          tempUser.id = event.user_message.id;
          tempUser.files = event.user_message.files || files;
          tempAsst.id = event.assistant_id;
          if (!stillHere) continue;
          state.current.id = event.conversation.id;
          state.current.title = event.conversation.title;
          if (state.inspectId === prevId) state.inspectId = tempAsst.id;
        } else if (event.type === "phase") {
          tempAsst.phase = event;
          const label = t(`phase.${event.phase}`);
          tempAsst.status = label === `phase.${event.phase}` ? event.phase : label;
        } else if (event.type === "status") {
          tempAsst.status = event.text;
        } else if (event.type === "activity") {
          if (event.entry && event.entry.kind !== "think") {
            tempAsst.activity = tempAsst.activity || [];
            tempAsst.activity.push(event.entry);
          }
        } else if (event.type === "agent") {
          upsertAgent(tempAsst, event.agent);
          if (autoInspect && messageInCurrent(tempAsst.id)) {
            autoInspect = false;
            openInspect(tempAsst.id, event.agent?.id || "");
          }
        } else if (event.type === "agent-delta") {
          const agent = findAgent(tempAsst, event.agent_id) || { id: event.agent_id, content: "", activity: [] };
          agent.content = (agent.content || "") + (event.text || "");
          upsertAgent(tempAsst, agent);
        } else if (event.type === "agent-activity") {
          if (event.entry && event.entry.kind !== "think") {
            const agent = findAgent(tempAsst, event.agent_id) || { id: event.agent_id, content: "", activity: [] };
            agent.activity = agent.activity || [];
            agent.activity.push(event.entry);
            upsertAgent(tempAsst, agent);
          }
        } else if (event.type === "agent-status") {
          const agent = findAgent(tempAsst, event.agent_id);
          if (agent) {
            agent.note = event.text;
            upsertAgent(tempAsst, agent);
          }
        } else if (event.type === "ledger") {
          tempAsst.ledger = event.entries || tempAsst.ledger || [];
        } else if (event.type === "link") {
          tempAsst.links = tempAsst.links || [];
          if (event.from && event.to) {
            tempAsst.links.push({ from: event.from, to: event.to, kind: event.kind || "feedback" });
          }
        } else if (event.type === "guide") {
          const agent = findAgent(tempAsst, event.agent_id) || { id: event.agent_id, content: "", activity: [] };
          agent.guidance = [...(agent.guidance || []), ...(event.notes || [])];
          upsertAgent(tempAsst, agent);
        } else if (event.type === "ask") {
          openAsk(event);
        } else if (event.type === "reset") {
          tempAsst.content = "";
        } else if (event.type === "agent-reset") {
          const agent = findAgent(tempAsst, event.agent_id);
          if (agent) {
            agent.content = "";
            upsertAgent(tempAsst, agent);
          }
        } else if (event.type === "delta") {
          tempAsst.content += event.text;
        } else if (event.type === "error") {
          tempAsst.error = event.message;
          tempAsst.pending = false;
        } else if (event.type === "done") {
          tempAsst.content = event.text || tempAsst.content;
          tempAsst.pending = false;
          if (event.activity) tempAsst.activity = event.activity;
          if (event.agents?.length) tempAsst.agents = event.agents;
          if (event.ledger) tempAsst.ledger = event.ledger;
          if (event.links?.length) tempAsst.links = event.links;
          if (event.ask && messageInCurrent(tempAsst.id)) openAsk(event.ask);
          if (event.phase) tempAsst.phase = event.phase;
          if (!String(tempAsst.content || "").trim()) {
            tempAsst.error = tempAsst.error || t("inspect.empty");
          }
          tempAsst.status = tempAsst.agents?.length ? t("view.team") : tempAsst.activity?.length ? t("view.process") : "";
          if (event.conversation && messageInCurrent(tempAsst.id)) {
            state.current.title = event.conversation.title;
            state.current.id = event.conversation.id;
          }
        }
        if (messageInCurrent(tempAsst.id)) renderMessages();
      }
    }
  } catch (err) {
    if (err.name === "AbortError") {
      stopCrewMessage(tempAsst);
    } else {
      tempAsst.error = err.message;
      tempAsst.pending = false;
    }
    renderMessages();
  } finally {
    state.sending = false;
    state.crewRunId = null;
    state.abort = null;
    syncSendButton();
    if (state.inspectId) renderInspect();
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
  renderModeChip();
  hideSlash();
  if (els.input.value.startsWith("/")) {
    els.input.value = "";
    resizeInput();
    syncSendButton();
  }
  els.input.focus({ preventScroll: true });
}

function renderModeChip() {
  const chip = els.modeChip;
  if (!chip) return;
  const mode = SLASH.find((m) => m.id === state.mode && MODE_IDS.has(m.id) && m.id !== "chat");
  if (!mode) {
    chip.hidden = true;
    chip.innerHTML = "";
    syncModeIndent();
    return;
  }
  chip.hidden = false;
  chip.innerHTML = `<span class="mode-chip-label">${escapeHtml(slashName(mode))}</span><button type="button" data-clear-mode aria-label="${escapeHtml(t("close"))}">×</button>`;
  syncModeIndent();
}

function syncModeIndent() {
  const field = els.modeChip?.parentElement;
  if (!field) return;
  if (!els.modeChip || els.modeChip.hidden) {
    field.classList.remove("has-mode");
    field.style.removeProperty("--mode-indent");
    resizeInput();
    return;
  }
  field.classList.add("has-mode");
  const width = Math.ceil(els.modeChip.getBoundingClientRect().width) + 8;
  field.style.setProperty("--mode-indent", `${Number.isFinite(width) && width > 8 ? width : 92}px`);
  resizeInput();
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
    toast(state.lang === "en" ? "This chat is sent by turn. Compact is not needed." : state.lang === "ja" ? "この会話はターンごとに送られるため、compact は不要です。" : "当前对话按轮次发送，无需压缩。");
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
    const level = (arg || "").trim().toLowerCase().replace("extra high", "xhigh").replace("x-high", "xhigh");
    if (EFFORTS.some((e) => e.id === level)) {
      setEffort(level);
      toast(`推理强度：${currentEffort().name}`);
    } else {
      openEffortMenu();
    }
    return;
  }
  if (id === "theme") {
    openThemePanel();
    return;
  }
  if (id === "settings") {
    openSettings("account");
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
      `${rows || `<p class="status-line">${state.lang === "en" ? "No saved workflows yet." : state.lang === "ja" ? "保存済みのワークフローはありません。" : "还没有已保存的工作流。"}</p>`}
      <p class="help">${state.lang === "en" ? "Browse definitions here. Run them from the Grok CLI with /workflow." : state.lang === "ja" ? "定義はここで確認できます。実行は Grok CLI の /workflow から行います。" : "可在此查看工作流定义。运行请使用 Grok CLI 的 /workflow。"}</p>`
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
  if (id === "config-agents") {
    openSettings("agents");
    return;
  }
  if (id === "skills" || id === "plugins" || id === "marketplace" || id === "hooks" || id === "mcps" || id === "memory" || id === "personas") {
    showPanel(
      item.name,
      `<p class="status-line">${state.lang === "en" ? `/${escapeHtml(id)} is available in the Grok CLI.` : state.lang === "ja" ? `/${escapeHtml(id)} は Grok CLI で利用できます。` : `/${escapeHtml(id)} 可在 Grok CLI 中使用。`}</p>`
    );
    return;
  }
  toast(state.lang === "en" ? `/${id} is not available here.` : state.lang === "ja" ? `/${id} はこの画面では実行できません。` : `/${id} 暂不可在此使用。`);
}

function currentModel() {
  return MODELS.find((m) => m.id === state.model) || MODELS[0];
}

function currentEffort() {
  return EFFORTS.find((e) => e.id === state.effort) || EFFORTS[2];
}

function renderModelMenu() {
  els.modelLabel.textContent = currentModel().name;
  els.modelMenu.innerHTML = MODELS.map(
    (m) => `<button type="button" class="model-option ${m.id === state.model ? "active" : ""}" data-model="${m.id}" role="option">
      <span><span class="name">${escapeHtml(m.name)}</span><span class="desc">${escapeHtml(t(`model.${m.id}.desc`))}</span></span>
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

function renderEffortMenu() {
  if (els.effortLabel) els.effortLabel.textContent = currentEffort().name;
  if (!els.effortMenu) return;
  els.effortMenu.innerHTML = EFFORTS.map(
    (e) => `<button type="button" class="model-option ${e.id === state.effort ? "active" : ""}" data-effort="${e.id}" role="option">
      <span><span class="name">${escapeHtml(e.name)}</span><span class="desc">${escapeHtml(t(`effort.${e.id}.desc`))}</span></span>
      <span class="check">${e.id === state.effort ? "✓" : ""}</span>
    </button>`
  ).join("");
}

function setEffort(id, persist = true) {
  if (!EFFORTS.some((e) => e.id === id)) return;
  state.effort = id;
  if (persist) localStorage.setItem("grok-effort", id);
  renderEffortMenu();
  closeEffortMenu();
}

function openEffortMenu() {
  renderEffortMenu();
  els.effortMenu.hidden = false;
  els.effortPicker.classList.add("open");
  els.effortBtn.setAttribute("aria-expanded", "true");
}

function closeEffortMenu() {
  if (!els.effortMenu) return;
  els.effortMenu.hidden = true;
  els.effortPicker?.classList.remove("open");
  els.effortBtn?.setAttribute("aria-expanded", "false");
}

function hideSlash() {
  if (state.ask) {
    renderAsk();
    return;
  }
  state.slashOpen = false;
  els.slash.hidden = true;
  els.slash.innerHTML = "";
  els.composer?.classList.remove("has-slash");
}

function askItems() {
  const ask = state.ask;
  if (!ask) return [];
  return [
    ...(ask.options || []),
    { id: "other", label: t("ask.other"), desc: t("ask.otherDesc") },
  ];
}

function closeAsk() {
  state.ask = null;
  state.askIndex = 0;
  state.askOther = false;
  state.slashOpen = false;
  if (els.input && els.input.dataset.askPh) {
    els.input.placeholder = t("input.placeholder");
    delete els.input.dataset.askPh;
  }
  els.slash.hidden = true;
  els.slash.innerHTML = "";
  els.composer?.classList.remove("has-slash");
  syncSendButton();
}

function openAsk(ev) {
  const options = (ev.options || []).filter((item) => item && item.label);
  if (options.length < 2) return;
  state.ask = {
    run_id: ev.run_id || state.crewRunId || null,
    question: ev.question || "",
    options,
  };
  state.askIndex = 0;
  state.askOther = false;
  renderAsk();
  syncSendButton();
  els.input?.focus();
}

function renderAsk() {
  if (!state.ask || !els.slash) return;
  state.slashOpen = false;
  const items = askItems();
  if (state.askIndex >= items.length) state.askIndex = 0;
  els.slash.hidden = false;
  els.composer?.classList.add("has-slash");
  const rows = items
    .map((item, i) => {
      const icon = item.id === "other" ? "✎" : String(i + 1);
      return `<button type="button" class="slash-item ${i === state.askIndex ? "active" : ""}" data-ask="${escapeHtml(item.id)}">
        <span class="slash-icon">${icon}</span>
        <span><span class="slash-name">${escapeHtml(item.label)}</span>${
          item.desc ? `<span class="slash-desc">${escapeHtml(item.desc)}</span>` : ""
        }</span>
      </button>`;
    })
    .join("");
  els.slash.innerHTML = `<div class="slash-head">${t("ask.head")}</div>${
    state.ask.question ? `<div class="slash-group">${escapeHtml(state.ask.question)}</div>` : ""
  }${rows}`;
}

async function submitAsk(option, extraText) {
  const ask = state.ask;
  if (!ask) return;
  let text = "";
  if (option && option.id !== "other") {
    text = option.desc ? `${option.label} — ${option.desc}` : option.label;
  } else {
    text = (extraText || els.input.value || "").trim();
    if (!text) {
      state.askOther = true;
      state.askIndex = askItems().length - 1;
      if (els.input) {
        els.input.dataset.askPh = "1";
        els.input.placeholder = t("ask.otherPh");
        els.input.focus();
      }
      renderAsk();
      return;
    }
  }
  const runId = ask.run_id;
  const reply = text.startsWith("选择") || text.startsWith("Chose") ? text : `${t("ask.head")}：${text}`;
  closeAsk();
  els.input.value = "";
  resizeInput();
  if (runId && state.sending) {
    const tempUser = {
      id: `ask-${Date.now()}`,
      role: "user",
      content: reply,
      files: [],
      created_at: new Date().toISOString(),
    };
    state.current?.messages.push(tempUser);
    renderMessages();
    try {
      const res = await fetch("/api/crew/answer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ run_id: runId, text: reply }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || t("req.fail"));
      }
    } catch (err) {
      toast(err.message || t("req.fail"));
    }
    return;
  }
  els.input.value = reply;
  resizeInput();
  await send();
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
      const group = t(GROUP_KEY[m.group] || m.group);
      const head = m.group !== lastGroup ? `<div class="slash-group">${escapeHtml(group)}</div>` : "";
      lastGroup = m.group;
      return `${head}<button type="button" class="slash-item ${i === state.slashIndex ? "active" : ""}" data-cmd="${m.id}">
        <span class="slash-icon">${escapeHtml(m.icon)}</span>
        <span><span class="slash-name">/${escapeHtml(m.id)} · ${escapeHtml(slashName(m))}</span><span class="slash-desc">${escapeHtml(slashDesc(m))}</span></span>
      </button>`;
    })
    .join("");
  els.slash.innerHTML = `<div class="slash-head">${t("cmd")}</div>${rows}`;
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
    ? `<button type="button" data-act="rename">${t("rename.title")}</button>`
    : `<button type="button" data-act="rename">${t("rename.title")}</button>
    <button type="button" data-act="delete" class="danger">${slashName(findSlash("delete") || { id: "delete", name: "删除" })}</button>`;
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
  $("themeBtn").addEventListener("click", (e) => {
    e.stopPropagation();
    if (els.themePanel && !els.themePanel.hidden) closeThemePanel();
    else openThemePanel();
  });
  $("langBtn")?.addEventListener("click", (e) => {
    e.stopPropagation();
    cycleLang();
  });
  $("closeTheme")?.addEventListener("click", closeThemePanel);
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
    if (!e.target.closest("#effortPicker")) closeEffortMenu();
    if (!e.target.closest(".set-picker")) closeSetMenus();
  });
  els.modelBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    closeEffortMenu();
    if (els.modelMenu.hidden) openModelMenu();
    else closeModelMenu();
  });
  els.modelMenu.addEventListener("click", (e) => {
    const id = e.target.closest("[data-model]")?.dataset.model;
    if (id) setModel(id);
  });
  els.effortBtn?.addEventListener("click", (e) => {
    e.stopPropagation();
    closeModelMenu();
    if (els.effortMenu.hidden) openEffortMenu();
    else closeEffortMenu();
  });
  els.effortMenu?.addEventListener("click", (e) => {
    const id = e.target.closest("[data-effort]")?.dataset.effort;
    if (id) setEffort(id);
  });
  els.search.addEventListener("input", renderRecents);
  els.input.addEventListener("input", () => {
    resizeInput();
    syncSendButton();
    if (state.ask) return;
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
    if (state.ask) {
      const items = askItems();
      if (e.key === "ArrowDown") {
        e.preventDefault();
        state.askIndex = (state.askIndex + 1) % Math.max(items.length, 1);
        state.askOther = items[state.askIndex]?.id === "other";
        renderAsk();
        return;
      }
      if (e.key === "ArrowUp") {
        e.preventDefault();
        state.askIndex = (state.askIndex - 1 + items.length) % Math.max(items.length, 1);
        state.askOther = items[state.askIndex]?.id === "other";
        renderAsk();
        return;
      }
      if (e.key === "Enter" || e.key === "Tab") {
        e.preventDefault();
        send();
        return;
      }
      if (e.key === "Escape" && !state.ask.run_id) {
        e.preventDefault();
        closeAsk();
        return;
      }
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
    const askId = e.target.closest("[data-ask]")?.dataset.ask;
    if (askId) {
      const item = askItems().find((x) => x.id === askId);
      state.askIndex = Math.max(0, askItems().findIndex((x) => x.id === askId));
      submitAsk(item);
      return;
    }
    const id = e.target.closest("[data-cmd]")?.dataset.cmd;
    const item = id && findSlash(id);
    if (item) runSlash(item);
  });
  els.modeChip?.addEventListener("click", (e) => {
    if (e.target.closest("[data-clear-mode]")) setMode("chat");
  });
  $("starters")?.addEventListener("click", (e) => {
    const id = e.target.closest("[data-mode]")?.dataset.mode;
    if (id) {
      setMode(id);
      els.input.focus();
    }
  });
  $("openSettings").addEventListener("click", () => openSettings("account"));
  $("closeSettings")?.addEventListener("click", () => els.settings.close());
  els.settings?.addEventListener("click", (e) => {
    const tab = e.target.closest("[data-set-tab]")?.dataset.setTab;
    if (tab) {
      closeSetMenus();
      setSettingsTab(tab);
      return;
    }
    const theme = e.target.closest("[data-theme-set]")?.dataset.themeSet;
    if (theme) {
      state.theme = theme;
      localStorage.setItem("grok-theme", theme);
      applyTheme();
      fillAgentSelects();
      return;
    }
    const lang = e.target.closest("[data-lang-set]")?.dataset.langSet;
    if (lang) setLang(lang);
  });
  els.themePanel?.addEventListener("click", (e) => {
    const theme = e.target.closest("[data-theme-set]")?.dataset.themeSet;
    if (!theme) return;
    state.theme = theme;
    localStorage.setItem("grok-theme", theme);
    applyTheme();
    fillAgentSelects();
    document.querySelectorAll("[data-theme-set]").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.themeSet === theme);
    });
  });
  const setPickers = [
    ["leadModel", MODELS, "lead_model"],
    ["leadEffort", EFFORTS, "lead_effort"],
    ["workerModel", MODELS, "worker_model"],
    ["workerEffort", EFFORTS, "worker_effort"],
  ];
  for (const [prefix, items, key] of setPickers) {
    const picker = $(`${prefix}Picker`);
    const btn = $(`${prefix}Btn`);
    const menu = $(`${prefix}Menu`);
    if (!picker || !btn || !menu) continue;
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const open = picker.classList.contains("open");
      closeSetMenus();
      if (open) return;
      renderSetMenu(menu, items, state.agentSettings[key], prefix.toLowerCase().includes("effort") ? "effort" : "model");
      menu.hidden = false;
      picker.classList.add("open");
    });
    menu.addEventListener("click", async (e) => {
      const id = e.target.closest("[data-pick]")?.dataset.pick;
      if (!id) return;
      closeSetMenus();
      await persistAgentSettings({ [key]: id });
    });
  }
  $("workerCount")?.addEventListener("input", () => {
    const n = Number($("workerCount").value) || 3;
    if ($("workerCountVal")) $("workerCountVal").textContent = String(n);
    syncWorkerCountWarn(n);
  });
  $("workerCount")?.addEventListener("change", async () => {
    await persistAgentSettings({ worker_count: Number($("workerCount").value) || 3 });
  });
  $("workerCountSuggest")?.addEventListener("click", async () => {
    await persistAgentSettings({ worker_count: 8 });
  });
  $("saveKey").addEventListener("click", async () => {
    const payload = {};
    if (els.apiKey.value.trim()) payload.api_key = els.apiKey.value;
    else return toast(t("toast.fillKey"));
    await api("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    els.apiKey.value = "";
    await refreshHealth();
    toast(t("toast.saved"));
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
      openInspect(inspectBtn.dataset.inspect, inspectBtn.dataset.agent || "");
      return;
    }
    const act = e.target.closest("[data-msg]");
    if (act) {
      const kind = act.dataset.msg;
      const id = act.dataset.id;
      if (kind === "copy") {
        const msg = (state.current?.messages || []).find((m) => m.id === id);
        if (!msg?.content) return toast(t("copyFail"));
        const ok = await copyText(msg.content);
        act.textContent = ok ? t("copied") : t("copyFail");
        setTimeout(() => {
          act.textContent = t("copy");
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
      toast(t("copyFail"));
      return;
    }
    const ok = await copyText(text);
    const prev = btn.textContent;
    btn.textContent = ok ? t("copied") : t("copyFail");
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
  bindGraphGutter(els.gutterGraph);
  $("closeInspect")?.addEventListener("click", closeInspect);
  const pickAgent = (e) => {
    const chip = e.target.closest("[data-agent]");
    if (!chip) return;
    e.preventDefault();
    state.inspectAgent = chip.dataset.agent;
    renderInspect();
    if (state.crewRunId) els.inspectGuideInput?.focus();
  };
  els.inspectBody?.addEventListener("pointerdown", pickAgent);
  els.inspectRoster?.addEventListener("pointerdown", pickAgent);
  els.agentGraph?.addEventListener("pointerdown", onGraphPointerDown);
  els.agentGraph?.addEventListener("pointermove", onGraphPointerMove);
  els.agentGraph?.addEventListener("pointerup", onGraphPointerUp);
  els.agentGraph?.addEventListener("pointercancel", onGraphPointerUp);
  els.inspectGuideSend?.addEventListener("click", sendGuide);
  els.inspectGuideInput?.addEventListener("input", resizeGuideInput);
  els.inspectGuideInput?.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey && !e.isComposing) {
      e.preventDefault();
      sendGuide();
    }
  });
  renderModelMenu();
  renderEffortMenu();
  renderModeChip();
  fillAgentSelects();
  applyI18n();
  syncSendButton();
  await refreshHealth();
  await loadConversations();
  els.input.focus();
}

init();
