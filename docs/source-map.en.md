# Claude Code Mainline Source Map

[中文](./source-map.md) | English

> This map answers one question only: where is a request on the mainline right now, and where should you trace next?

If you do not yet have the mainline in your head, go back to the [Learning Paths](./paths/README.en.md). If you are coming from an example, open the [example-to-source bridge](./example-source-bridge.en.md) first.

## How to use this map

1. First locate which mainline step you are standing on.
2. Use the input / output pair to verify what this step actually finishes.
3. Open only 1 to 2 core files first, and search 2 to 4 symbols before broadening out.
4. Follow the “next flow” line instead of reading every side system in parallel.

<a id="step-1-startup-routing"></a>
## Step 1 — Startup / mode routing

- **Mainline position:** user input → startup / mode routing
- **Input:** CLI args, current working directory, config / environment, runtime mode selection
- **Output:** a chosen entrypoint, baseline setup completion, and a decision to enter interactive, headless, bridge, or another runtime surface
- **Open these files first:**
- [`claudecode_src/src/main.tsx`](../claudecode_src/src/main.tsx)
- [`claudecode_src/src/setup.ts`](../claudecode_src/src/setup.ts)
- [`claudecode_src/src/cli/print.ts`](../claudecode_src/src/cli/print.ts)

- **Search these symbols first:**
- `main`
- `setup`
- `runHeadless`

- **Next flow:**
Move into Step 2, where the prompt, history, and tool context are actually handed to `query` / `queryLoop`.

<a id="step-2-enter-query-loop"></a>
## Step 2 — Enter `query` / `queryLoop`

- **Mainline position:** startup complete → enter the single-turn request loop
- **Input:** chosen runtime mode, current session state, user message / initial message, tool context
- **Output:** `QueryEngine` or the REPL hands one turn to `query`, and `queryLoop` starts the async-generator mainline
- **Open these files first:**
- [`claudecode_src/src/QueryEngine.ts`](../claudecode_src/src/QueryEngine.ts)
- [`claudecode_src/src/query.ts`](../claudecode_src/src/query.ts)
- [`claudecode_src/src/screens/REPL.tsx`](../claudecode_src/src/screens/REPL.tsx)

- **Search these symbols first:**
- `QueryEngine`
- `query`
- `queryLoop`
- `processInitialMessage`

- **Next flow:**
Continue to Step 3 to see how the model request is sent and why the returned assistant content becomes either “continue talking” or “call a tool.”

<a id="step-3-model-output-tool-selection"></a>
## Step 3 — Model output / tool selection

- **Mainline position:** inside `queryLoop` → call the model → parse streaming events → decide whether a `tool_use` should happen
- **Input:** current message history, system prompt, model configuration, available tool set
- **Output:** assistant text blocks, `tool_use` blocks, stop reasons, and the event stream that drives the next step
- **Open these files first:**
- [`claudecode_src/src/query.ts`](../claudecode_src/src/query.ts)
- [`claudecode_src/src/services/api/claude.ts`](../claudecode_src/src/services/api/claude.ts)
- [`claudecode_src/src/tools.ts`](../claudecode_src/src/tools.ts)
- [`claudecode_src/src/Tool.ts`](../claudecode_src/src/Tool.ts)

- **Search these symbols first:**
- `queryModelWithStreaming`
- `getTools`
- `buildTool`
- `isWithheldMaxOutputTokens`

- **Next flow:**
If the model emits `tool_use`, continue to Step 4. If it produces a directly displayable assistant result, skip ahead to Step 6 / Step 7 for state updates and exit conditions.

<a id="step-4-tool-execution"></a>
## Step 4 — Tool execution

- **Mainline position:** the model has chosen a tool → permission / safety checks run → the tool actually executes
- **Input:** `tool_use` blocks, tool registry, permission context, current working directory, security policy
- **Output:** successful tool output, denial output, or error output, all of which are turned into re-enterable `tool_result` data
- **Open these files first:**
- [`claudecode_src/src/query.ts`](../claudecode_src/src/query.ts)
- [`claudecode_src/src/tools.ts`](../claudecode_src/src/tools.ts)
- [`claudecode_src/src/tools/BashTool/bashPermissions.ts`](../claudecode_src/src/tools/BashTool/bashPermissions.ts)
- [`claudecode_src/src/tools/BashTool/bashSecurity.ts`](../claudecode_src/src/tools/BashTool/bashSecurity.ts)

