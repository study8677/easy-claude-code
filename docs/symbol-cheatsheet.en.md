# Symbol Cheat Sheet

[中文](./symbol-cheatsheet.md) | English

> Every row is a verified symbol from the real source. Check this table before searching blindly.

Use with IDE global search (⌘P / Ctrl+P for files, ⌘F / Ctrl+F for symbols) inside `claudecode_src/src/`.

---

## Core Loop

| Symbol | File | Line | Description |
|--------|------|------|-------------|
| `export async function* query` | `query.ts` | 219 | Outer generator entry — handles startup and teardown |
| `async function* queryLoop` | `query.ts` | 241 | Inner loop, home of the `while(true)` |
| `while (true)` | `query.ts` | 307 | Agent Loop body — calls model and executes tools each turn |
| `isWithheldMaxOutputTokens` | `query.ts` | 175 | Error-withholding mechanism: hides intermediate errors until recovery is confirmed |
| `queryModelWithStreaming` | `services/api/claude.ts` | — | Issues the API call and returns a streaming event flow |
| `first_chunk` | `services/api/claude.ts` | — | Event emitted when the first streaming token arrives |
| `stream_request_start` | `query.ts` | — | Event yielded at the start of each queryLoop iteration |
| `tool_result` | `query.ts` | — | Role/type used when writing tool output back into message history |
| `normalizeMessagesForAPI` | `utils/contentArray.ts` | — | Converts internal message format to the shape the API expects |

---

## Startup / Mode Routing

| Symbol | File | Line | Description |
|--------|------|------|-------------|
| `main` | `main.tsx` | — | CLI entry point — calls setup then routes to entrypoints |
| `setup` | `setup.ts` | — | Detects working directory, API key, permission mode, creates session_id |
| `runHeadless` | `entrypoints/` | — | Non-interactive runtime entry |
| `bridgeMain` | `entrypoints/` | — | Bridge mode entry (used by IDE extensions and external integrations) |
| `processInitialMessage` | `screens/REPL.tsx` | — | Injects startup-time messages into the interactive flow |

---

## Tool System

| Symbol | File | Line | Description |
|--------|------|------|-------------|
| `getTools` | `tools.ts` | — | Returns the full tool list for the current session (including MCP tools) |
| `buildTool` | `tools.ts` | — | Wraps a tool definition into a JSON schema the model can see |
| `canUseTool` | `tools/BashTool/bashPermissions.ts` | — | Permission check entry — decides whether a tool is allowed to run |
| `MCPTool` | `tools/MCPTool/` | — | Wraps MCP tools into the same Tool interface as built-in tools |
| `ASYNC_AGENT_ALLOWED_TOOLS` | `coordinator/coordinatorMode.ts` | 2 | Whitelist of tools a sub-agent may use in multi-agent mode |
| `SyntheticOutputTool` | `coordinator/coordinatorMode.ts` | 88–97 | What the coordinator sees: sub-agent exposes only final result, not intermediate state |

---

## Permission System

| Symbol | File | Line | Description |
|--------|------|------|-------------|
| `checkBashSecurity` | `tools/BashTool/bashSecurity.ts` | — | Entry for all 23 security checkers (layer 1: semantic denial) |
| `BASH_SECURITY_CHECK_IDS` | `tools/BashTool/bashSecurity.ts` | — | Numeric IDs for the 23 checkers (numeric IDs, not string names) |
| `getCommandPermission` | `tools/BashTool/bashPermissions.ts` | — | Rule-matching layer: checks against existing allow/deny rules |
| `askPermission` | `tools/BashTool/bashPermissions.ts` | — | User-confirmation layer: pops a prompt and waits for approval |

---

## State / UI

| Symbol | File | Line | Description |
|--------|------|------|-------------|
| `DO NOT ADD MORE STATE HERE` | `bootstrap/state.ts` | 31 | Global state discipline boundary — explicit comment against expansion |
| `setAppState` | `bootstrap/state.ts` | — | The only entry point for mutating global AppState |
| `REPL` | `screens/REPL.tsx` | — | Root component of the interactive terminal, drives QueryEngine |

---

## Prompt Cache / Context

| Symbol | File | Line | Description |
|--------|------|------|-------------|
| `SYSTEM_PROMPT_DYNAMIC_BOUNDARY` | `constants/prompts.ts` | 114–115 | Marker separating static prefix from dynamic parts — protects cache hit rate |
| `CONTEXT_1M_BETA_HEADER` | `constants/prompts.ts` | — | Beta header for enabling 1M context window |
| `reversibility and blast radius` | `constants/prompts.ts` | 258 | Verbatim phrase from system prompt encoding the reversibility-first principle |

---

## Memory System

| Symbol | File | Line | Description |
|--------|------|------|-------------|
| Four memory type definitions | `memdir/memdir.ts` | 189 | `user / feedback / project / reference` |
| MEMORY.md limits | `memdir/memdir.ts` | 34–37 | 200-line cap + byte limit to prevent context bloat |
| `buildMemoryLines` | `memdir/memdir.ts` | — | Formats memory files and injects them into the system prompt |
| `extractMemories` | `services/extractMemories/` | — | Asynchronously extracts memorable information after a conversation ends |
| `ENTRYPOINT_NAME` | `constants/prompts.ts` | — | Identifier used by the memory system to distinguish session entry type |

---

## Sticky Latch (cache stability mechanism)

| Symbol | File | Line | Description |
|--------|------|------|-------------|
| `AFK_MODE` latch | `bootstrap/state.ts` | 226–233 | Once set, never auto-resets — prevents system prompt churn from breaking cache |
| `FAST_MODE` latch | `bootstrap/state.ts` | 226–233 | Same design — comment explicitly mentions `~50-70K token prompt cache` |

---

## How to search these symbols

```bash
# Search exact symbol name under claudecode_src/src/
grep -r "queryModelWithStreaming" claudecode_src/src/ --include="*.ts"

# Search within a specific file
grep -n "while (true)" claudecode_src/src/query.ts

# Search verbatim comment text
grep -r "DO NOT ADD MORE STATE" claudecode_src/src/
```

Or use IDE global symbol search (VS Code: ⌘T / Ctrl+T).
