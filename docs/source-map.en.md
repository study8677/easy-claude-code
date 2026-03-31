# Claude Code Source Map

[中文](./source-map.md) | English

> This is not a file list. It is a reading map for the real call chains in Claude Code.

## 1. Startup Path

Start with:

- `main.tsx`
- `setup.ts`
- `entrypoints/`
- `QueryEngine.ts`

Questions to answer:

- where CLI arguments are parsed
- where mode dispatch happens
- where session-level initialization becomes stable

Useful search terms:

- `main_entry`
- `setup`
- `runHeadless`
- `createSyntheticOutputTool`

## 2. Main Query Path

Core chain:

`QueryEngine.ts -> query.ts -> services/api/claude.ts -> tool execution -> query.ts`

Anchor on these symbols first:

- `query`
- `queryLoop`
- `queryModelWithStreaming`
- `isWithheldMaxOutputTokens`

What you should really understand here:

- who drives a single turn
- how streaming API chunks become runtime events
- how tool results get appended back into history
- how and when the loop exits

## 3. Tool System And Permission Path

Core chain:

`Tool.ts -> tools.ts -> tools/BashTool/* -> bashPermissions.ts -> bashSecurity.ts`

Read for:

- how a tool is defined
- how tools are registered and filtered
- which safety checks live at the tool boundary

Useful search terms:

- `buildTool`
- `getTools`
- `canUseTool`
- `BASH_SECURITY_CHECK_IDS`

## 4. UI / State / REPL Path

Core chain:

`bootstrap/state.ts -> screens/REPL.tsx -> components/* -> ink/*`

Observe:

- what is kept in global state
- what is intentionally kept out
- how terminal rendering is composed in a React-like way

Useful search terms:

- `DO NOT ADD MORE STATE HERE`
- `REPL`
- `App`
- `render`

## 5. Context / Prompt Cache / Memory Path

Core chain:

`constants/prompts.ts -> utils/context.ts -> utils/api.ts -> memdir/*`

This layer matters because it determines:

- prompt cache hit rate
- whether long conversations can keep going
- why memory is treated as an index instead of dumping content directly

Useful search terms:

- `SYSTEM_PROMPT_DYNAMIC_BOUNDARY`
- `context_1m_beta`
- `MEMORY.md`
- `ENTRYPOINT_NAME`

## 6. Multi-Agent / Structured Output Path

Core chain:

`tools/AgentTool/* -> tools/SyntheticOutputTool/* -> coordinator/coordinatorMode.ts`

The important question is not “can it do multi-agent work?” but:

- why the coordinator does not inspect worker internals
- why structured output boundaries matter
- how restricted tool sets constrain worker authority

Useful search terms:

- `SYNTHETIC_OUTPUT_TOOL_NAME`
- `createSyntheticOutputTool`
- `ASYNC_AGENT_ALLOWED_TOOLS`

## 7. Recommended Reading Order

### If you are new

1. `l1-startup`
2. `l2-agent-loop`
3. `l3-tool-system`
4. `l7-permissions`
5. `l8-streaming`
6. `l9-context`

### If you already build agents

1. `query.ts`
2. `services/api/claude.ts`
3. `bashSecurity.ts`
4. `constants/prompts.ts`
5. `memdir/memdir.ts`
6. `coordinatorMode.ts`

## 8. Advanced Deep-Dive Topics

- [L10 QueryEngine And System Prompt Assembly](./layers/l10-query-engine.en.md)
- [L11 API Streaming And The Event Model](./layers/l11-api-streaming.en.md)
- [L12 The REPL Screen And Input System](./layers/l12-repl-ui.en.md)
- [L13 MCP, Hooks, And Plugins](./layers/l13-mcp-hooks-plugins.en.md)
- [L14 Memory Extraction And Team Memory](./layers/l14-memory-system.en.md)
- [L15 Print, Serve, Bridge, And Other Runtime Modes](./layers/l15-runtime-modes.en.md)

## 9. Read Alongside

- philosophy guide: [`../PHILOSOPHY_EN.MD`](../PHILOSOPHY_EN.MD)
- navigation guide: [`source-navigation.en.md`](./source-navigation.en.md)
- article roadmap: [`articles/series.en.md`](./articles/series.en.md)
- per-layer notes: [`layers/README.en.md`](./layers/README.en.md)
