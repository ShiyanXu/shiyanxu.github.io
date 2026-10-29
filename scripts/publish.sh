#!/bin/zsh
# 知识库每日发布：扫描 → 有变化才提交 → 推送 → GitHub Pages 自动构建
# 由 launchd 每天 22:30 触发，也可以手动跑：./publish.sh

set -u

PY=/Users/xushiyan/.workbuddy/binaries/python/versions/3.13.12/bin/python3
REPO=/Users/xushiyan/dev/kb-site
LOG=$REPO/.publish.log

cd "$REPO" || exit 1

{
  echo ""
  echo "=== $(date '+%Y-%m-%d %H:%M:%S') 开始 ==="
  # launchd 环境没有交互式 ssh-agent，禁用主机密钥交互，避免卡住
  GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=accept-new -o BatchMode=yes" \
    "$PY" scripts/sync.py
  echo "=== $(date '+%Y-%m-%d %H:%M:%S') 结束（退出码 $?）==="
} >> "$LOG" 2>&1

# 日志只保留最近 500 行
if [ -f "$LOG" ]; then
  tail -n 500 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
fi
