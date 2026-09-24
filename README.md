# Shiyan's Notes

部署在 GitHub Pages 上的个人博客（Jekyll 静态站点），用 Markdown 写作，push 后由 GitHub 自动构建发布。
线上地址：https://shiyanxu.github.io/

## 目录结构

```
shiyanxu.github.io/
├── _config.yml        # 站点配置（标题 / URL / 插件 / 文章链接规则）
├── Gemfile            # 本地预览依赖（github-pages，与线上构建环境一致）
├── _layouts/
│   ├── default.html   # 全局布局（导航 + 页脚 + SEO）
│   └── post.html      # 文章布局（标签 / 日期 / 阅读时长 / 上下篇）
├── _includes/         # 导航、页脚等复用片段
├── _posts/            # 全部文章，Markdown 格式
├── index.html         # 首页（最新文章、分类计数均由 Liquid 自动生成）
├── archive.html       # 文章列表页（按年份分组 + 分类筛选）
├── categories.html    # 分类归档页
└── assets/            # css / js / img
```

## 写一篇新文章（核心工作流）

在 `_posts/` 新建 `YYYY-MM-DD-标题.md`，顶部写 front matter，正文用 Markdown：

```markdown
---
layout: post
title: "文章标题"
date: 2026-09-24
categories: [机器学习]
description: 一句话摘要，会显示在首页卡片和 SEO 里。
---

正文从这里开始……
```

提交并推送后，首页「最新文章」卡片、列表页、分类计数、RSS **全部自动更新**，无需手动改任何页面。

```bash
git add . && git commit -m "新文章：文章标题" && git push
```

## 本地预览（可选）

push 后 GitHub 会自动构建，本地预览不是必须的。如需本地预览：

```bash
bundle install
bundle exec jekyll serve
# 打开 http://localhost:4000
```

## 部署（GitHub Pages）

1. GitHub 新建公开仓库，名称必须是 `shiyanxu.github.io`；
2. 推送全部文件到 `main` 分支；
3. Settings → Pages → Source 选 `main / (root)`（此类仓库通常默认开启）；
4. 每次 push 后 1–2 分钟线上自动更新，部署状态见仓库 Actions 页。

已启用插件：`jekyll-feed`（RSS，/feed.xml）、`jekyll-seo-tag`（SEO）、`jekyll-sitemap`（站点地图）。
