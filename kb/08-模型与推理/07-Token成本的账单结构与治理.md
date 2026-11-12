---
layout: "kb"
title: "Token 成本的账单结构：先归因，再动手"
kb_cat: "模型与推理"
kb_cat_key: "08-模型与推理"
kb_src: "08-模型与推理/07-Token成本的账单结构与治理.md"
kb_updated: "2026-11-12"
---

# Token 成本的账单结构：先归因，再动手

> 结论：账单不是「用得多」，是三层价格（input / cached / output）× 六类驱动项。顺序应该是先归因、再按支柱砍、最后用组织治理兜住。六项一起治理，复合测算是 baseline 100% → 59%。

## 账单先拆三层

起因是计费方式变了：2026-06-01 起 Copilot 改用 GitHub AI Credits，成本公式从 `seats × headcount` 变成 `seats × usage patterns`——「用得多」从采购问题变成工程问题，也才谈得上优化。

| 层 | 里面是什么 | 特征 |
|---|---|---|
| input | 文件、prompt、历史、工具 schema、系统提示 | 每轮重发，量最大 |
| cached | 稳定前缀：instructions、项目规范、技能上下文 | 命中后走折扣价 |
| output | 可见回答 + 隐藏的 reasoning tokens | 单价最高 |

计费公式是 `cost = input + cached + output`，1 AI credit = $0.01 USD。

两个判断：agentic workflow 里 **input + cached 往往占到 70%+**；output 单价最高，而 reasoning 一般按 output 类 token 计费——所以「开高思考」既贵又慢。

## 六类驱动项对应六个支柱

| 驱动项 | 表现 | 支柱 | 可省区间 |
|---|---|---|---|
| Context | 上下文每轮重发，越大召回越差 | 只发有用上下文 | 10–14% |
| Model | 高阶 / 轻量模型的价差 | 任务匹配模型层级 | 10–14% |
| Instructions | 未缓存的规范重复计费 | 稳定前缀可缓存 | 7–10% |
| Reasoning | HIGH / MAX thinking 按输出计费 | 按任务支付思考 | 5–8% |
| Agents & Tools | agent loop + MCP schema 放大调用 | 启用而不堆积 | 3–5% |
| Sessions | 长会话历史复利膨胀 | 重置而不复利 | 5–8% |

复合效果 100% → 59%，约 41% 的降幅。**值钱的不是单点省 token，而是六项一起治理。**

## 支柱里值得记住的数字

**模型路由**：Lightweight $1.25–3/M、Versatile $5–15/M、Powerful $25–30/M。一个 11 轮的 OAuth workflow，全程高阶约 $13.75，按步骤路由后约 $2.30，约 6×。

**思考深度倍数**（相对 LOW）：MEDIUM 2–4×、HIGH 10–25×、MAX 50–80×。推荐链路是 MEDIUM 规划 → LOW 小步执行 ×N → MEDIUM 复核，HIGH / MAX 只留给复杂或高风险回合。

**工具治理**：MCP 控 schema 开销（约 5× 少）、Hooks 过滤长日志（约 50× 少的历史噪声）、Skills 按需加载（约 10× 少的项目结构探索）。一小时 feature session：未治理约 1.5M tokens / ~$4.50，治理后约 150K / ~$0.45。

**子代理与交接**：发现型任务交给子代理，文件在子上下文读一次，父线程只拿 1K 摘要（86K → 8K input，约 92%）；多阶段构建用 handoff，Planner 用强模型一次、Implementer 用轻模型、Reviewer 用通用模型（10 个 Opus turn 约 $15 → 约 $2.11）。

## 会话生命周期：四个边界动作

每轮都会重发三块——system prompt、conversation history、新消息；只有 history 会不断膨胀（示例曲线 15.3K → 3.3K → 2.3K）。

| 时机 | 动作 |
|---|---|
| 新主题 | 开新 chat |
| 中途 | `/compact <focus>` |
| 探索 | fork 分支 |
| 完成 | archive，保留引用 |

原则：一个主题一个会话，及时重置，别让历史成本复利。

## 指令文件：短、准、只在必要时进上下文

`AGENTS.md` / `copilot-instructions.md` 该保留：会引发缺陷或事故的仓库约束、测试与构建命令及失败判定、安全边界与发布禁区、短 checklist。

该剔除：通用工程常识、模型生成的冗长规则、每天变化的内容（还会让缓存失效）、与当前工作区无关的历史包袱。

判断标准一句话：**删掉这条规则后，事故概率会不会显著上升？不会，就别让它进每轮上下文。**

## 提示与输出：密度大于长度

- 输出约束直接写死：`code only`、`diff only`、`max 5 bullets`、`JSON`。解释、重述、整文件回写都会进账单。
- 输入表达走四种：精简、结构化、代码原生、宣告式。输入降幅可到约 75%。
- **中文更短 ≠ token 更省**：英文通常是 prompt 里最省 token 的语言。可以中文讨论，关键 prompt 与 instructions 用英文。
- 一次只放一项任务。多任务 prompt 会让完成度分散、验证成本上升。

## 云端 Coding Agent：成本由 issue 质量和 setup 决定

一个 agent task 可能吃掉 50K–500K tokens，压缩探索范围是最直接的节省：

- issue 写清精确描述、验收标准、reproduce steps、相关文件路径、明确 scope；
- `.github/copilot-setup-steps.yml` 预装依赖、预跑 build / test、备好环境变量与缓存；
- PR 描述带上决策；失败时返回证据，而不是空手。

## 组织治理四条

个人技巧只能省一部分，组织级要靠四个结构：**共享额度池**（统一看企业消耗）、**成本归属**（按团队 / 项目归因，找结构性 driver）、**单人上限**（异常先预警，不直接阻断生产力）、**超支护栏**（把 overage 比控在可解释范围）。

目标是在同等许可下拿到更多有效工作，而不是靠禁用工具降成本。

## 关联

- 具体动作清单（选型、缓存、压缩、限额）：见 [AI 用量成本优化](06-AI用量成本优化.md)
- 上下文为什么有限：见 [有效上下文的构成](../02-上下文工程/01-有效上下文的构成.md)
- 子代理与多 Agent 拓扑：见 [多 Agent 协作](../07-工作流与循环/04-多Agent协作.md)
- 指令文件写法：见 [AGENTS.md：给 Agent 的项目上下文文件](../13-工程实践/02-AGENTS-md与项目上下文.md)
- 提示词分层与四要素：见 [提示词的分层与工程化](../03-提示词工程/05-提示词的分层与工程化.md)
