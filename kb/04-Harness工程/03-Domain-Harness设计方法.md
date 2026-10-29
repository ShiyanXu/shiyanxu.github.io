---
layout: "kb"
title: "Domain Harness 五步法：把领域知识做进模型外面那层壳"
kb_cat: "Harness 工程"
kb_cat_key: "04-Harness工程"
kb_src: "04-Harness工程/03-Domain-Harness设计方法.md"
kb_updated: "2026-10-29"
---

# Domain Harness 五步法：把领域知识做进模型外面那层壳

> 模型决定单次推理的上限，Harness 决定任务能不能稳定收口；Domain Harness 的活法不是把 Prompt 改得更长，而是把领域知识、工具和验收标准做成 Agent 能执行、系统能验证的工程件。

## 三段演进：每一段都是被上一段的残余问题推着走

| 阶段 | 解决什么 | 为什么还不够 |
|---|---|---|
| **Prompt Engineering**（2023） | 面对空白输入框不知道说什么：用结构化、明确化的写法，把「我到底要什么」的框架讲给模型 | 那个阶段的上下文操作只有不断 Append；ChatBot 的形态扛不住真实业务 |
| **Context Engineering**（2025 年中） | ToolCall 让会话轮次变长，tool 结果、system prompt、历史状态、检索内容全塞进 Messages，注意力预算被吃光：从不断增长的信息里挑「最小但信号最强」的那组 token | 信息相关性和行为一致性变好了，长程任务的可靠性没解决 |
| **Harness Engineering**（2026） | 长程任务里人类得当 Connector，负责中间的粘合和推进动力：把「发现缺什么 → 补进环境」变成可重复的动作 | 概念仍在演进，Base Harness 与模型的绑定正在重排生态位 |

Chat Completions API 时代，对上下文的操作基本就是 Append：把用户输入和模型输出一起写进会话的 Message 序列。GPT-3.5 Turbo / GPT-4 支持 ToolCall 之后，每个 tool 的 Params 和 Response 也要回传，轮次越滚越长；而模型的上下文和注意力机制决定了注意力预算有限，光靠 Append 迟早把自己撑爆。

2025 年中，Karpathy、Tobi Lütke 等人提出 Context Engineering，随后 Anthropic 发布《Effective context engineering for AI agents》，这套理念才算正式落地。但它止步于「让模型在合适的时间看到合适的信息」。

用 ReAct 一类框架做长程任务时，执行依然很不稳定，人类还得介入承担粘合与推进。Anthropic 在长程 Agent 实践里给过一版 Harness 设计《Effective harnesses for long-running agents》，还定义了特定的 Feature List；今天 Claude Code 用 Dynamic workflows 做了相同但更强的事。

2026 年 2 月 5 日，HashiCorp 联合创始人 Mitchell Hashimoto 在《My AI Adoption Journey》里明确使用并阐述这个概念，给出两种形式：改进 AGENTS.md、改进编程工具。

> 「每当我看到 Agent 干了件坏事，就认真想办法让它不再干这件事；反过来，也努力让 Agent 能验证自己干的是好事。」

2 月 11 日，OpenAI 发布《Harness engineering: leveraging Codex in an agent-first world》。它没有定义 Harness Engineering 是什么，只给了做法：人始终在环里，但换一层抽象工作——排优先级、把用户反馈翻译成验收条件、验证结果；Agent 卡住时把它当成信号，识别缺的是工具、护栏还是文档，然后让 Codex 自己把修复写回仓库。

至此画像清楚：**不是改进模型本身，而是改进围绕模型的一切环境、产物和工具。**

## 什么是 Harness：所有不在 Model 里的部分

把 Agent 拆成 Model + Harness，**所有不在 Model 的部分都在 Harness**。这不是严格的系统架构定义，只是工程视角的简化：模型权重不变的前提下，你能主动设计的执行机制、上下文管理、工具调用、状态管理、验证反馈，都算 Harness。

真正的价值不在这个拆法，而在它带来的思路切换——把目光从「改进模型」移到「改进 Harness」。

