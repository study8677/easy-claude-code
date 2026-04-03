# Claude Code 学习路径

[English](./README.en.md) | 中文

> 如果 `docs/layers/` 更像参考书，这组路径页就是围绕“一次请求生命周期主线”组织出来的课程目录。目标不是看完所有文档，而是按阶段把主线站稳。

## 先记住：这组路径页在解决什么问题

这四个阶段不是通用课程列表，而是把同一条主线拆成四段：

**用户输入 → 启动 / 模式分流 → `queryLoop` 单轮推进 → 模型 / 工具 / 回流 → 状态 / UI 更新 → 下一轮或退出**

你每次只需要解决一个问题：**我现在正在主线的哪一段？这一段先搞懂什么？**

## 这一阶段先不要看什么

在走路径页时，先不要：

- 把 `docs/layers/` 当作必须从头到尾读完的课程
- 一开始就钻进 memory、runtime modes、多 Agent、plugins
- 因为看到大量文件名就切换成“全仓库导览模式”
- 在还没站稳 P1 / P2 之前，就线性硬读 `claudecode_src/src/`

如果页面写着“现在可以先忽略什么”，那不是客气话，而是为了保护你的主线感。

## 这四个阶段如何对应主线

| 阶段 | 主线位置 | 本阶段只搞懂什么 |
|---|---|---|
| [P1 第一个小时](./p1-first-hour.md) | 用户输入 → 启动 / 分流 | 请求是如何真正进入系统的 |
| [P2 Core Loop](./p2-core-loop.md) | `queryLoop` 单轮主线 | 模型、工具、结果回流如何串起来 |
| [P3 源码阅读](./p3-source-reading.md) | 主线源码直读 | 直接读关键文件与关键 symbol |
| [P4 高级架构](./p4-advanced-architecture.md) | 主线之外的边界 | permissions / memory / runtime modes 如何围绕主线展开 |

## 示例在主线与阶段中的对照

| 阶段 | 主线切片 | 先看哪些示例 | 这些示例在证明什么 |
|---|---|---|---|
| P1 | 输入 → 启动 / 分流 | `l1_startup.py`, `l4_ui_ink.py` | 请求怎样进入系统，以及 UI 怎样暴露早期状态 |
| P2 | `queryLoop` → 模型 / 工具 / 回流 | `l2_agent_loop.py`, `l3_tool_system.py`, `l7_permissions.py`, `l8_streaming.py` | 单轮主线怎样推进，工具怎样被调用，权限怎样介入，streaming 怎样贯穿全过程 |
| P3 | 主线源码直读 | `l5_state_commands.py`, `l9_context_mgmt.py` | 状态与 context 怎样支撑多轮持续运行和源码追踪 |
| P4 | 主线外的扩展边界 | `l6_advanced.py` | coordinator / cost / skills / runtime 边界怎样挂在主线之外 |

## 怎么用这组路径

1. 从 `P1` 开始，除非你已经很熟悉 agent 框架和 Claude Code 调用链。
2. 每次只完成一个阶段，不要同时打开 5 篇 deep-dive 文档。
3. 每一阶段都先跑示例，再读路径页，再用 layer 和 source-map 加固主线。
4. 如果在源码里迷路，立刻打开 [源码导航手册](../source-navigation.md)。
5. 每一阶段都先确认“我现在为什么要读这一页”，再决定要不要扩展阅读。

## 推荐顺序

### 如果你是初学者

按顺序走：

`P1 -> P2 -> P3 -> P4`

### 如果你已经做过 Agent

可以直接从：

- `P2` 开始，如果你想先确认 Claude Code 的 loop / permission / streaming 设计
- `P3` 开始，如果你已经准备好读核心源码

## 一条标准学习动作

每个阶段都尽量按这个顺序：

`run example -> read path page -> read matching layer -> open source-map -> search symbols -> open source files`

如果你不想自己拼这条链，直接看：

- [example 到源码的桥接页](../example-source-bridge.md)

## 什么时候该停下来

每一阶段只要求你稳定回答当前页面的问题。

如果你已经能：

- 说清当前阶段对应主线的哪一段
- 说清这一段为什么重要
- 搜到对应关键符号
- 用自己的话复述这一层解决了什么工程问题

就继续往下一阶段。

如果还不能，就不要急着开下一篇。

## 搭配阅读

- [example 到源码的桥接页](../example-source-bridge.md)
- [源码导图](../source-map.md)
- [Layer 深挖目录](../layers/README.md)
- [学习练习册](../exercises.md)
- [设计哲学](../../PHILOSOPHY.MD)
