# Layer 9: Context Window Management And Prompt Cache

[中文](./l9-context.md) | English

## Core Question

How does Claude Code control context budget in long conversations while protecting prompt-cache hit rate?

## Run First

```bash
python examples/l9_context_mgmt.py
```

## Read First

- `utils/context.ts`
- `constants/prompts.ts`
- `utils/api.ts`
- `memdir/memdir.ts`

## Search Anchors

- `SYSTEM_PROMPT_DYNAMIC_BOUNDARY`
- `context_1m_beta`
- `MEMORY.md`
- `ENTRYPOINT_NAME`

## What To Notice

- why the static/dynamic boundary matters
- how snapshotting and sticky latches protect cache stability
- what auto-compact solves versus what memory indexing solves

## Demo vs Real Source

The demo only illustrates token budgeting and compaction. The real source also handles model window capability, cache boundaries, system-prompt assembly, and memory injection rules.

## Questions To Answer

1. Why does prompt-cache hit rate end up shaping architecture?
2. Why must `MEMORY.md` stay short and index-like?
3. Auto-compact solves “history is too long” — what problem does memory solve?
