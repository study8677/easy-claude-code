# Claude Code Source Navigation Guide

[中文](./source-navigation.md) | English

> The `source-map` explains which call chains to study. This guide explains how to find them quickly in the code.

## 1. The Most Useful Search Commands

Run these from the repo root:

```bash
rg -n "export async function\\* query|async function\\* queryLoop" claudecode_src/src/query.ts
rg -n "class QueryEngine|before_getSystemPrompt|system_message_yielded" claudecode_src/src/QueryEngine.ts
rg -n "queryModelWithStreaming|api_request_sent|first_chunk" claudecode_src/src/services/api/claude.ts
rg -n "buildTool|getTools|canUseTool" claudecode_src/src -S
rg -n "BASH_SECURITY_CHECK_IDS|canAutoApprove" claudecode_src/src/tools/BashTool -S
rg -n "REPL|processInitialMessage" claudecode_src/src/screens/REPL.tsx -S
rg -n "buildMemoryLines|ENTRYPOINT_NAME|extractMemories" claudecode_src/src -S
rg -n "bridgeMain|runHeadless|serve" claudecode_src/src/main.tsx claudecode_src/src/bridge -S
```

If you only remember one tool, remember `rg -n`. This codebase is much easier to learn by anchoring on symbols than by clicking through folders.

## 2. Start From a Question, Not a Directory

### I want to understand the main loop

- Read first: `query.ts`
- Then: `QueryEngine.ts`
- Search first:
  - `export async function* query`
  - `async function* queryLoop`
  - `tool_result`
- Questions to answer:
  - Who owns the state for a turn
  - Why tool results must be appended back into history
  - What ends the loop

### I want to understand system prompt assembly

- Read first: `QueryEngine.ts`
- Then: `constants/prompts.ts`
- Search first:
  - `before_getSystemPrompt`
  - `after_getSystemPrompt`
  - `fetchSystemPromptParts`
  - `SYSTEM_PROMPT_DYNAMIC_BOUNDARY`
- Questions to answer:
  - Which prompt parts are stable
  - Which parts are dynamic
  - Why this layering helps prompt cache hit rate

### I want to understand tools and permissions

- Read first: `Tool.ts`, `tools.ts`
- Then: `tools/BashTool/`
- Search first:
  - `buildTool`
  - `getTools`
  - `BASH_SECURITY_CHECK_IDS`
  - `canUseTool`
- Questions to answer:
  - Where schemas and execution functions are joined
  - Which permission checks live at which layer
  - Why security scans and approval policy are separate

### I want to understand streaming and the event model

- Read first: `query.ts`
- Then: `services/api/claude.ts`
- Search first:
  - `stream_request_start`
  - `queryModelWithStreaming`
  - `api_request_sent`
  - `first_chunk`
- Questions to answer:
  - How raw API streaming becomes internal events
  - How the query loop consumes those events
  - Why async generators fit this better than callbacks

### I want to understand the REPL and terminal UI

- Read first: `screens/REPL.tsx`
- Then: `bootstrap/state.ts`, `components/`
- Search first:
  - `export function REPL`
  - `processInitialMessage`
  - `DO NOT ADD MORE STATE HERE`
- Questions to answer:
  - Which state must be global
  - Which state is intentionally local
  - How the initial message enters the REPL

### I want to understand memory and context

- Read first: `memdir/memdir.ts`
- Then: `services/extractMemories/`, `constants/prompts.ts`
- Search first:
  - `ENTRYPOINT_NAME`
  - `buildMemoryLines`
  - `extractMemories`
  - `SYSTEM_PROMPT_DYNAMIC_BOUNDARY`
- Questions to answer:
  - How memory becomes part of system context
  - Why memory is not appended without bound
  - Where context management stops and memory extraction begins

### I want to understand print, serve, and bridge modes

- Read first: `main.tsx`
- Then: `entrypoints/cli.tsx`, `bridge/bridgeMain.ts`
- Search first:
  - `runHeadless`
  - `serve`
  - `bridgeMain`
- Questions to answer:
  - Which modes share QueryEngine
  - Which modes bypass the REPL
  - Why runtime mode dispatch happens at the entrypoint

## 3. Key Symbol Index

| Topic | Read First | Search Terms | Why It Matters |
|---|---|---|---|
| Startup | `main.tsx`, `setup.ts` | `main_entry`, `setup`, `runHeadless` | Shows how CLI mode dispatch works |
| Main loop | `query.ts` | `query`, `queryLoop`, `tool_result` | The core control flow of Claude Code |
| Session orchestration | `QueryEngine.ts` | `class QueryEngine`, `system_message_yielded` | The staging area before the loop |
| API streaming | `services/api/claude.ts` | `queryModelWithStreaming`, `first_chunk` | Converts model streaming into internal events |
| Tool registry | `Tool.ts`, `tools.ts` | `buildTool`, `getTools` | Shows how tools are exposed to the model |
| Bash security | `tools/BashTool/bashSecurity.ts` | `BASH_SECURITY_CHECK_IDS` | The core guardrail logic for shell commands |
| REPL | `screens/REPL.tsx` | `REPL`, `processInitialMessage` | The main interactive terminal screen |
| Hooks and plugins | `utils/hooks/*`, `plugins/*` | `execAgentHook`, `builtinPlugins` | How extensions enter the system |
| Memory | `memdir/memdir.ts` | `ENTRYPOINT_NAME`, `buildMemoryLines` | How memory is turned into system context |
| Multi-agent | `tools/SyntheticOutputTool/*`, `coordinator/coordinatorMode.ts` | `SYNTHETIC_OUTPUT_TOOL_NAME` | The boundary for structured output and delegation |
| Runtime modes | `bridge/bridgeMain.ts`, `entrypoints/cli.tsx` | `bridgeMain`, `serve` | The non-REPL execution surfaces |

## 4. An Efficient Reading Workflow

1. Start with one question, not one directory.
2. Use `docs/source-map.en.md` to find the relevant call chain.
3. Use the search terms in this guide to locate the functions and constants.
4. Read the entrypoint, the return or exit path, and the cleanup or finally logic first.
5. Then compare the teaching demo in `examples/` with the real source and note the extra constraints.

## 5. Avoid These Reading Mistakes

- Do not read `claudecode_src/src/` linearly from the top.
- Do not chase eight imports at once. Understand the two most important symbols in the current file first.
- Do not treat the demos as equivalent implementations. They are teaching mappings, not line-by-line replicas.

## 6. Read Alongside

- [Source Map](./source-map.en.md)
- [Layer Deep-Dive Index](./layers/README.en.md)
- [Study Exercises](./exercises.en.md)
- [FAQ](./faq.en.md)
