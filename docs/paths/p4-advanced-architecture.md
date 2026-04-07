# P4：高级架构

[English](./p4-advanced-architecture.en.md) | 中文

## 适合谁

- 已经能独立读核心文件，准备理解架构边界的人
- 想系统掌握 permissions / memory / runtime modes / coordinator 等专题的人

## 预计时间

2-3 小时

## 本阶段只搞懂什么

只有在主线已经稳定后，这一阶段才展开边界专题。你现在只需要看清四类外围边界：

1. permissions 怎样在工具执行前后保护主线
2. memory / context 怎样围绕主线提供长期支撑
3. runtime modes 怎样在 REPL 之外分叉出 print / serve / bridge
4. coordinator / structured output / extension surfaces 怎样挂接在主线周围

## 你在主线中的位置

**主线位置：** 主线已经稳定 → 向外展开 permissions / memory / runtime modes / coordinator 等边界专题

P4 不再重新教你单轮主线；它假设你已经能独立解释 P1-P3 的请求生命周期。

只有在主线稳定后，才值得研究这些外围边界：

- 哪些机制直接包围主线（比如 permissions）
- 哪些机制在主线之外维护长期能力（比如 memory）
- 哪些机制会从主线分叉成别的运行面（比如 print / serve / bridge）
- 哪些机制负责更高层协调（比如 coordinator / structured output）

## 先跑哪个 example

先从最贴主线边界的 example 开始：

```bash
python examples/l7_permissions.py
```

如果这一层已经稳定，再按专题补：

```bash
python examples/l6_advanced.py
python examples/l1_startup.py serve
python examples/l1_startup.py --print "hello"
```

这里的原则不是“把所有 example 都跑一遍”，而是按边界专题回看主线如何被包围或分叉。

## 再读哪篇 layer

建议先抓离主线最近的边界，再往外扩：

1. [L7 权限系统](../layers/l7-permissions.md)
2. [L14 Memory 提取与 Team Memory](../layers/l14-memory-system.md)
3. [L15 Print / Serve / Bridge 等运行模式](../layers/l15-runtime-modes.md)
4. [L6 高级机制](../layers/l6-advanced.md)
5. [L13 MCP / Hooks / Plugins 扩展面](../layers/l13-mcp-hooks-plugins.md)
6. [设计哲学](../../PHILOSOPHY.MD)

## 再开哪些源码文件

按边界主题分组去开：

- permissions：`claudecode_src/src/tools/BashTool/bashPermissions.ts`、`claudecode_src/src/tools/BashTool/bashSecurity.ts`
- memory：`claudecode_src/src/services/extractMemories/extractMemories.ts`、`claudecode_src/src/memdir/memdir.ts`
- runtime / coordinator：`claudecode_src/src/coordinator/coordinatorMode.ts`、`claudecode_src/src/bridge/bridgeMain.ts`、`claudecode_src/src/tools/SyntheticOutputTool/SyntheticOutputTool.ts`
- extensions：`claudecode_src/src/utils/hooks/execAgentHook.ts`、`claudecode_src/src/plugins/builtinPlugins.ts`

## 这一阶段先不要看什么

为了保持边界阅读可控，先不要这样做：

- 不要在主线还不稳时直接跳来 P4
- 不要一次追完所有 plugin / hook / MCP 细节
- 不要把每个 memory 提取流程都端到端跑完
- 不要把所有多 Agent 代码全部读完，先抓 coordinator / structured output 的边界
- 如果 `query.ts` / `QueryEngine.ts` / `services/api/claude.ts` 还说不清，先回 P3

P4 的目标是“主线之外的边界感”，不是重新制造新的信息洪水。

## 推荐阅读方式

### 如果你想先看“系统怎么扩展”

按这条线读：

1. `L13`
2. `L6`
3. 搜 `execAgentHook` / `builtinPlugins` / `ENTRYPOINT_NAME`

### 如果你想先看“长期上下文怎么围绕主线”

按这条线读：

1. `L14`
2. 搜 `buildMemoryLines` / `extractMemories`
3. 再回看 `QueryEngine` 怎么消费上下文结果

### 如果你想先看“为什么不只有一个 REPL”

按这条线读：

1. `L15`
2. `L6`
3. 搜 `bridgeMain` / `SYNTHETIC_OUTPUT_TOOL_NAME`

## 必搜符号

- `SYNTHETIC_OUTPUT_TOOL_NAME`
- `execAgentHook`
- `builtinPlugins`
- `ENTRYPOINT_NAME`
- `buildMemoryLines`
- `extractMemories`
- `bridgeMain`

## 这一阶段只回答三个问题

1. Claude Code 为什么同时保留多套扩展面，而不是只有一种 plugin 机制？
2. memory extraction 和 context 管理的真正边界是什么？
3. 为什么 REPL 之外还需要 print / serve / bridge 这些运行模式？

## 推荐练习

- [练习 6：prompt cache 和 memory 的关系](../exercises.md)
- [练习 7：比较 REPL 和非 REPL 运行模式](../exercises.md)

## 综合任务

写一段你自己的架构总结，至少覆盖这四个词中的三个：

- `extension surfaces`
- `memory index`
- `runtime modes`
- `structured output boundary`

要求：

- 不能只写功能列表
- 每个结论都要能回到具体源码符号

## 完成标准

完成这一页时，你应该能：

- 用自己的话解释 Claude Code 的主要架构边界
- 指出 permissions、memory、运行模式、扩展面分别由哪些文件承载
- 区分“功能很多”和“架构清晰”不是一回事
- 明确知道这些内容都建立在 P1-P3 的主线已经稳定之上

如果还做不到，回去补：

- `P3`，如果主线三件套还不稳
- `L6`，如果 multi-agent 和 structured output 边界还不清楚
- `L14`，如果 memory 仍然像“把更多文本塞进 prompt”
- `L15`，如果你仍把 Claude Code 理解成单纯 REPL 工具

## 走完之后

这时再回看：

- [Layer 深挖目录](../layers/README.md)
- [文章路线图](../articles/series.md)

你应该已经能自己决定先精读哪一块源码。