- **Search these symbols first:**
- `canUseTool`
- `checkBashSecurity`
- `getCommandPermission`
- `askPermission`

- **Next flow:**
Continue to Step 5, where the tool result is reinserted into the same assistant trajectory before the next model continuation.

<a id="step-5-tool-result-reentry"></a>
## Step 5 — Tool result re-entry

- **Mainline position:** tool execution finishes → results are written back into message history → the same `queryLoop` turn keeps advancing
- **Input:** tool output, denial / error messages, existing assistant trajectory
- **Output:** user-side messages containing `tool_result`, updated turn history, and the next model-call input
- **Open these files first:**
- [`claudecode_src/src/query.ts`](../claudecode_src/src/query.ts)
- [`claudecode_src/src/services/api/claude.ts`](../claudecode_src/src/services/api/claude.ts)
- [`claudecode_src/src/utils/contentArray.ts`](../claudecode_src/src/utils/contentArray.ts)

- **Search these symbols first:**
- `tool_result`
- `queryLoop`
- `normalizeMessagesForAPI`
- `insertBlockAfterToolResults`

- **Next flow:**
Step 5 is the control-flow continuation of the same turn: once the tool result is written back into history, `queryLoop` returns to Step 3 for the next model continuation. Step 6 is not a separate control path; it is the UI / state observation surface for those same events.

<a id="step-6-state-ui-update"></a>
## Step 6 — State / UI update

- **Mainline position:** as turn events advance, the REPL and app state make the current status visible
- **Input:** query events, message history, loading / permission / notification state, initial messages, and command-entry state
- **Output:** terminal rendering, session-state updates, and user-visible messages / tool results / prompts
- **Open these files first:**
- [`claudecode_src/src/bootstrap/state.ts`](../claudecode_src/src/bootstrap/state.ts)
- [`claudecode_src/src/screens/REPL.tsx`](../claudecode_src/src/screens/REPL.tsx)
- [`claudecode_src/src/components/Messages.tsx`](../claudecode_src/src/components/Messages.tsx)
- [`claudecode_src/src/history.ts`](../claudecode_src/src/history.ts)

- **Search these symbols first:**
- `DO NOT ADD MORE STATE HERE`
- `REPL`
- `processInitialMessage`
- `setAppState`

- **Next flow:**
If the current turn is still running, keep following Step 3 / Step 5 events. If the turn has converged, move to Step 7 to see whether the runtime continues or exits.

<a id="step-7-next-turn-or-exit"></a>
## Step 7 — Next turn / exit conditions

- **Mainline position:** one turn ends → decide whether to continue, how multi-turn context survives, and what cleanup happens before exit
- **Input:** stop reasons, accumulated history, context trimming / prompt-cache state, memory-extraction triggers
- **Output:** the next user turn, a runtime exit, or background memory / context maintenance work
- **Open these files first:**
- [`claudecode_src/src/query.ts`](../claudecode_src/src/query.ts)
- [`claudecode_src/src/constants/prompts.ts`](../claudecode_src/src/constants/prompts.ts)
- [`claudecode_src/src/utils/context.ts`](../claudecode_src/src/utils/context.ts)
- [`claudecode_src/src/memdir/memdir.ts`](../claudecode_src/src/memdir/memdir.ts)
- [`claudecode_src/src/services/extractMemories/extractMemories.ts`](../claudecode_src/src/services/extractMemories/extractMemories.ts)

- **Search these symbols first:**
- `SYSTEM_PROMPT_DYNAMIC_BOUNDARY`
- `CONTEXT_1M_BETA_HEADER`
- `ENTRYPOINT_NAME`
- `buildMemoryLines`
- `extractMemories`

- **Next flow:**
If the user keeps going, return to Step 2 for the next turn. If the runtime ends, follow the current mode out. If you want the systems surrounding the mainline, continue into [layers/README.en.md](./layers/README.en.md) and [source-navigation.en.md](./source-navigation.en.md).

## Common extensions outside the spine

- For how multi-agent / structured output attaches to the mainline: start with [L6 Advanced Mechanisms](./layers/l6-advanced.en.md)
- For why memory / context affects whether the next turn can keep going: start with [L14 Memory Extraction And Team Memory](./layers/l14-memory-system.en.md)
- For why runtime modes change the entry surface without changing the core mainline: start with [L15 Print, Serve, Bridge, And Other Runtime Modes](./layers/l15-runtime-modes.en.md)
