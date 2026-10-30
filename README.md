# Shiyan's Notes

部署在 GitHub Pages 上的个人站点（Jekyll 静态站点），push 后由 GitHub 自动构建发布。
线上地址：https://shiyanxu.github.io/

站点分两块：

- **知识库 `/kb/`** —— 主体内容，60 篇笔记、15 个分类，从 Obsidian 知识库自动同步
- **博客 `/posts/`** —— 手写的长文，放在 `_posts/`

## 知识库是怎么同步的

源目录：`~/Library/CloudStorage/OneDrive-个人/Obsidian/AI/知识库`

每天 **22:30** 由定时任务跑一次 `scripts/publish.sh`：

1. 扫描源目录的 15 个分类，逐个算 SHA-256
2. 只把**有变化**的笔记复制进 `kb/<分类>/`，删掉源里已删的
3. 给每篇加 frontmatter（layout、标题、分类、同步日期），原文一个字不改
4. 重建 `_data/kb.yml`（分类树）和 `_data/kb_updates.yml`（按天归档的增删改）
5. 有改动才 `git commit` + `push`；没改动什么都不做

**一天最多一个 commit**，同一天重复运行会 amend 当天那次提交（已推送的除外）。提交信息形如
`知识库更新 2026-10-29：新增 2 篇、修改 1 篇`。

「以天为单位」也体现在站内：`/kb/updates.html` 按日期倒序列出每天的增删改。

### 手动运行

```bash
cd ~/dev/kb-site
./scripts/publish.sh          # 等价于下面这条 + 写日志
python3 scripts/sync.py       # 同步 + 提交 + 推送

python3 scripts/sync.py --dry-run    # 只看会改什么
python3 scripts/sync.py --no-push    # 只提交不推送
python3 scripts/sync.py --force      # 忽略同步记录，全量重建
```

同步记录在 `.kb-manifest.json`（每个文件的哈希、首次收录日、最后修改日、变更事件）。
**这个文件要跟着提交**，否则下次会当全量新增处理。

### 定时任务

**主方式：WorkBuddy 每日任务**（每天 22:30 触发，跑 `scripts/publish.sh`）。
要求 WorkBuddy 那个时间在运行；没跑的话第二天手动补一次 `./scripts/publish.sh` 也一样。

**备选：launchd**（不依赖 WorkBuddy，但需要手动装一次。当前环境里 WorkBuddy 的终端调用不了
`launchctl`，所以这一步得你在自己的终端执行）：

```bash
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.shiyanxu.kb-publish.plist
launchctl kickstart -k gui/$(id -u)/com.shiyanxu.kb-publish   # 立刻试跑
launchctl list | grep kb-publish                               # 确认已加载
launchctl bootout gui/$(id -u)/com.shiyanxu.kb-publish         # 卸载
```

日志：`.publish.log`（脚本输出）、`.launchd.log`（launchd 自身报错）。
机器 22:30 若在睡眠，唤醒后 launchd 会补跑一次。

### 为什么无人值守也能推送

推送**不走 `~/.ssh`**，用的是一把专用部署密钥：

| 文件 | 作用 |
|---|---|
| `~/.config/kb-site/deploy_key` | 私钥，只对该仓库有写权限 |
| `~/.config/kb-site/deploy_key.pub` | 公钥，需加到仓库 Settings → Deploy keys 并勾选 **Allow write access** |
| `~/.config/kb-site/known_hosts` | 独立的 github.com 主机密钥，丢了脚本会自动重建 |

`publish.sh` 里用 `GIT_SSH_COMMAND` 显式指定这两个文件，并加 `IdentitiesOnly=yes`。
这样运行时完全不碰 `~/.ssh`——那里的读取规则是「每次询问」，碰它就会卡在人工授权上。
换成 `~/.config` 之后，整个推送在沙箱内即可完成，不需要任何确认。

## 目录结构

```
shiyanxu.github.io/
├── _config.yml            # 站点配置（含 kb 的 permalink 与 layout 约定）
├── _layouts/
│   ├── default.html       # 博客全局布局
│   ├── post.html          # 文章布局
│   └── kb.html            # 知识库布局（左栏分类树 + 正文）
├── _includes/
│   ├── nav.html
│   ├── footer.html
│   └── kb-sidebar.html    # 知识库侧边栏
├── _data/
│   ├── kb.yml             # 自动生成：分类树与篇目
│   └── kb_updates.yml     # 自动生成：按天更新记录
├── kb/                    # 自动同步，不要手改
│   ├── index.md           # 知识库总览（源 README + 统计）
│   ├── updates.md         # 更新日志模板
│   └── <分类>/<笔记>.md
├── _posts/                # 手写博客
├── scripts/
│   ├── sync.py            # 同步脚本
│   └── publish.sh         # 定时任务入口
├── assets/css/style.css   # 博客样式
├── assets/css/kb.css      # 知识库样式
└── .kb-manifest.json      # 同步记录（必须提交）
```

## 写博客

在 `_posts/` 新建 `YYYY-MM-DD-标题.md`：

```markdown
---
layout: post
title: "文章标题"
date: 2026-09-24
categories: [机器学习]
description: 一句话摘要，会显示在首页卡片和 SEO 里。
---
```

push 后首页「最新文章」、列表页、分类计数、RSS 自动更新。

## 部署

仓库名 `shiyanxu.github.io`，Pages 用 `main / (root)`、Jekyll 构建，**不需要 Actions**。
已启用插件：`jekyll-feed`、`jekyll-seo-tag`、`jekyll-sitemap`、`jekyll-relative-links`。

`jekyll-relative-links` 是关键：知识库笔记之间用相对路径互链（285 处），
它负责把 `.md` 链接改写成 `.html`。所以 `_config.yml` 里 kb 的 `permalink`
必须显式写成 `/:path/:basename.html`——若沿用全局以 `/` 结尾的 permalink，
页面会变成目录式 URL（`/kb/xx/`），与改写后的 `.html` 链接对不上，全部 404。
