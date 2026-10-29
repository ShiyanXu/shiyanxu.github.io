---
layout: "kb"
title: "长时程 Agent 的 Harness：把「跨窗口交接」当一等公民"
kb_cat: "Harness 工程"
kb_cat_key: "04-Harness工程"
kb_src: "04-Harness工程/02-长时程Agent的Harness.md"
kb_updated: "2026-10-29"
---

# 长时程 Agent 的 Harness：把「跨窗口交接」当一等公民

> 长任务做不完，问题多半不在模型能力，而在交接：新窗口不知道上一窗口干了什么，于是要么一次做太多把自己撑爆，要么看见一点进展就宣布完工。

## 问题：会话是离散的，记忆是断的

把长任务交给 Agent，等于让一群**轮班工程师**接力，每班到岗时完全不记得上一班干了什么。上下文窗口有限，绝大多数复杂项目又装不进一个窗口，于是「怎么把两次会话接上」成了硬约束。

Claude Agent SDK 本身有压缩（compaction）这类上下文管理能力，理论上可以无限期地干下去。但原文的实验结论很直接：**压缩不够**。即便用 Opus 4.5，在 SDK 里跨多个窗口循环，只给一句「做一个 claude.ai 的克隆」，也做不出生产质量的 Web 应用。

失败集中在两种形态：

- **一次性做完**。Agent 试图一口气把整个应用写出来，写到一半上下文耗尽；下一个会话接手时，某个功能只写了一半、没有任何记录，只能靠猜，然后花大量时间把基本应用重新跑起来。压缩也救不了——压缩传递的指令并不总是足够清晰。
- **过早宣布完成**。项目后期，新实例环顾四周，看到「已经有进展了」，就判定任务结束。

两种失败指向同一个缺口：上下文窗口里没有一份**可交接的状态记录**，也没有一种机制强迫 Agent 按「功能」而不是按「灵感」推进。

## 解法骨架：初始化代理 + 增量编码代理

原文的方案是两段式：第一次会话用一份专门的提示词把地基打好，之后每次会话只要求增量推进并留下结构化产物。

| | 初始化代理（initializer agent） | 编码代理（coding agent） |
|---|---|---|
| 何时运行 | 仅第一次会话 | 之后每一次会话 |
| 核心职责 | 搭起承载**全部**功能的初始环境 | 每次只推进一个功能，收尾时把环境留在干净状态 |
| 留下的产物 | `init.sh`、`claude-progress.txt`、初始 git 提交 | 描述性 commit、进度文件更新、功能列表里 `passes` 状态变更 |
| 解决的问题 | 一次性做完、不会跑应用 | 过早完工、环境带病、进度丢失 |

一个容易被忽略的细节（原文脚注）：这两者被称作两个 agent，只是因为**首条用户提示词不同**；系统提示词、工具集和整体 harness 完全一致。换句话说，这不是两套系统，而是同一个 harness 的两种入场方式。

所谓「干净状态」，原文给的定义是适合直接合进主分支的代码：没有重大 bug，结构清晰、有文档，下一个人不必先清理一团乱麻就能开始新功能。

## 功能列表：把「做完了没」变成可判定问题

初始化代理要做的最重要一件事，是把用户那句高层提示扩写成一份**穷尽式的功能需求文件**。claude.ai 克隆这个例子里，这份清单有 **200 多项**功能，粒度细到「用户能打开一个新对话、输入查询、按回车、看到 AI 回复」。

设计上有三个关键点：

1. **初始全部标记为 `failing`**。后续每个编码代理拿到的，是「完整功能长什么样」的轮廓，而不是一句模糊目标。
2. **只允许改 `passes` 字段**。编码代理不能增删、改写条目；提示词用了很硬的措辞——「删除或修改测试是不可接受的，这会导致功能缺失或有缺陷」。
3. **用 JSON 而不是 Markdown**。实验后发现，模型更不容易去改乱、覆盖 JSON 文件。

单条功能长这样：

```json
{
  "category": "functional",
  "description": "New chat button creates a fresh conversation",
  "steps": [
    "Navigate to main interface",
    "Click the 'New Chat' button",
    "Verify a new conversation is created",
    "Check that chat area shows welcome state",
    "Verify conversation appears in sidebar"
  ],
  "passes": false
}
```

这份文件同时干两件事：**进度仪表盘**（还剩多少 `passes: false`）和**验收标准**（每条都写死了端到端步骤，而不是「实现了就算」）。

## 增量推进：一次只做一个功能

有了脚手架，编码代理被要求**一次只处理一个功能**。原文说这是对付「一次做太多」最关键的一招。

光做增量还不够，改完代码必须把环境收拾干净。实验里最有效的触发方式是两条硬要求：

