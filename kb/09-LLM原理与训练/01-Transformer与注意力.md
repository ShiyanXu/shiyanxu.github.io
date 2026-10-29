---
layout: "kb"
title: "Transformer 与注意力机制"
kb_cat: "LLM 原理与训练"
kb_cat_key: "09-LLM原理与训练"
kb_src: "09-LLM原理与训练/01-Transformer与注意力.md"
kb_updated: "2026-10-29"
---

# Transformer 与注意力机制

> 素材来源：长文《Transformer 全解——完整拆解 Transformer 架构，并从零开始逐步编写一个类似 BERT 的模型》（#39）。本篇补齐截图之外的细节。

## 章节脉络

从「大语言模型如何预测下一个词」讲起：

```
词分词（tokenization）与 BPE → 词嵌入与位置编码
→ 用矩阵和数值示例推导 Q / K / V → 缩放点积注意力
→ 因果遮罩 → 多头注意力 → LayerNorm / FFN / 残差
→ 预训练、微调与迁移学习
```

## 关键机制

**Tokenization / BPE**
Byte-Pair Encoding 把文本切成子词单元（subword），兼顾词表大小与未登录词。中文常被切成 1–2 个字一 token 的片段——这直接决定了中文的 token 成本与上下文占用。

**位置编码**
注意力本身不含顺序信息，需注入位置。原论文用正弦函数；现代模型多用**可学习位置嵌入**或 **RoPE（旋转位置编码）**。

**Q / K / V 与缩放点积注意力**

```
Attention(Q, K, V) = softmax(QKᵀ / √d_k) V
```

- Q（Query）：我在找什么；
- K（Key）：我提供什么索引；
- V（Value）：我实际携带的信息。

除以 √d_k 是为了避免点积随维度增大而方差爆炸，导致 softmax 饱和。

完整计算流：输入嵌入 × Q/K/V 权重 → 得到 Q/K/V → Q·Kᵀ → Scaling → Softmax → ×V → Context Vector。

**因果遮罩（Causal Mask）**
GPT 类自回归模型在预测第 t 个 token 时不能看见 t 之后的内容，因此把上三角位置置为 −∞，softmax 后权重为 0。BERT 用的是双向注意力，故用 **Masked**（遮盖被预测词）而非因果遮罩。

**多头注意力**
把 Q/K/V 投影到多个子空间并行计算，捕捉不同关系（语法、指代、语义等），再拼接投影。

**LayerNorm / FFN / 残差**
LayerNorm 稳定训练；FFN（两层 MLP + 激活）提供非线性容量；残差连接（输入 + 子层输出）缓解深层梯度消失，是「能堆很深」的关键。

**预训练 → 微调 → 迁移学习**
先在无标注海量语料上自学（预测下一词 / 掩码词），再在特定任务上微调。这就是「基座模型 + 下游适配」范式的由来。

## 一个直觉

注意力不是「理解」，而是**按相关性加权取信息**：每个 token 都在问「我现在最需要谁的什么信息」，然后按相似度把信息搬过来。所谓「上下文窗口」，就是这个加权能覆盖的范围。

## 关联

- 训练与对齐（PPO/DPO/GRPO）：见 [预训练、微调与RLHF](02-预训练、微调与RLHF.md)
- 为什么长上下文贵：见 [本地部署与量化](../08-模型与推理/03-本地部署与量化.md) 的 KV Cache 一节

## 延伸阅读

- 博文《Transformer 全解》（vizuaranewsletter.com/p/the-transformers）
- 论文《Attention Is All You Need》

**来源**：#39；两份原报告的技术细节段落几乎逐条同文，已合并。
