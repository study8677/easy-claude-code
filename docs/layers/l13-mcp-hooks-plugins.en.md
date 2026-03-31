# Layer 13: MCP, Hooks, And Plugins

[中文](./l13-mcp-hooks-plugins.md) | English

## Core Question

Why does Claude Code expose multiple extension surfaces instead of one single “plugin API”?

## Review First

- `l3-tool-system`
- `l6-advanced`

## Read First

- `main.tsx`
- `plugins/builtinPlugins.ts`
- `utils/hooks/hookHelpers.ts`
- `utils/hooks/execAgentHook.ts`
- `components/mcp/*`

## Search Anchors

- `mcp`
- `createStructuredOutputTool`
- `registerStructuredOutputEnforcement`
- `getBuiltinPlugins`
- `execAgentHook`

## What To Notice

- MCP solves “bring external capabilities into the runtime”
- hooks solve “inject behavior at lifecycle boundaries”
- plugins solve “package skills/hooks/MCP into toggleable feature groups”

## Source Evidence

- `main.tsx`: heavy MCP initialization and CLI entry logic
- `plugins/builtinPlugins.ts`: built-in plugin registry and enable/disable policy
- `utils/hooks/hookHelpers.ts`: structured output enforcement helpers
- `utils/hooks/execAgentHook.ts`: hooks can run a restricted agent through `query()`

## What You Should Actually Learn

The point is not merely that Claude Code supports many extension types. The point is that different extension problems get different abstractions. A single plugin API would look simpler, but the boundaries would be blurrier.

## Questions To Answer

1. Which of MCP, hooks, and plugins is closest to capability ingress, lifecycle interception, and feature packaging?
2. Why do hooks also use `SyntheticOutputTool`?
3. If you wanted to integrate an external service, would you start with MCP or a plugin, and why?
