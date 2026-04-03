# Claude Code Learning Paths

[中文](./README.md) | English

> If `docs/layers/` is the reference shelf, these path pages are the course index organized around the one-request lifecycle. The goal is not to finish every doc, but to make that request flow clear in stages.

## First, remember what these path pages are for

These four stages are not a generic course list. They split the same request flow into four slices:

**user input → startup / mode routing → `queryLoop` one-turn progression → model / tools / result flow-back → state / UI update → next turn or exit**

Each time, you only need to answer one question: **which slice of the request flow am I in, and what do I need to understand now?**

## What not to read yet

While following the path pages, do **not**:

- treat `docs/layers/` as a mandatory cover-to-cover course
- dive into memory, runtime modes, multi-agent flows, or plugins first
- switch into “full repository tour mode” just because you saw many file names
- start linear reading of `claudecode_src/src/` before P1 / P2 feel stable

When a page says “ignore this for now,” that is there to protect your sense of the request flow.

## How the four stages map onto the lifecycle

| Stage | Request-flow position | Only understand this in the current stage |
|---|---|---|
| [P1 First Hour](./p1-first-hour.en.md) | user input → startup / routing | how the request actually enters the system |
| [P2 Core Loop](./p2-core-loop.en.md) | `queryLoop` one-turn core flow | how model work, tool use, and result flow-back connect |
| [P3 Source Reading](./p3-source-reading.en.md) | direct reading of the core source path | the key files and key symbols on the core path |
| [P4 Advanced Architecture](./p4-advanced-architecture.en.md) | boundaries outside the core flow | how permissions, memory, and runtime modes surround the core path |

## How the examples map onto the request flow and stages

| Stage | Request-flow slice | Start with these examples | What these examples show |
|---|---|---|---|
| P1 | input → startup / routing | `l1_startup.py`, `l4_ui_ink.py` | how the request enters the system, and how the UI exposes early-state transitions |
| P2 | `queryLoop` → model / tools / flow-back | `l2_agent_loop.py`, `l3_tool_system.py`, `l7_permissions.py`, `l8_streaming.py` | how one turn advances, how tools are called, how permissions intervene, and how streaming carries the full path |
| P3 | direct reading of the core source path | `l5_state_commands.py`, `l9_context_mgmt.py` | how state and context support multi-turn execution and source tracing |
| P4 | extension boundaries outside the core flow | `l6_advanced.py` | how coordinators, cost tracking, skills, and runtime boundaries hang off the core path |

## How to use these paths

1. Start from `P1` unless you are already comfortable with agent frameworks and Claude Code call chains.
2. Finish one stage at a time instead of opening five deep-dive notes in parallel.
3. In each stage, run the example first, then read the path page, then use the layer note and source-map to steady the request flow.
4. If you get lost in the source, open the [Source Navigation Guide](../source-navigation.en.md) immediately.
5. At each stage, confirm why you are reading that page before you branch into extra material.

## Recommended order

### If you are new

Go in order:

`P1 -> P2 -> P3 -> P4`

### If you already build agents

Start from:

- `P2` if you mainly want Claude Code’s loop / permission / streaming design
- `P3` if you are ready to read the core source directly

## A standard study sequence

Try to use this sequence in every stage:

`run example -> read path page -> read matching layer -> open source-map -> search symbols -> open source files`

If you do not want to assemble that chain yourself, open:

- [Example-To-Source Bridge](../example-source-bridge.en.md)

## When to stop and review

Each stage only asks you to answer the current page’s questions.

If you can already:

- explain which slice of the request flow this stage covers
- explain why that slice matters
- locate the matching symbols
- explain what engineering problem this layer solves

then continue.

If not, do not rush into the next page yet.

## Read alongside

- [Example-To-Source Bridge](../example-source-bridge.en.md)
- [Source Map](../source-map.en.md)
- [Layer Deep-Dive Index](../layers/README.en.md)
- [Study Exercises](../exercises.en.md)
- [Design Philosophy](../../PHILOSOPHY_EN.MD)
