# Claude Code 深度解析

[English](./README_EN.MD) | 中文

> 一个面向源码学习的 Claude Code 教程仓库：既能带你跑通直觉，也能带你顺着真实调用链深入架构。

## 这是什么

这个仓库把 Claude Code 的学习拆成两条路线：

- `快速理解 Claude Code`：先跑示例，建立启动、Agent Loop、工具系统和权限模型的直觉。
- `深入源码分析`：按真实文件、关键符号和设计决策去读 TypeScript 源码。

仓库内容分四层：

- `examples/`：9 个可运行 Python 示例，用来建立直觉
- [docs/source-map.md](./docs/source-map.md)：源码调用链总导图
- `docs/layers/`：每一层的中英双语深挖文档
- [PHILOSOPHY.MD](./PHILOSOPHY.MD)：设计哲学与工程权衡总结

`claudecode_src/` 仅供本地研究，已加入 `.gitignore`，不会随本仓库上传。

## 先从哪开始

### 路线 A：快速理解 Claude Code

1. 运行 `python examples/l1_startup.py`
2. 阅读 [docs/layers/l1-startup.md](./docs/layers/l1-startup.md)
3. 继续跑 `l2`、`l3`、`l7`，先建立 loop、工具和权限直觉
4. 最后回看 [PHILOSOPHY.MD](./PHILOSOPHY.MD)，理解“为什么这样设计”

### 路线 B：深入源码分析

1. 先读 [docs/source-map.md](./docs/source-map.md)
2. 再读 `l2 -> l8 -> l7 -> l9 -> l6`
3. 边读边在 `claudecode_src/src/` 中搜索关键符号：
   - `query`
   - `queryLoop`
   - `SYSTEM_PROMPT_DYNAMIC_BOUNDARY`
   - `BASH_SECURITY_CHECK_IDS`
   - `SyntheticOutputTool`

## 快速热身

```bash
pip install openai python-dotenv
export DEEPSEEK_API_KEY=你的key

python examples/l1_startup.py
python examples/l1_startup.py --print "hello"
python examples/l1_startup.py serve
```

如果你没有 API Key，也可以先学习这些无需联网的层：

- `l1_startup.py`
- `l3_tool_system.py`
- `l4_ui_ink.py`
- `l5_state_commands.py`
- `l6_advanced.py`
- `l7_permissions.py`
- `l9_context_mgmt.py`

## 9 层学习地图

| Layer | 先跑什么 | 重点源码 | 这一层真正要学什么 |
|---|---|---|---|
| L1 启动与入口 | `examples/l1_startup.py` | `main.tsx`, `setup.ts`, `entrypoints/` | Claude Code 如何启动、分流、建立会话 |
| L2 Agent Loop | `examples/l2_agent_loop.py` | `query.ts`, `QueryEngine.ts` | 工具调用如何进入循环并退出 |
| L3 工具系统 | `examples/l3_tool_system.py` | `Tool.ts`, `tools.ts`, `tools/*/` | 工具为什么是 schema + 执行函数 |
| L4 UI / Ink | `examples/l4_ui_ink.py` | `components/`, `ink.ts` | 终端 UI 为什么能像 React 一样重渲染 |
| L5 状态与命令 | `examples/l5_state_commands.py` | `state/`, `commands/`, `history.ts` | 消息历史、用户设置、斜杠命令如何组织 |
| L6 高级机制 | `examples/l6_advanced.py` | `skills/`, `coordinator/`, `memdir/` | 技能、多 Agent、记忆、费用统计的边界 |
| L7 权限系统 | `examples/l7_permissions.py` | `bashPermissions.ts`, `bashSecurity.ts` | 为什么权限设计是三层，而不是一次询问 |
| L8 Streaming | `examples/l8_streaming.py` | `query.ts`, `services/api/claude.ts` | 为什么核心抽象是 async generator |
| L9 Context 管理 | `examples/l9_context_mgmt.py` | `utils/context.ts`, `constants/prompts.ts` | Claude Code 如何保住上下文和 prompt cache |

对应的双语深挖文档见：

- 中文索引：[`docs/layers/README.md`](./docs/layers/README.md)
- 英文索引：[`docs/layers/README.en.md`](./docs/layers/README.en.md)

## 必读导图与深挖

- [源码导图（中文）](./docs/source-map.md)
- [Source Map (English)](./docs/source-map.en.md)
- [Layer 深挖目录（中文）](./docs/layers/README.md)
- [Layer Deep-Dive Index (English)](./docs/layers/README.en.md)
- [设计哲学（中文）](./PHILOSOPHY.MD)
- [Design Philosophy (English)](./PHILOSOPHY_EN.MD)
- [源码导航手册（中文）](./docs/source-navigation.md)
- [Source Navigation Guide (English)](./docs/source-navigation.en.md)
- [学习练习册（中文）](./docs/exercises.md)
- [Study Exercises (English)](./docs/exercises.en.md)
- [FAQ（中文）](./docs/faq.md)
- [FAQ (English)](./docs/faq.en.md)
- [文章选题路线（中文）](./docs/articles/series.md)
- [Article Roadmap (English)](./docs/articles/series.en.md)

## 进阶深挖专题

如果你已经走完 9 层示例，下一步建议直接读这些专题：

- [L10 QueryEngine 与系统 Prompt 拼装](./docs/layers/l10-query-engine.md)
- [L11 API Streaming 与事件模型](./docs/layers/l11-api-streaming.md)
- [L12 REPL 主界面与输入系统](./docs/layers/l12-repl-ui.md)
- [L13 MCP / Hooks / Plugins 扩展面](./docs/layers/l13-mcp-hooks-plugins.md)
- [L14 Memory 提取与 Team Memory](./docs/layers/l14-memory-system.md)
- [L15 Print / Serve / Bridge 等运行模式](./docs/layers/l15-runtime-modes.md)

## 环境配置

```bash
pip install openai python-dotenv

# DeepSeek（推荐，与 l2 / l8 示例兼容）
export DEEPSEEK_API_KEY=你的key
export DEEPSEEK_MODEL=deepseek-chat   # 可选
```

需要 API Key 的示例：

- `examples/l2_agent_loop.py`
- `examples/l8_streaming.py`

## 适合怎么读

- 初学者：先跑，再看 layer 文档，再去源码里搜符号
- 有 Agent 经验的读者：先读 source map，再按调用链穿透源码
- 不要线性硬啃 `claudecode_src/src/`，而是带着问题阅读
- 每看完一层，都尝试用自己的话解释“它解决了什么工程问题”

## 免责声明

本仓库仅供个人学习与技术研究使用。`claudecode_src/` 目录中的源码已加入 `.gitignore`，不会随本仓库上传至任何公开平台。请勿将相关内容用于商业目的或侵犯 Anthropic 相关权益的行为，一切责任由使用者自行承担。
