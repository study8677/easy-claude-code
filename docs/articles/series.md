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

## 写作约束

- 每篇文章都必须回链一个 layer 文档和一个 source-map 节点
- 中文和英文必须共享同一组源码证据
- 不写“泛泛而谈的 AI Agent 常识”，只写源码里能证明的设计决策
