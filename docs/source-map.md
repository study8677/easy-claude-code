# Claude Code 源码导图

[English](./source-map.en.md) | 中文

> 这份导图不是文件清单，而是“先看什么、再看什么、调用链怎么穿”的阅读地图。

## 1. 启动路径

先看这些文件：

- `main.tsx`
- `setup.ts`
- `entrypoints/`
- `QueryEngine.ts`

要回答的问题：

- CLI 参数在什么地方被解析
- 什么时候决定进入 REPL、print、serve 等模式
- 会话级别的初始化在什么阶段完成

建议搜索：

- `main_entry`
- `setup`
- `runHeadless`
- `createSyntheticOutputTool`

## 2. 单轮查询主链路

核心路径：

`QueryEngine.ts -> query.ts -> services/api/claude.ts -> tool execution -> query.ts`

先抓住这些符号：

- `query`
- `queryLoop`
- `queryModelWithStreaming`
- `isWithheldMaxOutputTokens`

这一段真正要理解的是：

- 谁在驱动一轮调用
- 事件是怎么从 API 流里转换出来的
- 工具结果是怎么回到消息历史里的
- 循环什么时候终止

## 3. 工具系统与权限路径

核心路径：

`Tool.ts -> tools.ts -> tools/BashTool/* -> bashPermissions.ts -> bashSecurity.ts`

先看：

- 工具接口如何定义
- 工具注册表如何装配
- 哪些权限在工具层处理，哪些在上层处理

建议搜索：

- `buildTool`
- `getTools`
- `canUseTool`
- `BASH_SECURITY_CHECK_IDS`

## 4. UI / 状态 / REPL 路径

核心路径：

`bootstrap/state.ts -> screens/REPL.tsx -> components/* -> ink/*`

要观察：

- 哪些东西被放进全局状态
- 哪些东西故意不进全局状态
- Ink/React 风格的终端渲染是如何组合出来的

建议搜索：

- `DO NOT ADD MORE STATE HERE`
- `REPL`
- `App`
- `render`

## 5. Context / Prompt Cache / Memory 路径

核心路径：

`constants/prompts.ts -> utils/context.ts -> utils/api.ts -> memdir/*`

这是 Claude Code 最容易被低估的一层，因为这里决定了：

- prompt cache 命中率
- 长对话是否还能继续
- 记忆为什么不直接塞满系统提示词

建议搜索：

- `SYSTEM_PROMPT_DYNAMIC_BOUNDARY`
- `context_1m_beta`
- `MEMORY.md`
- `ENTRYPOINT_NAME`

## 6. 多 Agent / Structured Output 路径

核心路径：

`tools/AgentTool/* -> tools/SyntheticOutputTool/* -> coordinator/coordinatorMode.ts`

真正值得理解的不是“会不会多 Agent”，而是：

- worker 为什么不用把所有中间状态暴露给 coordinator
- structured output 边界为什么重要
- 受限工具集如何限制子任务越权

建议搜索：

- `SYNTHETIC_OUTPUT_TOOL_NAME`
- `createSyntheticOutputTool`
- `ASYNC_AGENT_ALLOWED_TOOLS`

## 7. 推荐阅读顺序

### 如果你是初学者

1. `l1-startup`
2. `l2-agent-loop`
3. `l3-tool-system`
4. `l7-permissions`
5. `l8-streaming`
6. `l9-context`

### 如果你已经做过 Agent

1. `query.ts`
2. `services/api/claude.ts`
3. `bashSecurity.ts`
4. `constants/prompts.ts`
5. `memdir/memdir.ts`
6. `coordinatorMode.ts`

## 8. 进阶深挖专题

- [L10 QueryEngine 与系统 Prompt 拼装](./layers/l10-query-engine.md)
- [L11 API Streaming 与事件模型](./layers/l11-api-streaming.md)
- [L12 REPL 主界面与输入系统](./layers/l12-repl-ui.md)
- [L13 MCP / Hooks / Plugins 扩展面](./layers/l13-mcp-hooks-plugins.md)
- [L14 Memory 提取与 Team Memory](./layers/l14-memory-system.md)
- [L15 Print / Serve / Bridge 等运行模式](./layers/l15-runtime-modes.md)

## 9. 搭配阅读

- 哲学总结：[`../PHILOSOPHY.MD`](../PHILOSOPHY.MD)
- 导航手册：[`source-navigation.md`](./source-navigation.md)
- 文章路线：[`articles/series.md`](./articles/series.md)
- Layer 文档：[`layers/README.md`](./layers/README.md)
