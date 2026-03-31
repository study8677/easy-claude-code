# Layer 10: QueryEngine And System Prompt Assembly

[中文](./l10-query-engine.md) | English

## Core Question

Why is `QueryEngine.ts` more than a wrapper around `query`? Why is it the session-level orchestration center?

## Review First

- `l1-startup`
- `l2-agent-loop`
- `l9-context`

## Read First

- `QueryEngine.ts`
- `bootstrap/state.ts`
- `constants/prompts.ts`

## Search Anchors

- `class QueryEngine`
- `before_getSystemPrompt`
- `after_getSystemPrompt`
- `system_message_yielded`
- `fetchSystemPromptParts`

## What To Notice

- how the default system prompt, append prompt, and memory mechanics prompt get assembled
- why slash-command processing, transcript persistence, and skill/plugin loading happen before the main query
- why QueryEngine acts like both a session controller and a staging area before each turn

## Source Evidence

- `QueryEngine.ts:184`: `export class QueryEngine`
- `QueryEngine.ts:284-301`: profiler checkpoints around system prompt assembly
- `QueryEngine.ts:554`: `system_message_yielded`

## What You Should Actually Learn

`query.ts` answers “how does a turn run?” `QueryEngine.ts` answers “what must be prepared before a turn can run at all?” If you want to understand how Claude Code unifies slash commands, memory, skills, plugins, and structured output under one entry path, this layer matters more than the loop itself.

## Questions To Answer

1. Why is system-prompt assembly centralized in QueryEngine instead of scattered across tools?
2. Why is transcript persistence handled before entering the main loop?
3. Where is the boundary between QueryEngine and the REPL?
