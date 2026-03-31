# Layer 13：MCP / Hooks / Plugins 扩展面

[English](./l13-mcp-hooks-plugins.en.md) | 中文

## 核心问题

Claude Code 的扩展点为什么不是一个单一“插件接口”，而是 MCP、hooks、builtin plugins 三套机制并存？

## 建议先复习

- `l3-tool-system`
- `l6-advanced`

## 先看源码

- `main.tsx`
- `plugins/builtinPlugins.ts`
- `utils/hooks/hookHelpers.ts`
- `utils/hooks/execAgentHook.ts`
- `components/mcp/*`

## 关键搜索词

- `mcp`
- `createStructuredOutputTool`
- `registerStructuredOutputEnforcement`
- `getBuiltinPlugins`
- `execAgentHook`

## 这一层要观察什么

- MCP 解决的是“把外部能力接进来”
- hooks 解决的是“在生命周期节点插入行为”
- plugins 解决的是“把 skills/hooks/mcp 作为一组可开关功能分发”

## 源码证据

- `main.tsx`：大量 MCP 初始化与 CLI 入口逻辑
- `plugins/builtinPlugins.ts`：builtin plugin registry 与启用/禁用策略
- `utils/hooks/hookHelpers.ts`：`createStructuredOutputTool` 与 structured output enforcement
- `utils/hooks/execAgentHook.ts`：hook 通过 `query()` 运行一个受限 agent

## 这一层真正学什么

这层的重点不是“Claude Code 支持很多扩展”，而是“不同扩展问题用不同抽象”。如果都压成一个 plugin API，系统会更统一，但边界会更糊；Claude Code 选择了把能力按职责拆开。

## 看完后请回答

1. MCP、hook、plugin 三者分别像“能力接入”“生命周期拦截”“功能打包”中的哪一种？
2. 为什么 hook 也会用到 `SyntheticOutputTool`？
3. 如果你要接入一个外部服务，优先考虑 MCP 还是 plugin，为什么？