作者的比方是人算难题：换人又难又贵，于是把目光转到人能用的工具上。算盘能算复杂题目，但如果有计算器，用计算器更快到目的地。**好的 Harness 让更差的模型也能做出更好的质量**；好模型可以向下兼容算盘，但给它计算器，它才能把精力省下来做更难的部分。

边界也在这里：Harness Engineering 的意义不只是把模型的能力表现再抬高一点，而是**降低任务成功对模型单次推理和执行正确性的依赖**。用外部工具、状态管理、验证反馈和错误恢复，把原本要模型独立完成的那部分工作交给工程系统，把不确定的推理与执行转成可验证、可恢复、可持续的任务交付。

拿代码重构举例。它不只改代码，还要保证没破坏现有功能：

- 没有 Harness：只能期待模型记得跑测试、正确理解测试结果、失败了自己修。
- 接上 Harness：把编译检查、单元测试、端到端测试、任务状态管理接进去，某次改错了，系统也能发现问题、给出反馈、引导继续修。

模型没变，变的是整个系统交付的可靠性。

## 为什么模型公司要做自己的 Harness

Harness 存在的目标就是帮模型拿到更好的结果。各家训练环境不一样，模型公司天然倾向于优化自己的 Harness 来换更好的结果和智能。这也解释了一个现象：**报 Benchmark 分数时必须说清楚用的是哪个 Harness**——Harness 本身就会影响最终结果。

设计哲学的分叉长出了不同的产品：Claude Code、Codex、Pi、Deepseek Harness。每一个背后都是对应公司对 Agent 的重新理解和定义。

## 身位选择：Base 悲观，Domain 乐观

作者把 Harness 分成两类：

| 类型 | 定义 | 判断 |
|---|---|---|
| **Base Harness** | 模型公司基于 Agent 能力抽象出来的最小集合 | 悲观 |
| **Domain Harness / Business Harness** | 把特定领域的知识、工具、业务流程和验收标准，封装成 Agent 可执行、可验证的工程系统 | 乐观 |

对 Base 悲观的逻辑：模型公司会优先适配自己的 Base Harness，用最低成本拿最好效果，再分一部分精力适配社区用得多的那几个。这种和模型的深度绑定，会让开源的 Base Harness 在持续发展中逐步被抛下——除非你能成为 The One。

Pi 可能好一点：足够简单，设计理念也简单，就算只靠模型泛化、不做特定优化，大概率也能拿到不错的结果。其他缺少独特系统能力、只想着复制官方 Agent 产品体验的通用 Harness，长期竞争空间会被压缩；和模型厂商绑定的 Harness 会逐步在自己的 Harness 上表现最好，顶多再适配一下 Codex / Claude Code。第三方 Harness 如果不够薄、不够可替换，就容易被官方 Harness 挤掉（作者的反问：Garry Tan 那个很复杂的 Gstack，你还在用吗）。

对 Domain 乐观的逻辑：领域知识太深太杂，模型公司自己啃要吃掉巨大的人力成本。与其去做 Domain Harness，不如把开放度做好（比如 Pi / Deepseek Harness），让领域专家自己来建——这也是 Deepseek Harness 设计理念显得激进的一种解释。

## Domain Harness 五步法

五步的价值不在顺序，而在第 3、4 步：先诊断失败类型，再决定改什么。

| 步骤 | 产出 | 判据 |
|---|---|---|
| 1 定义问题与验收条件 | 任务集 + 成功标准 | 每条任务能被判对错 |
| 2 选 Base Harness | 一个改得动的底座 | 能改到执行循环这一层 |
| 3 跑任务、分析 Trajectory | 失败分类 | 每个失败能归到三类之一 |
| 4 按失败类型分别修 | 验证 / 状态 / 信息 | 说得清这次修的是哪类 |
| 5 回归测评 | 四个指标的对照数据 | 不是只看成功率 |

### 1. 定义问题与验收条件

怎么做：定义这个领域的真问题，以及对应的成功标准和验收条件，用来判断 Agent 的行为对不对；围绕它设计任务集。

