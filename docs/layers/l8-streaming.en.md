# Layer 8: Streaming And Async Generators

[中文](./l8-streaming.md) | English

## Core Question

Why does Claude Code use async generators as the core query abstraction instead of callbacks or plain async functions?

## Run First

```bash
python examples/l8_streaming.py
```

This requires `DEEPSEEK_API_KEY`.

## Read First

- `query.ts`
- `services/api/claude.ts`

## Search Anchors

- `yield`
- `yield*`
- `queryModelWithStreaming`
- `stream_request_start`

## What To Notice

- how text chunks, tool events, and results all become one event stream
- why cancellation aligns naturally with generator semantics
- why `yield*` makes nested agent composition simpler

## Demo vs Real Source

The demo keeps only the event shape and the minimum streaming loop. The real implementation also handles SDK event conversion, recovery, throughput, and UI integration.

## Questions To Answer

1. What does Promise, callback, or generator each fail to provide in this specific runtime?
2. Why is `yield*` crucial for multi-agent and nested event forwarding?
3. Where is the boundary between `services/api/claude.ts` and `query.ts`?
