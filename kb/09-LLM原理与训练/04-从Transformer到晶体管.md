---
layout: "kb"
title: "从 Transformer 到晶体管：把整条技术栈走一遍"
kb_cat: "LLM 原理与训练"
kb_cat_key: "09-LLM原理与训练"
kb_src: "09-LLM原理与训练/04-从Transformer到晶体管.md"
kb_updated: "2026-10-29"
---

# 从 Transformer 到晶体管：把整条技术栈走一遍

> 素材来源：Project Titania（`pengberg/titania`，#58）。Slogan：*A large language model, from transformer to transistor.*

## 它是什么

通常运行大模型要借助 PyTorch、CUDA、成熟 GPU 指令集和现成硬件，开发者很难看清整个技术栈。这个项目反其道而行：为了让一个人能理解完整链路，**从头设计模型运行时、编译器、GPU 指令集和模拟器**，并计划继续实现 RTL 硬件、FPGA 原型与芯片。

目标是构建一套「**没有黑箱**」的大模型系统。

## 当前能做什么

可以运行真实的 **Qwen3-0.6B** 解码器 Transformer：

```
模型算子被写成 GPU kernel
→ 编译器转换为 Titania 自己的 ISA 指令
→ 指令集模拟器逐条执行
```

## 现代 AI 栈的抽象层级

```
模型（Python / PyTorch）
→ 图 / 算子
→ CUDA kernel
→ PTX / SASS
→ GPU 指令集
→ 微架构
→ 晶体管
```

绝大多数工程师只在最上两层工作，导致「用得溜却不知所以然」。把每一层都实现一遍，价值在于**理解**——这与「AI 时代基本功会不会退化」的讨论形成呼应（见 [根基崩溃论](../11-职业与合规/01-根基崩溃论.md)）。

## 同类学习资源

| 资源 | 覆盖 | 特点 |
|---|---|---|
| 《Transformer 全解》（#39） | 模型结构 | 从零实现类 BERT |
| `deep-learning-notes`（#6） | PyTorch → Attention → GAN/CLIP/Diffusion/SAM3 | 成体系、含公式推导与代码 |
| 《Hands on Modern RL》（#10） | RL / RLHF | 补齐 PPO/DPO/GRPO |
| 《CUDA for Deep Learning》（#7） | kernel 层 | 到 Flash Attention |
| Titania（#58） | 全栈 | 到指令集与模拟器 |

## 延伸：一条与 AI 无关的收藏

#1 是《从零开始的 OpenWrt》教程，目录包括：基础入门（OpenWrt 与其他 Linux 的不同、路由器与串口、文件系统原理、三种固件、刷机）、移植固件、逆向固件、Flash、移植无线驱动。

它属于**嵌入式 / 网络工程**，与本批 AI 主线无关，但因信息完整作为知识留档保留。

背景：OpenWrt 是基于 Linux 的开源路由器固件发行版，用**包管理 + 可写文件系统**替代厂商固件的封闭镜像；「三种固件」通常指不同根文件系统形态（squashfs+overlay、jffs2、ext4 等），决定可恢复性与空间占用的权衡。

## 关联

- 基本功为什么重要：见 [根基崩溃论](../11-职业与合规/01-根基崩溃论.md)
- 推理性能：见 [CUDA与推理优化](03-CUDA与推理优化.md)

**来源**：#1、#6、#7、#10、#39、#58；两份原报告此段重合，OpenWrt 部分按「低权重留档」处理。
