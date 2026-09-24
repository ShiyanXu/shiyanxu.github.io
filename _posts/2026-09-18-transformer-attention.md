---
layout: post
title: "Transformer 注意力机制：从直觉到公式"
date: 2026-09-18
categories: [机器学习]
description: 用最小直觉理解 Q、K、V 的分工，再推导缩放点积注意力的完整计算过程，附 PyTorch 实现要点。
---

注意力机制是 Transformer 的核心。这篇文章先建立直觉，再给公式，最后落到代码。

## 一、直觉：注意力在做什么

可以把注意力理解为「带权重的检索」：对于当前词（Query），去和序列里每个词（Key）算相关度，再按相关度对所有词的信息（Value）加权求和。

- **Q（查询）**：我当前关心什么；
- **K（键）**：我能被怎样检索到；
- **V（值）**：我实际携带的信息。

## 二、公式：缩放点积注意力

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}\right) V$$

除以 $\sqrt{d_k}$ 是为了防止点积过大导致 softmax 进入梯度极小的饱和区。

## 三、PyTorch 实现要点

```python
import torch
import torch.nn.functional as F

def scaled_dot_product_attention(q, k, v):
    d_k = q.size(-1)
    scores = q @ k.transpose(-2, -1) / (d_k ** 0.5)
    weights = F.softmax(scores, dim=-1)
    return weights @ v
```

后续会补充多头注意力、KV Cache 与 Flash Attention 的笔记，欢迎关注更新。
