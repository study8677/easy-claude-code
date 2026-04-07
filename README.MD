# Claude Code 深度解析

[English](./README_EN.MD) | 中文

> 一个面向源码学习的 Claude Code 教程仓库：先抓住“一次请求如何流动”的主线，再顺着示例、路径页和真实调用链把架构读透。

## 你现在要抓的唯一主线

这个仓库的第一目标，不是记住所有层，也不是一开始就把所有文档全部看完。

你先要抓住 Claude Code 里 **一次请求如何流动**：

**用户输入 → 启动 / 模式分流 → 进入 `query` / `queryLoop` → 模型产出 → 工具调用 → 工具执行 → 工具结果回流 → 状态 / UI 更新 → 下一轮或退出**

只要这条主线稳定了，后面的 permissions、memory、runtime modes、skills、coordinator 才会有位置感。

## 现在先不要试图同时理解什么

第一轮学习里，先不要把这些当成主战场：

- 不要一上来线性硬啃 `claudecode_src/src/`
- 不要先把 `docs/layers/` 当成主线课程
- 不要先钻进多 Agent、memory、runtime modes、插件边界
- 不要试图一次性记住所有文件名；先记住“请求下一步会流向哪里”

如果你暂时只能稳定回答“这次请求现在位于主线哪一段”，你就走在正确方向上。

## 这个仓库里每类材料是干什么的

- `examples/`：9 个可运行 Python 示例，把主线拆成可观察切片
- [`docs/paths/`](./docs/paths/README.md)：正式学习路线；告诉你 P1-P4 每阶段只学什么
- [`docs/example-source-bridge.md`](./docs/example-source-bridge.md)：把示例、主线位置、source-map 和真实源码对起来
- [docs/source-map.md](./docs/source-map.md)：按调用链追踪主线与关键分支
- `docs/layers/`：当你在某个环节卡住时，用来补细节与边界感

补充材料：

- [PHILOSOPHY.MD](./PHILOSOPHY.MD)：设计哲学与工程权衡总结
- [docs/symbol-cheatsheet.md](./docs/symbol-cheatsheet.md)：关键符号速查卡（文件名 + 行号 + 一句话说明）
- [docs/source-navigation.md](./docs/source-navigation.md)：源码符号搜索手册
- [docs/exercises.md](./docs/exercises.md)：练习册
- [docs/faq.md](./docs/faq.md)：常见问题

## 9 个 examples 在主线中的位置

| Example | 主线位置 | 读者要抓住什么 |
|---|---|---|
| `l1_startup.py` | 用户输入 → 启动 / 分流 | CLI 如何进入正确运行模式，并建立 session / 入口上下文 |
| `l2_agent_loop.py` | 进入 `queryLoop` → 单轮请求推进 | 一轮请求怎样驱动模型、工具与退出条件 |
| `l3_tool_system.py` | 模型产出 → 工具调用 | 工具为什么是 schema + execute，而不是随意 JSON |
| `l4_ui_ink.py` | 状态 / UI 更新 | 终端 UI 怎样把主线当前状态显示出来 |
| `l5_state_commands.py` | 状态组织 / 命令入口 | 状态对象与命令入口怎样支撑多轮对话 |
| `l6_advanced.py` | 主线外的扩展边界 | coordinator / cost / skills 这类扩展怎样挂在主线周围 |
| `l7_permissions.py` | 工具执行前的关口 | 权限系统怎样在工具真正执行前介入 |
| `l8_streaming.py` | 主线的贯穿方式 | 为什么核心抽象更像 async generator / 事件流 |
| `l9_context_mgmt.py` | 多轮持续运行 | context 管理如何保护主线继续前进而不失控 |
| `l10_mcp.py` | 主线外扩展 | MCP 协议如何把外部工具注入 Claude Code 的工具注册表 |

## 5 分钟开始

### 路线 A：无需 API Key

先安装依赖：

```bash
pip install openai python-dotenv
```

然后运行：

```bash
python examples/l1_startup.py
python examples/l3_tool_system.py
python examples/l7_permissions.py
```

你会看到：

- `l1_startup.py`：请求怎样真正进入系统
- `l3_tool_system.py`：模型为什么不会“直接做工具”，而要走 schema + execute
- `l7_permissions.py`：工具执行前为什么要经过权限关口

下一步直接去：

- [学习路径：P1 第一个小时](./docs/paths/p1-first-hour.md)

### 路线 B：有 API Key，想先看到核心 loop

```bash
pip install openai python-dotenv
export DEEPSEEK_API_KEY=你的key

python examples/l2_agent_loop.py
python examples/l8_streaming.py
```

你会看到：

- `l2_agent_loop.py`：一轮请求如何推进模型调用、工具执行、结果回写与退出
- `l8_streaming.py`：为什么主线不是单点函数调用，而更像持续事件流

下一步直接去：

- [学习路径：P2 Core Loop](./docs/paths/p2-core-loop.md)

## 读完首页后，下一步去哪

- 想按阶段学：看 [学习路径（中文）](./docs/paths/README.md)
- 想知道“某个示例之后去读哪里”：看 [example 到源码的桥接页](./docs/example-source-bridge.md)
- 想直接追真实调用链：看 [源码导图](./docs/source-map.md)
- 想在源码里搜索 symbol：看 [源码导航手册](./docs/source-navigation.md)

## `claudecode_src/` 到底是什么

`claudecode_src/` 是本地研究用的 Claude Code 源码镜像。

需要明确几点：

- 这个仓库的教学文档和 Python 示例本身可以独立阅读
- 真正的“对照源码阅读”依赖你本地存在 `claudecode_src/`
- `examples/` 不是逐行复刻源码，而是“保留架构形状的教学版映射”
- `claudecode_src/` 已加入 `.gitignore`，不会跟随这个教程仓库公开上传

## 继续深入

- [Layer 深挖目录（中文）](./docs/layers/README.md)
- [Layer Deep-Dive Index (English)](./docs/layers/README.en.md)
- [设计哲学（中文）](./PHILOSOPHY.MD)
- [Design Philosophy (English)](./PHILOSOPHY_EN.MD)
- [文章选题路线（中文）](./docs/articles/series.md)
- [Article Roadmap (English)](./docs/articles/series.en.md)

## 免责声明

本仓库仅供个人学习与技术研究使用。`claudecode_src/` 目录中的源码已加入 `.gitignore`，不会随本仓库上传至任何公开平台。请勿将相关内容用于商业目的或侵犯 Anthropic 相关权益的行为，一切责任由使用者自行承担。
