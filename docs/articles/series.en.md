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

## Writing Rules

- every article must link back to one layer note and one source-map node
- Chinese and English versions must share the same evidence points
- do not write generic AI-agent advice; write only what the source can support
