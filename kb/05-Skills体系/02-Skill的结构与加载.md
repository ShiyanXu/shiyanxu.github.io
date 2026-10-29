---
layout: "kb"
title: "Skill 的结构与渐进式披露"
kb_cat: "Skills 体系"
kb_cat_key: "05-Skills体系"
kb_src: "05-Skills体系/02-Skill的结构与加载.md"
kb_updated: "2026-10-29"
---

# Skill 的结构与渐进式披露

> 官方定义：一个 Skill 就是一个**目录**，核心是 `SKILL.md`。来源 #15 的 info-digest 图解、Anthropic Agent Skills 规范。

## 目录结构

```
my-skill/
├── SKILL.md          # 必需：YAML frontmatter(name, description) + Markdown 指令
├── scripts/          # 可选：可执行代码
├── references/       # 可选：参考资料
└── assets/           # 可选：模板等素材
```

## frontmatter 的两个字段

| 字段 | 作用 | 写法要点 |
|---|---|---|
| `name` | 唯一标识 | 短、动词或领域名，别用「助手」「工具」这类泛词 |
| `description` | **触发条件** | 写「什么时候用」，不写「这是什么」；包含用户可能说出的关键词 |

`description` 是整个 Skill 里最重要的一行：**它决定 Skill 会不会被加载**。写「一个帮助整理资讯的技能」几乎不会被触发；写「当用户提供新闻链接或资讯片段、需要生成社交平台文案时使用」才会。

## 渐进式披露（Progressive Disclosure）

Skill 的分层加载机制：

1. **元数据层**：启动时只把每个 Skill 的 `name` + `description` 预载进系统提示词，开销极小；
2. **指令层**：任务匹配时，才加载 `SKILL.md` 正文；
3. **资源层**：仅在需要时再读取 `scripts/`、`references/`、`assets/` 中的具体文件。

意义：**技能数量可以很多，但常驻上下文开销几乎不变**。这也是 Skill 能形成「生态」的结构性原因——安装 100 个 Skill 不会让模型变笨。

## 推论：写得克制比写得全更重要

- 正文只放「模型不知道、又必须知道」的东西：判断标准、步骤、反例。
- 大段参考资料放 `references/`，别塞进正文——正文是每轮都可能被加载的。
- 脚本放 `scripts/`，让模型调用而不是让模型重写。
- 这与「用超高档写 Skill 反而抓不住重点」是同一件事的两面（见 [写Skill与迭代Skill](03-写Skill与迭代Skill.md)）。

## 一个最小可用示例

```markdown
---
name: info-digest
description: 把 AI 资讯整理成可直接发布的中文短内容。当用户提供新闻链接或资讯片段、需要生成社交平台文案时使用。
---

# Info Digest

## 写作原则
1. 站在读者关心的角度写，不自嗨式表达。
2. 联网检索核对事实，避免放大错误资讯。
3. 交代清楚背景，让不了解概念的读者也能读懂来龙去脉。
4. 输出纯文本、短小精炼，开头有吸引力。

## 输出格式
- 标题：一句话点明价值
- 正文：3-5 句
- 结尾：一个引导互动的问题
```

注意它没有做的事：没有解释「什么是 AI 资讯」，没有罗列平台规则，没有附 20 个范文。**只写了模型不知道的四条原则和一个格式。**

## 自检清单

- [ ] `description` 里有没有用户会说的原话？
- [ ] 正文有没有超过 100 行？超了就该拆 `references/`。
- [ ] 每条指令是否可验证（做完能看出对错）？
- [ ] 有没有和已有 Skill 触发条件重叠？重叠会导致「抢触发」。
- [ ] 有没有把「工具用法」写进来？那属于 MCP 的地盘（见下一篇）。

## 关联

- Skill 与 MCP 的边界：见 [Skill的边界：与MCP、Subagent、Prompt](04-Skill与MCP-Subagent-Prompt的边界.md)
- 官方规范与 SDK：agentskills.io

**来源**：#15 的 info-digest 示例、Anthropic Agent Skills 官方结构；两份原报告此段几乎逐字相同，已合并。