- 用描述性的提交信息把进度提交到 git；
- 在进度文件里写下这一轮做了什么。

好处是双向的：git 让模型能回退坏改动、恢复到能跑的状态；进度文件让下一个会话不必猜。原文还提到效率收益——省掉了「猜上一轮发生了什么、再把基本应用弄跑」的时间。

## 测试：像用户那样点，别像程序员那样 curl

原文观察到的最后一个主要失败模式：**没测就标记完成**。不给明确提示时，Claude 会改代码，也会跑单元测试或拿 `curl` 打开发服务器，但识别不出「这个功能端到端根本没通」。

对策是把测试方式写死：明确要求使用**浏览器自动化工具**，像真人用户一样走完整个流程。在 Web 应用场景下，Claude 的端到端验证表现随之明显变好——截图通过 Puppeteer MCP 采集，能看到仅凭读代码发现不了的 bug。

仍有未解的限制：视觉能力和浏览器自动化工具本身有边界。例如 Puppeteer MCP 看不到浏览器原生的 alert 弹窗，依赖这类弹窗的功能就更容易带 bug。

## 快速上手：每次开窗的固定动作

所有铺垫到位后，每个编码代理开场都要走三步。步骤很基础，但每个会话省下的 token 是实打实的：

1. 跑 `pwd` 确认工作目录——只能改这个目录下的文件。
2. 读 git log 和进度文件，搞清楚最近在做什么。
3. 读功能列表，挑**优先级最高且尚未完成**的那一项。

再往前一步，是让初始化代理写 `init.sh`：一条命令起开发服务器，然后先跑一遍基础端到端测试，再动新功能。在 claude.ai 克隆里，这意味着每次都先起本地服务，用 Puppeteer MCP 新建对话、发一条消息、收到回复——先确认应用没被上一轮搞坏，坏了就地修；如果直接开新功能，问题只会更大。

原文给出的典型开场（节选）：

```text
[Assistant] I'll start by getting my bearings and understanding the current state of the project.
[Tool Use] <bash - pwd>
[Tool Use] <read - claude-progress.txt>
[Tool Use] <read - feature_list.json>
[Assistant] Let me check the git log to see recent work.
[Tool Use] <bash - git log --oneline -20>
[Assistant] Now let me check if there's an init.sh script to restart the servers.
<Starts the development server>
[Assistant] ... let me navigate to the application and verify that some fundamental features are still working.
<Tests basic functionality>
<Starts work on a new feature>
```

## 失败模式与对策

| 失败模式 | 初始化代理做什么 | 编码代理做什么 |
|---|---|---|
| 过早宣布整个项目完成 | 按输入规格建一份结构化 JSON 功能列表，逐条写端到端描述 | 会话开始先读功能列表，只挑一个功能开工 |
| 留下带 bug 或未记录的环境 | 建好初始 git 仓库和进度记录文件 | 开场读进度文件和 git log，在开发服务器上跑基础测试；收尾写 commit 和进度更新 |
| 功能没测就标记完成 | 建好功能列表 | 自己验证所有功能，仔细测过才标 `passing` |
| 花时间研究怎么把应用跑起来 | 写一个能起开发服务器的 `init.sh` | 开场先读 `init.sh` |

四行压成一句：**初始化代理负责把隐性知识写成文件，编码代理负责每次开场读文件、收场写文件。**

## 未来工作

- **单 agent 还是多 agent，没有定论**。一个通用编码 agent 是否在各环节都最优，还是拆出测试 agent、质量保证 agent、代码清理 agent 更好，原文明确说仍不清楚。
- **结论目前只覆盖全栈 Web 开发**。这些经验能否迁移到科学研究、金融建模这类长周期任务，是下一步要验证的方向。

## 关联

- 模型层与 Harness 层的分工：见 [Harness 是什么](01-Harness是什么.md)。本笔记讨论的是 Harness 层如何为长任务补上「记忆」与「验收」。
- 上下文工程：压缩与上下文管理是这里的前提，见 [上下文腐化与长时程策略](../02-上下文工程/02-上下文腐化与长时程策略.md)；原文的结论是压缩不足以替代显式的状态文件。
- 长任务与循环执行：见 [长任务与 Ralph Loop](../01-Agent心法/03-长任务与Ralph-Loop.md)。`init.sh` + 进度文件 + git 的组合，可以看作把循环执行的外部状态落成文件。
- 多模型分工与编排：见 [多模型分工与编排](../01-Agent心法/02-多模型分工与编排.md)。初始化/编码两段式，是「按阶段换提示词」，不是「按阶段换模型」。

## 来源

- Clippings 原文标题：Effective harnesses for long-running agents
- 原文出处：Anthropic Research，https://www.anthropic.com/research/effective-harnesses-for-long-running-agents（2025-11-26，作者 Justin Young）
