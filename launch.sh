#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
PORT="${PORT:-8787}"
URL="http://127.0.0.1:${PORT}"
DATA="${HOME}/.grok/web-chat"
LOG="${DATA}/server.log"
mkdir -p "${DATA}"

already=0
if curl -sf --noproxy '*' --max-time 1 "${URL}/api/health" >/dev/null 2>&1; then
  already=1
else
  cd "${ROOT}"
  if [ ! -x .venv/bin/python ]; then
    created=0
    for py in /opt/miniconda3/bin/python3.13 python3.13 python3; do
      if command -v "$py" >/dev/null 2>&1 || [ -x "$py" ]; then
        if "$py" -m venv .venv; then
          created=1
          break
        fi
        rm -rf .venv
      fi
    done
    if [ "$created" -ne 1 ]; then
      echo "无法创建虚拟环境"
      exit 1
    fi
  fi
  # shellcheck disable=SC1091
  source .venv/bin/activate
  python -m pip install -q -r requirements.txt
  nohup env PORT="${PORT}" python server.py >>"${LOG}" 2>&1 &
  echo $! >"${DATA}/server.pid"
  ok=0
  for _ in $(seq 1 40); do
    if curl -sf --noproxy '*' --max-time 1 "${URL}/api/health" >/dev/null 2>&1; then
      ok=1
      break
    fi
    sleep 0.25
  done
  if [ "$ok" -ne 1 ]; then
    echo "启动失败，日志：${LOG}"
    exit 1
  fi
fi

if command -v open >/dev/null 2>&1; then
  open "${URL}"
fi

if [ "$already" -eq 1 ]; then
  echo "Grok Chat 已在运行：${URL}"
else
  echo "Grok Chat 已启动：${URL}"
fi
