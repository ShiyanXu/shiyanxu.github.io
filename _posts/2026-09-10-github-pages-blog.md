---
layout: post
title: "用 GitHub Pages 从零搭建个人博客"
date: 2026-09-10
categories: [前端开发]
description: 不写后端、零成本上线：从仓库命名、目录结构到 Jekyll 与自定义域名，完整走通一次静态博客发布流程。
---

这个博客本身就是用 GitHub Pages 搭的。记录一遍完整流程，下次重构时照做即可。

## 一、为什么是 GitHub Pages

- **零成本**：公开仓库免费托管，带宽不限；
- **零运维**：没有服务器，push 即发布；
- **原生支持 Jekyll**：Markdown 提交后自动构建成 HTML。

## 二、关键三步

1. 新建公开仓库，名称必须是 `<用户名>.github.io`；
2. 推送代码到 `main` 分支；
3. Settings → Pages 确认 Source 为 `main / (root)`，等 1–2 分钟生效。

## 三、Jekyll 目录约定

```text
_config.yml     # 站点配置
_layouts/       # 页面布局
_includes/      # 可复用片段
_posts/         # 文章，YYYY-MM-DD-标题.md
assets/         # CSS / JS / 图片
```

## 四、踩坑记录

- 改 `_config.yml` 后本地需要重启 `jekyll serve` 才生效；
- 文章文件名日期不能是未来日期，否则不会被构建（除非开 `future: true`）；
- 本地预览用 `github-pages` gem，保证和线上构建环境一致。
