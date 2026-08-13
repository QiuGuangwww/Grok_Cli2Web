#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

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
    echo "无法创建虚拟环境，请先安装 Python 3.13+"
    exit 1
  fi
fi
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install -q -r requirements.txt

PORT="${PORT:-8787}"
export PORT
URL="http://127.0.0.1:${PORT}"
echo ""
echo "  Grok Chat  →  ${URL}"
echo "  按 Ctrl+C 停止"
echo ""

if command -v open >/dev/null 2>&1; then
  (sleep 0.8 && open "${URL}") >/dev/null 2>&1 &
fi

exec python server.py
