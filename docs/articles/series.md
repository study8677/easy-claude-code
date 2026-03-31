# Claude Code 文章路线图

[English](./series.en.md) | 中文

> 这不是待办列表，而是和仓库内容强绑定的双语文章路线。

## 首批 6 篇文章

1. `query.ts` 和 Agent Loop：Claude Code 的心脏
   - 对应仓库：`l2-agent-loop`
   - 重点：`query`, `queryLoop`, `while (true)`, 工具结果回流

2. 为什么 Claude Code 用 async generator
   - 对应仓库：`l8-streaming`
   - 重点：事件流、取消、`yield*` 组合

3. Claude Code 的三层权限系统
   - 对应仓库：`l7-permissions`
   - 重点：语义拒绝、规则匹配、用户确认

4. Prompt cache 如何反向塑造 Claude Code 的架构
   - 对应仓库：`l9-context`
   - 重点：动态边界、快照、sticky latch

5. Claude Code 的 memory 为什么是索引系统
   - 对应仓库：`l6-advanced`
   - 重点：`MEMORY.md`、typed memory、按需加载

6. SyntheticOutputTool 与 coordinator 的边界设计
   - 对应仓库：`l6-advanced`
   - 重点：structured output、worker 隔离、多 Agent 组合

## 第二批 6 篇文章

7. QueryEngine 为什么是会话 orchestration 中心
   - 对应仓库：`l10-query-engine`
   - 重点：system prompt 拼装、message staging、session orchestration

8. Claude Code 的 API streaming 不是“边输边打字”
   - 对应仓库：`l11-api-streaming`
   - 重点：event model、TTFB、stall detection、watchdog

9. REPL.tsx 为什么是交互编排层，而不是普通页面组件
   - 对应仓库：`l12-repl-ui`
   - 重点：initial message、onSubmit / onQuery、局部状态边界

10. Claude Code 为什么同时有 MCP、hooks、plugins 三套扩展面
   - 对应仓库：`l13-mcp-hooks-plugins`
   - 重点：能力接入、生命周期插桩、功能打包

11. memory extraction 与 team memory 的真正边界
   - 对应仓库：`l14-memory-system`
   - 重点：typed memory、extractMemories、team memory safety

12. 为什么 Claude Code 需要 print / serve / bridge 这些运行模式
   - 对应仓库：`l15-runtime-modes`
   - 重点：entrypoint、多运行面、bridge 长生命周期

## 写作约束

- 每篇文章都必须回链一个 layer 文档和一个 source-map 节点
- 中文和英文必须共享同一组源码证据
- 不写“泛泛而谈的 AI Agent 常识”，只写源码里能证明的设计决策
