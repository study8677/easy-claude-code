# Layer 14: Memory Extraction And Team Memory

[中文](./l14-memory-system.md) | English

## Core Question

Why is Claude Code memory more than `MEMORY.md`? Why does it include typed memory, extraction flows, and team memory boundaries?

## Review First

- `l6-advanced`
- `l9-context`

## Read First

- `memdir/memdir.ts`
- `services/extractMemories/extractMemories.ts`
- `services/extractMemories/prompts.ts`
- `memdir/teamMemPaths.ts`
- `memdir/teamMemPrompts.ts`

## Search Anchors

- `ENTRYPOINT_NAME`
- `buildMemoryLines`
- `Build the typed-memory`
- `extractMemories`
- `team memory`

## What To Notice

- why the memory taxonomy is closed to four types
- why writing memory content and updating the index are two explicit steps
- why team memory needs separate path handling, prompts, and escape validation

## Source Evidence

- `memdir/memdir.ts:34`: `ENTRYPOINT_NAME = 'MEMORY.md'`
- `memdir/memdir.ts:188`: typed-memory behavioral instructions
- `services/extractMemories/extractMemories.ts`: post-conversation extraction flow
- `memdir/teamMemPaths.ts`: team-memory path handling and escape checks

## What You Should Actually Learn

Claude Code memory is not a long-term chat log. It is a constrained knowledge-maintenance system: controlled writes, short indexes, typed content, and clear boundaries between personal and team memory.

## Questions To Answer

1. Why should `MEMORY.md` act as an entry index instead of content storage?
2. Why is extraction done asynchronously after the conversation instead of mutating memory every turn?
3. What extra risk controls does team memory need compared with personal memory?
