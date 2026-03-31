# Layer 6: Advanced Mechanisms

[中文](./l6-advanced.md) | English

## Core Question

How does Claude Code grow beyond the main loop into product-layer systems like skills, multi-agent work, memory, and cost tracking?

## Run First

```bash
python examples/l6_advanced.py
```

## Read First

- `skills/`
- `coordinator/`
- `tools/AgentTool/`
- `tools/SyntheticOutputTool/`
- `memdir/`
- `cost-tracker.ts`

## Search Anchors

- `SYNTHETIC_OUTPUT_TOOL_NAME`
- `createSyntheticOutputTool`
- `MEMORY.md`
- `cost`

## What To Notice

- which capabilities are really “prompt reuse as a product feature”
- how structured output locks the boundary around multi-agent work
- why memory behaves like an index instead of a growing log dump

## Demo vs Real Source

The demo compresses several advanced mechanisms into one file. The real source keeps them decoupled and lets the session orchestration compose them.

## Questions To Answer

1. What are the boundaries between skills, tools, and commands?
2. Why should the coordinator not inspect worker intermediate state?
3. Why is memory closer to a directory index than a long-term chat transcript?
