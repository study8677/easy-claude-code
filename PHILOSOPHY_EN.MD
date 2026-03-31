# Claude Code Design Philosophy: The Thinking Behind The Source

[中文](./PHILOSOPHY.MD) | English

> Reading a line of code is easy. Understanding why it was written that way is the real lesson.

This document mirrors the Chinese philosophy guide and keeps the same evidence points so English readers can follow the same learning path.

## Contents

1. [Reversibility First](#1-reversibility-first)
2. [Generator As The Core Abstraction](#2-generator-as-the-core-abstraction)
3. [A Three-Layer Permission Model](#3-a-three-layer-permission-model)
4. [Errors Do Not Need To Surface Immediately](#4-errors-do-not-need-to-surface-immediately)
5. [Cache Stability Is A First-Class Concern](#5-cache-stability-is-a-first-class-concern)
6. [Memory Is An Index, Not A Dump](#6-memory-is-an-index-not-a-dump)
7. [The Coordinator Never Peeks](#7-the-coordinator-never-peeks)
8. [Global State Must Stay Small](#8-global-state-must-stay-small)
9. [A Tool Is Schema Plus Function](#9-a-tool-is-schema-plus-function)
10. [Numeric IDs Beat String Labels](#10-numeric-ids-beat-string-labels)

## 1. Reversibility First

**Source evidence**: system prompt guidance in `constants/prompts.ts`

Claude Code optimizes for operations that are safe to undo. The more destructive or wide-reaching an action is, the more likely the agent should pause and confirm first.

This is not just a UX choice. It is an architecture choice:

- local, reversible actions can often proceed
- shared or hard-to-undo actions should stop for confirmation
- the cost of one missed confirmation is much higher than the cost of one extra confirmation

When you build your own agent, this principle should outrank feature completeness.

## 2. Generator As The Core Abstraction

**Source evidence**: `query.ts` exports `query()` and defines `queryLoop()`

Claude Code uses async generators because they solve three problems at once:

- streaming output
- cancellation
- composition through `yield*`

This is why nested agent flows can forward events all the way to the UI without inventing a second event bus. The design is less about syntax and more about keeping the runtime model simple.

## 3. A Three-Layer Permission Model

**Source evidence**: `tools/BashTool/bashPermissions.ts`, `tools/BashTool/bashSecurity.ts`

Command execution is guarded by three different layers:

1. semantic safety checks
2. allow/deny rule matching
3. an explicit user confirmation fallback

This layering matters because it separates:

- obviously dangerous commands
- repeatable user policy
- everything ambiguous

The result is safer than “always ask” and less annoying than “ask for everything.”

## 4. Errors Do Not Need To Surface Immediately

**Source evidence**: `query.ts`, especially `isWithheldMaxOutputTokens()`

Some errors are temporarily withheld so the runtime can attempt recovery before exposing failure to the outside world.

The key insight is operational:

- if a transient failure can be recovered internally, surfacing it too early may cause upstream callers to abort the whole session
- recovery first, reporting second, often produces a more stable system

This is one of the most instructive patterns in the codebase because it is counterintuitive but pragmatic.

## 5. Cache Stability Is A First-Class Concern

**Source evidence**: `constants/prompts.ts`, `QueryEngine.ts`, context utilities

Claude Code is designed around prompt-cache friendliness:

- a static/dynamic boundary keeps the stable prefix identical
- important session settings are snapshotted once
- sticky latches avoid changing cache-breaking headers mid-session

The lesson is larger than Claude Code itself: once prompt caching matters economically, architecture starts to bend around cache stability.

## 6. Memory Is An Index, Not A Dump

**Source evidence**: `memdir/memdir.ts`, memory prompts, `MEMORY.md`

Persistent memory is intentionally split into:

- a tiny index file that is always loaded
- content files that are loaded only when relevant

This keeps memory lightweight, searchable, and less likely to rot. Claude Code stores what cannot be cheaply rediscovered elsewhere, not everything that happened.

## 7. The Coordinator Never Peeks

**Source evidence**: `coordinator/coordinatorMode.ts`, `AgentTool`, `SyntheticOutputTool`

In coordinator mode, the parent agent does not inspect a worker’s internal state. It waits for a structured output boundary instead.

That preserves:

- isolation
- replaceability
- simpler orchestration logic

The analogy to processes is useful: good boundaries matter more than raw visibility.

## 8. Global State Must Stay Small

**Source evidence**: `bootstrap/state.ts`

The file literally says:

```ts
// DO NOT ADD MORE STATE HERE - BE JUDICIOUS WITH GLOBAL STATE
```

That comment expresses a discipline, not just a style preference. Claude Code keeps message history, UI state, and tool-use context out of the global singleton on purpose. The payoff is easier reasoning and lower coupling.

## 9. A Tool Is Schema Plus Function

**Source evidence**: `Tool.ts`, `tools/*/`

The model sees the schema and description. The runtime owns the implementation. Keeping those separate has three benefits:

- the model never sees local implementation details
- implementations can change without retraining the model’s mental contract
- descriptions become part of the API surface for tool quality

This is one of the cleanest design ideas in the project and worth copying directly.

## 10. Numeric IDs Beat String Labels

**Source evidence**: `tools/BashTool/bashSecurity.ts`, `BASH_SECURITY_CHECK_IDS`

Security checks use numeric IDs instead of verbose strings. That improves:

- telemetry efficiency
- privacy and log hygiene
- long-term stability across renames

It is a small detail with a very strong engineering smell: the code was written by people who expect the system to operate at scale.

## Closing View

Claude Code repeatedly makes the same kinds of decisions:

- optimize for reversibility
- prefer recovery over noisy failure
- keep boundaries explicit
- treat cache hit rate as architecture
- make abstractions compose cleanly

Those are the real lessons in the source. The syntax is secondary.

For guided reading, continue with:

- [源码导图（中文）](./docs/source-map.md)
- [Source Map (English)](./docs/source-map.en.md)
- `docs/layers/` for per-layer deep dives
