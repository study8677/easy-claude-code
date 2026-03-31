# Layer 14：Memory 提取与 Team Memory

[English](./l14-memory-system.en.md) | 中文

## 核心问题

Claude Code 的 memory 为什么不只是 `MEMORY.md`，而是包含 typed memory、extractMemories、team memory 的完整系统？

## 建议先复习

- `l6-advanced`
- `l9-context`

## 先看源码

- `memdir/memdir.ts`
- `services/extractMemories/extractMemories.ts`
- `services/extractMemories/prompts.ts`
- `memdir/teamMemPaths.ts`
- `memdir/teamMemPrompts.ts`

## 关键搜索词

- `ENTRYPOINT_NAME`
- `buildMemoryLines`
- `Build the typed-memory`
- `extractMemories`
- `team memory`

## 这一层要观察什么

- 为什么 memory taxonomy 被限制成四种类型
- 为什么新 memory 的写入和 index 更新要明确分两步
- team memory 为什么需要单独的 path / prompt / safety 校验

## 源码证据

- `memdir/memdir.ts:34`：`ENTRYPOINT_NAME = 'MEMORY.md'`
- `memdir/memdir.ts:188`：typed-memory behavioral instructions
- `services/extractMemories/extractMemories.ts`：对话结束后的 memory extraction 流程
- `memdir/teamMemPaths.ts`：team memory 路径和逃逸校验

## 这一层真正学什么

Claude Code 的 memory 系统不是“长期聊天记录”。它更像一个受约束的知识维护系统：写入方式受控、索引很短、内容按类型组织、团队和个人记忆分边界存放。

## 看完后请回答

1. 为什么 `MEMORY.md` 只适合做入口索引，不适合存内容？
2. extractMemories 为什么要在对话后异步提取，而不是每轮实时改 memory？
3. team memory 比个人 memory 多了哪类风险控制？
