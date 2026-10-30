#!/bin/zsh
# 知识库每日发布：扫描 → 有变化才提交 → 推送 → GitHub Pages 自动构建
# 由 launchd 每天 22:30 触发，也可以手动跑：./publish.sh

set -u

PY=/Users/xushiyan/.workbuddy/binaries/python/versions/3.13.12/bin/python3
REPO=/Users/xushiyan/dev/kb-site
LOG=$REPO/.publish.log

# 专用部署密钥：只对该仓库有写权限，放在非保护目录，
# 所以无人值守运行时不需要授权读取 ~/.ssh，也不需要人工确认
DEPLOY_KEY=/Users/xushiyan/.config/kb-site/deploy_key

cd "$REPO" || exit 1

if [ -f "$DEPLOY_KEY" ]; then
  SSH_CMD="ssh -i $DEPLOY_KEY -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new -o BatchMode=yes -o ConnectTimeout=10"
else
  SSH_CMD="ssh -o StrictHostKeyChecking=accept-new -o BatchMode=yes -o ConnectTimeout=10"
fi

{
  echo ""
  echo "=== $(date '+%Y-%m-%d %H:%M:%S') 开始 ==="
  GIT_SSH_COMMAND="$SSH_CMD" "$PY" scripts/sync.py
  echo "=== $(date '+%Y-%m-%d %H:%M:%S') 结束（退出码 $?）==="
} >> "$LOG" 2>&1

# 日志只保留最近 500 行
if [ -f "$LOG" ]; then
  tail -n 500 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
fi
