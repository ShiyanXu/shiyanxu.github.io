---
layout: "kb"
title: "MCP 协议原理，以及它与 Computer Use 的取舍"
kb_cat: "MCP 与工具接入"
kb_cat_key: "06-MCP与工具接入"
kb_src: "06-MCP与工具接入/01-MCP协议原理与取舍.md"
kb_updated: "2026-10-29"
---

# MCP 协议原理，以及它与 Computer Use 的取舍

> 一句话：**能用 MCP 就用 MCP，MCP 覆盖不到的最后一公里交给 Computer Use。**

## MCP 是什么

Anthropic 于 **2024 年 11 月**开源的**开放协议**，用统一方式让 AI 应用连接外部工具与数据源。

核心概念：

| 概念 | 说明 |
|---|---|
| **MCP Server** | 把某个能力（文件系统、数据库、GitHub、浏览器、Blender 等）包装成标准化接口 |
| **MCP Client / Host** | AI 应用（Claude Desktop、Claude Code、Cursor 等）作为客户端连接 Server |
| **原语（Primitives）** | Tools（可调用函数）、Resources（可读数据）、Prompts（预置提示模板） |

**2025 年 12 月，MCP 被捐赠给 Linux 基金会**（Google、Microsoft、AWS 等加入），成为事实上的行业标准。这也是「Harness 不是门槛」的底气之一。

## 与 Computer Use 的对比

| | MCP | Computer Use |
|---|---|---|
| 方式 | 结构化调用（函数 / 接口） | 直接「看屏幕、动鼠标键盘」 |
| 前提 | 目标服务需提供 MCP Server | 无需任何改造 |
| 稳定性 | 高、可复现 | 低、易受界面变化影响 |
| 速度与成本 | 快、上下文开销小 | 慢、贵、耗 token |
| 适用 | 有标准化接口的系统 | 没有 API / MCP 的存量系统 |

## 三条决策规则

1. **有 MCP 用 MCP**：稳定、可复现、上下文开销小。
2. **有 API 没 MCP**：先写一个薄 MCP Server，比用 Computer Use 划算。
3. **没 API 没 MCP**：才用 Computer Use 做「最后一公里」的界面操作。

反例（#50）：做 Blender 建模时**不要用 Computer Use，也不要用官方 MCP 插件**——社区已有更稳的第三方 Blender MCP。用 Computer Use 点 Blender 的界面，慢且易错。

## MCP 与 Skill 的关系

> **MCP 提供「连接」，Skill 提供「流程」。** MCP 是货架的通道，Skill 是懂行的店员（官方「硬件店」比喻）。

- MCP 指令写「这个服务器怎么用、参数格式是什么」；
- Skill 指令写「在这个业务里，先查什么、再查什么、怎么交叉比对、输出成什么样」。

详细边界见 [Skill的边界：与MCP、Subagent、Prompt](../05-Skills体系/04-Skill与MCP-Subagent-Prompt的边界.md)。

## 为什么 MCP 会成为标准

- **一次接入，多处复用**：Server 写一次，所有支持 MCP 的客户端都能用；
- **权限可收敛**：Server 可以只暴露必要能力，比「给模型一个 shell」安全；
- **生态效应**：Blender、浏览器、数据库、GitHub 都有现成 Server。

## 关联

- 实战：Blender / MMD / adb：见 [实战案例：Blender、MMD与adb](02-实战：Blender、MMD与adb.md)
- 配置写法与安全边界：见 [MCP配置与安全边界](03-MCP配置与安全边界.md)

## 延伸阅读

- MCP 官方规范与 SDK（modelcontextprotocol.io）
- Anthropic《Extending Claude's capabilities with skills and MCP servers》
- Linux 基金会关于 MCP 的公告

**来源**：两份原报告的 MCP 背景段几乎同文（一份含对比表），已合并并补入决策规则。
