# Example-To-Mainline Source Bridge

[中文](./example-source-bridge.md) | English

> First ask: which mainline step does this example sit on? Then ask: what real complexity does the source add at that step?

If you have not yet located the step, go back to the [mainline source map](./source-map.en.md). If you want the staged learning route, return to the [Learning Paths](./paths/README.en.md).

## Example → mainline step → next source hop

> The source files listed below are first-hop reading targets, not exhaustive ownership boundaries for that behavior.

| Example | Mainline step | What the example intentionally simplifies | Which source files to open next |
|---|---|---|---|
| `l1_startup.py` | [Step 1 — Startup / mode routing](./source-map.en.md#step-1-startup-routing) | compresses CLI parsing, global config, and runtime-mode dispatch into one startup skeleton | [`main.tsx`](../claudecode_src/src/main.tsx), [`setup.ts`](../claudecode_src/src/setup.ts), [`cli/print.ts`](../claudecode_src/src/cli/print.ts) |
| `l2_agent_loop.py` | [Step 2 — Enter `query` / `queryLoop`](./source-map.en.md#step-2-enter-query-loop) | compresses QueryEngine, turn state, and history assembly into one minimal loop | [`QueryEngine.ts`](../claudecode_src/src/QueryEngine.ts), [`query.ts`](../claudecode_src/src/query.ts) |
| `l3_tool_system.py` | [Step 3 — Model output / tool selection](./source-map.en.md#step-3-model-output-tool-selection) | compresses the real tool pool, schemas, and mode filtering into a small registry story | [`Tool.ts`](../claudecode_src/src/Tool.ts), [`tools.ts`](../claudecode_src/src/tools.ts), [`query.ts`](../claudecode_src/src/query.ts) |
| `l4_ui_ink.py` | [Step 6 — State / UI update](./source-map.en.md#step-6-state-ui-update) | compresses the Ink component tree, state slices, and message rendering into one visible feedback loop | [`bootstrap/state.ts`](../claudecode_src/src/bootstrap/state.ts), [`screens/REPL.tsx`](../claudecode_src/src/screens/REPL.tsx), [`components/Messages.tsx`](../claudecode_src/src/components/Messages.tsx) |
| `l5_state_commands.py` | [Step 6 — State / UI update](./source-map.en.md#step-6-state-ui-update) | compresses pending-message flow, command dispatch, and history sync into a simplified state machine | [`screens/REPL.tsx`](../claudecode_src/src/screens/REPL.tsx), [`history.ts`](../claudecode_src/src/history.ts), [`commands/`](../claudecode_src/src/commands) |
| `l6_advanced.py` | [Step 3 — Model output / tool selection](./source-map.en.md#step-3-model-output-tool-selection) | compresses the real multi-agent / structured-output boundary into a “restricted tools + constrained worker” sketch | [`tools/SyntheticOutputTool/`](../claudecode_src/src/tools/SyntheticOutputTool), [`coordinator/coordinatorMode.ts`](../claudecode_src/src/coordinator/coordinatorMode.ts), [`cli/print.ts`](../claudecode_src/src/cli/print.ts) |
| `l7_permissions.py` | [Step 4 — Tool execution](./source-map.en.md#step-4-tool-execution) | compresses layered permissions, auto-approval, and dangerous-command checks into one gatekeeper | [`tools/BashTool/bashPermissions.ts`](../claudecode_src/src/tools/BashTool/bashPermissions.ts), [`tools/BashTool/bashSecurity.ts`](../claudecode_src/src/tools/BashTool/bashSecurity.ts), [`query.ts`](../claudecode_src/src/query.ts) |
| `l8_streaming.py` | [Step 3 — Model output / tool selection](./source-map.en.md#step-3-model-output-tool-selection) | compresses provider event streams, chunk repair, and stop-reason handling into a readable async-generator view | [`services/api/claude.ts`](../claudecode_src/src/services/api/claude.ts), [`query.ts`](../claudecode_src/src/query.ts) |
| `l9_context_mgmt.py` | [Step 7 — Next turn / exit conditions](./source-map.en.md#step-7-next-turn-or-exit) | compresses prompt cache, context trimming, and memory extraction into one “how the next turn survives” story | [`constants/prompts.ts`](../claudecode_src/src/constants/prompts.ts), [`utils/context.ts`](../claudecode_src/src/utils/context.ts), [`memdir/memdir.ts`](../claudecode_src/src/memdir/memdir.ts), [`services/extractMemories/extractMemories.ts`](../claudecode_src/src/services/extractMemories/extractMemories.ts) |

## How to keep walking after the bridge

1. Use the table to locate the example’s mainline step.
2. Open the matching [source-map](./source-map.en.md) section and verify the input / output pair.
3. Open only the 1 to 3 source files listed in the table before branching out.
4. After those files are stable in your head, decide whether to expand into the matching layer note or [source-navigation](./source-navigation.en.md).

## Two common stitched routes

- `l1 -> l2 -> l8 -> l7 -> l4/l5 -> l9`: read in the order a real request actually moves.
- `l3 -> l7 -> l6`: lock onto tools and permissions first, then see how controlled multi-agent work reconnects to the mainline.
