# Layer 11: API Streaming And The Event Model

[中文](./l11-api-streaming.md) | English

## Core Question

How does Claude Code transform the raw API stream into a unified runtime event model?

## Review First

- `l2-agent-loop`
- `l8-streaming`

## Read First

- `services/api/claude.ts`
- `query.ts`

## Search Anchors

- `queryModelWithStreaming`
- `api_request_sent`
- `first_chunk`
- `stream_request_start`
- `message_start`

## What To Notice

- how request-sent, headers-received, and first-chunk timings are measured
- why `query.ts` emits `stream_request_start` before the stream is consumed
- why watchdogs, stall detection, and fallback timeouts live close to the API layer

## Source Evidence

- `services/api/claude.ts:752`: `export async function* queryModelWithStreaming`
- `services/api/claude.ts:1805-1807`: `api_request_sent`
- `services/api/claude.ts:1971-1973`: `first_chunk`
- `query.ts:337`: `stream_request_start`

## What You Should Actually Learn

Claude Code streaming is not just text chunking. It is a runtime model that unifies network state, event boundaries, recovery behavior, and latency measurement into one consumable stream. The lesson here is not “how to use the Anthropic SDK,” but how to define event semantics cleanly.

## Questions To Answer

1. Why does `services/api/claude.ts` care about stalls and idle timeouts?
2. What is the most important contract between `query.ts` and the API layer?
3. If the underlying stream dies, why is a generic exception not enough?
