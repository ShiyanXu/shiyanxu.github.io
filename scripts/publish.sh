#!/bin/zsh
# 知识库每日发布：扫描 → 有变化才提交 → 推送 → GitHub Pages 自动构建
# 由 launchd 每天 22:30 触发，也可以手动跑：./publish.sh

set -u

PY=/Users/xushiyan/.workbuddy/binaries/python/versions/3.13.12/bin/python3
REPO=/Users/xushiyan/dev/kb-site
LOG=$REPO/.publish.log

# 专用部署密钥 + 独立 known_hosts：
# 两者都放在非保护目录，无人值守运行时不触碰 ~/.ssh，
# 因而既不需要读取私钥授权，也不会触发沙箱外执行
KEYDIR=/Users/xushiyan/.config/kb-site
DEPLOY_KEY=$KEYDIR/deploy_key
KNOWN_HOSTS=$KEYDIR/known_hosts

cd "$REPO" || exit 1

# known_hosts 丢了就重建，避免首次运行卡在主机密钥确认
if [ ! -s "$KNOWN_HOSTS" ]; then
  mkdir -p "$KEYDIR"
  ssh-keyscan -t ed25519,rsa github.com > "$KNOWN_HOSTS" 2>/dev/null
fi

if [ -f "$DEPLOY_KEY" ]; then
  SSH_CMD="ssh -i $DEPLOY_KEY -o IdentitiesOnly=yes -o UserKnownHostsFile=$KNOWN_HOSTS -o StrictHostKeyChecking=yes -o BatchMode=yes -o ConnectTimeout=10"
else
  SSH_CMD="ssh -o UserKnownHostsFile=$KNOWN_HOSTS -o StrictHostKeyChecking=yes -o BatchMode=yes -o ConnectTimeout=10"
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
