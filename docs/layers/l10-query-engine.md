# Layer 10：QueryEngine 与系统 Prompt 拼装

[English](./l10-query-engine.en.md) | 中文

## 核心问题

为什么 `QueryEngine.ts` 不是“再包一层 query”，而是会话级 orchestration 中心？

## 建议先复习

- `l1-startup`
- `l2-agent-loop`
- `l9-context`

## 先看源码

- `QueryEngine.ts`
- `bootstrap/state.ts`
- `constants/prompts.ts`

## 关键搜索词

- `class QueryEngine`
- `before_getSystemPrompt`
- `after_getSystemPrompt`
- `system_message_yielded`
- `fetchSystemPromptParts`

## 这一层要观察什么

- 系统 Prompt 的默认部分、追加部分、memory mechanics prompt 是怎么组合出来的
- slash command 处理、消息持久化、技能/插件加载为什么放在 query 之前
- QueryEngine 为什么既像“会话控制器”，又像“主循环前的 staging 区”

## 源码证据

- `QueryEngine.ts:184`：`export class QueryEngine`
- `QueryEngine.ts:284-301`：系统 Prompt 片段获取前后都有 profiler checkpoint
- `QueryEngine.ts:554`：`system_message_yielded`

## 这一层真正学什么

`query.ts` 解决的是“这一轮怎么跑”，`QueryEngine.ts` 解决的是“这一轮开始前，整个会话需要准备什么”。如果你想理解 Claude Code 为什么能把 slash commands、memory、skills、plugins、structured output 放进同一个统一入口，这一层比 loop 本身更关键。

## 看完后请回答

1. 为什么系统 Prompt 拼装发生在 QueryEngine，而不是零散落在各个工具里？
2. 为什么“记录 transcript”要在进入主循环前处理？
3. QueryEngine 和 REPL 的边界是什么？
