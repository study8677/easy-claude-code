# Layer 2: The Agent Core Loop

[中文](./l2-agent-loop.md) | English

## Core Question

How does Claude Code keep cycling between model output and tool execution until the task is done?

## Run First

```bash
python examples/l2_agent_loop.py
```

This requires `DEEPSEEK_API_KEY`.

## Read First

- `query.ts`
- `QueryEngine.ts`
- `tasks/`

## Search Anchors

- `export async function* query`
- `async function* queryLoop`
- `while (true)`
- `tool_result`

## What To Notice

- who owns message history
- why tool results must be appended back into history
- what actually ends the loop
- how streamed events relate to the final answer

## Demo vs Real Source

The demo shows the minimum loop. The real source also handles streaming events, recovery, cancellation, permissions, task state, and UI event emission.

## Questions To Answer

1. Why is the agent loop closer to a state machine plus event stream than a plain `while` loop?
2. If the model returns multiple tool calls, how does Claude Code keep the context coherent?
3. What belongs in `QueryEngine` and what belongs in `query.ts`?
