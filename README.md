<div align="center">

<img src="static/grok-mark.svg" width="72" alt="Grok" />

# Grok Chat

本地网页版 Grok · 视觉参考 Claude

只监听 `127.0.0.1` · 对话存在本机 `~/.grok/web-chat/`

[功能](#功能) · [启动](#启动) · [登录](#登录) · [`/web`](#grok-cli-web) · [快捷键](#快捷键)

</div>

---

## 功能

- 流式对话，支持 Markdown、表格、KaTeX（`$...$` / `$$...$$`）
- 代码块和表格可复制；消息可编辑、重新生成
- 上传 / 拖拽 / 粘贴图片和文档
- 读取 Grok CLI 历史（`~/.grok/sessions/`），可在网页里继续聊
- `/` 命令菜单：模式、导出、用量、工作流等
- 服务端工具：网页搜索、X 搜索、代码解释器（工具调用不会漏进正文）
- 点击「正在搜索 / 查看过程」可在右侧看搜索词和打开过的网页
- 左右栏可拖拽改宽度

## 启动

```bash
git clone https://github.com/YOU/grok-chat.git
cd grok-chat
chmod +x start.sh launch.sh
./launch.sh
```

然后打开 [http://127.0.0.1:8787](http://127.0.0.1:8787)。

| 脚本 | 作用 |
| --- | --- |
| `./launch.sh` | 后台启动（已在跑就复用），并打开浏览器 |
| `./start.sh` | 前台运行，`Ctrl+C` 停止 |

需要 Python 3.13+（部分 Homebrew 的 3.14 `venv` 不好用）。依赖会自动装进 `.venv`。

## 登录

凭证按这个顺序找：

1. 环境变量 `XAI_API_KEY`（或 gitignore 的 `.env`）
2. 页面设置里保存的密钥
3. 已有的 `grok login` 会话（`~/.grok/auth.json`）

用过 Grok CLI 的话，一般不用再配密钥。

## Grok CLI：`/web`

在 Grok TUI 里输入：

```
/web
```

会启动（或复用）这个网页并打开浏览器。技能在仓库 `.grok/skills/web/`，拷到用户目录即可全局用：

```bash
mkdir -p ~/.grok/skills
cp -R .grok/skills/web ~/.grok/skills/
export GROK_CHAT_HOME="$PWD"   # 仓库不在 ~/code/grok-chat 时需要
```

## 快捷键

`Enter` 发送 · `Shift+Enter` 换行 · `/` 命令 · `⌘N` 新对话 · `⌘K` 搜索历史

中文输入法确认时的回车不会误发送。

## 配置

| 变量 | 含义 |
| --- | --- |
| `XAI_API_KEY` | [console.x.ai](https://console.x.ai) 的 API 密钥 |
| `PORT` | 端口，默认 `8787` |
| `GROK_CHAT_HOME` | `/web` 和 `launch.sh` 用的仓库路径 |

数据在 `~/.grok/web-chat/`（对话、上传、可选密钥），不要提交这个目录。

## License

MIT