判据：任务集能反复跑，每条任务的成败由脚本或检查项判定，而不是「看着还行」。

### 2. 选一个 Base Harness

怎么做：选你喜欢的、熟悉的、定制方便的。作者推荐 Pi 或 Deepseek Harness；Codex 虽然和 GPT 强绑定，但 Open Core，可以快速找到它的 Base Harness 实现，再基于此做自己的实现和改造——论开放度还是前两者更好。

判据：能改到执行循环、上下文管理、工具定义这些层，而不只是换个系统提示词。

### 3. 跑任务，在失败处停下来分析 Trajectory

怎么做：让 Agent 去完成任务，失败时别急着改，先看轨迹，判断它属于哪种失败：

- 缺验证机制：无法判断对错，最终做错了；
- 缺外部状态：在长程任务中迷路，丢了自己的位置；
- 前两者都不是：单纯缺信息、缺外部输入。

判据：每个失败都能落到上面三类之一，并指向一个具体修改点。落不进去，说明第 1 步的验收条件还不够细。

### 4. 按失败类型分别修

| 失败类型 | 症状 | 修法 |
|---|---|---|
| 缺验证 | 做错了自己不知道 | 给一个能验证对错的方案（验证脚本或 Linter），要求 Agent 看完验证结果再往下推进，并检查它的行为是否符合预期 |
| 缺状态 | 长任务做到一半失了位 | 定义长程任务里必须完成的工作，让 Agent 自己跟进状态，不丢位置（Claude Code 第一版的 Todolist、后来的 Dynamic workflows 都是这个作用） |
| 缺信息 | 前两类都不是 | 才轮到设计新工具、引入更多内容作为 Prompt，把上下文补够 |

判据：改完能一句话说清「这次修的是哪一类」，而不是笼统地说效果变好了。

### 5. 回归测评

怎么做：所有修改完成后重跑一次回归测评，对比成功率、成本、耗时和副作用，用数据推动下一轮优化。

判据：四个指标一起看。成功率涨了但成本、耗时或副作用恶化，不算改好；副作用（误删、越权、破坏既有功能）要单列。跑不出对照数据的改动，不进 Baseline。

## 常见误区：把改 Prompt 当成默认优化手段

改 Prompt 文件是成本最低、最直接的优化手段，但按作者的说法，它不该成为默认选项。

- 它改的是模型的表达和注意力分配，不改系统的纠错能力：这次对了，下次不一定。
- 隐含的排序是：先补验证，再补状态，最后才是补信息。
- 跳过诊断直接改 Prompt，等于把一次系统缺陷当成一次措辞问题。

## 关联

- 「Model + Harness 两层」的切分，以及 Harness 为什么无法被模型内化：见 [Harness 是什么](01-Harness是什么.md)
- Base Harness 与 Domain Harness 的生态位判断，和「为什么模型公司要做自己的 Harness」是同一件事的两面
- 第 3、4 步依赖可观测的 Trajectory：见 [循环的五个动作](../07-工作流与循环/03-循环的五个动作.md)；长任务的状态管理可对照 [长任务与 Ralph Loop](../01-Agent心法/03-长任务与Ralph-Loop.md)
- 第 4 步「缺信息」分支的前置知识：见 [有效上下文的构成](../02-上下文工程/01-有效上下文的构成.md) 与 [上下文腐化与长时程策略](../02-上下文工程/02-上下文腐化与长时程策略.md)

## 来源

- Clippings 原文：《Everything is Harness： 从 Prompt Engineering 到 Context Engineering 再到 Harness Engineering》，白宦成，2026-10-26，https://www.ixiqin.com/2026/10/26/harness-engineering/
- AI应用/思想/Harness.md：上述原文「在这样的生态格局下，我们如何做好 Domain Harness？」一节的摘录，只含五步，不含演进与定义部分
- 原文引用：Mitchell Hashimoto《My AI Adoption Journey》（2026-02-05）；OpenAI《Harness engineering: leveraging Codex in an agent-first world》（2026-02-11）；Anthropic《Effective context engineering for AI agents》《Effective harnesses for long-running agents》
