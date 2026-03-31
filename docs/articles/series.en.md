# Claude Code Article Roadmap

[中文](./series.md) | English

> This is not a loose backlog. It is the bilingual article track tied directly to the repository.

## First 6 Articles

1. `query.ts` and the Agent Loop: the heart of Claude Code
   - repo companion: `l2-agent-loop`
   - focus: `query`, `queryLoop`, `while (true)`, tool-result feedback

2. Why Claude Code uses async generators
   - repo companion: `l8-streaming`
   - focus: event flow, cancellation, `yield*` composition

3. Claude Code’s three-layer permission model
   - repo companion: `l7-permissions`
   - focus: semantic denial, rule matching, user confirmation

4. How prompt cache requirements shape Claude Code architecture
   - repo companion: `l9-context`
   - focus: dynamic boundary, snapshotting, sticky latches

5. Why Claude Code memory is an index system
   - repo companion: `l6-advanced`
   - focus: `MEMORY.md`, typed memory, on-demand loading

6. The boundary between SyntheticOutputTool and the coordinator
   - repo companion: `l6-advanced`
   - focus: structured output, worker isolation, multi-agent composition

## Second 6 Articles

7. Why QueryEngine is the session-orchestration center
   - repo companion: `l10-query-engine`
   - focus: system-prompt assembly, message staging, session orchestration

8. Claude Code API streaming is more than “typing as it goes”
   - repo companion: `l11-api-streaming`
   - focus: event model, TTFB, stall detection, watchdogs

9. Why `REPL.tsx` is an interaction-orchestration layer, not just a screen
   - repo companion: `l12-repl-ui`
   - focus: initial messages, `onSubmit` vs `onQuery`, local state boundaries

10. Why Claude Code has MCP, hooks, and plugins instead of one extension API
   - repo companion: `l13-mcp-hooks-plugins`
   - focus: capability ingress, lifecycle interception, feature packaging

11. The real boundary between memory extraction and team memory
   - repo companion: `l14-memory-system`
   - focus: typed memory, extractMemories, team-memory safety

12. Why Claude Code needs print, serve, and bridge runtime modes
   - repo companion: `l15-runtime-modes`
   - focus: entrypoints, multiple runtime surfaces, long-lived bridge sessions

## Writing Rules

- every article must link back to one layer note and one source-map node
- Chinese and English versions must share the same evidence points
- do not write generic AI-agent advice; write only what the source can support
