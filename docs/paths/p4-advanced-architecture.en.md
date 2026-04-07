# P4: Advanced Architecture

[中文](./p4-advanced-architecture.md) | English

## Best For

- Readers who can already navigate the core files and now want architectural boundaries
- Readers who want a system-level understanding of permissions, memory, runtime modes, coordinator, and extension topics

## Time

2-3 hours

## What This Stage Should Understand

Only after the mainline is stable should this stage open the boundary topics. You only need to clarify four surrounding layers now:

1. how permissions protect the mainline before and after tool execution
2. how memory and context support the mainline over longer horizons
3. how runtime modes branch beyond the REPL into print, serve, and bridge
4. how coordinator, structured output, and extension surfaces attach around the mainline

## Where You Are On The Mainline

**Mainline position:** mainline is stable → branch outward into permissions, memory, runtime modes, coordinator, and related boundaries

P4 does not reteach the single-turn loop. It assumes you can already explain the request lifecycle from P1-P3.

Only after the mainline is secure does it make sense to study these outer boundaries:

- which mechanisms sit directly around the mainline, like permissions
- which mechanisms maintain longer-lived capability outside the turn, like memory
- which mechanisms branch the system into different runtime surfaces, like print, serve, and bridge
- which mechanisms coordinate higher-level behavior, like coordinator and structured output

## Which Example To Run First

Start with the example closest to the mainline boundary:

```bash
python examples/l7_permissions.py
```

Once that feels stable, add topic branches as needed:

```bash
python examples/l6_advanced.py
python examples/l1_startup.py serve
python examples/l1_startup.py --print "hello"
```

The rule here is not “run every example.” It is “revisit the mainline through the boundary you are studying.”

## Which Layer To Read Next

Start with the boundary closest to the mainline, then move outward:

1. [L7 Permissions](../layers/l7-permissions.en.md)
2. [L14 Memory Extraction And Team Memory](../layers/l14-memory-system.en.md)
3. [L15 Print, Serve, Bridge, And Other Runtime Modes](../layers/l15-runtime-modes.en.md)
4. [L6 Advanced Mechanisms](../layers/l6-advanced.en.md)
5. [L13 MCP, Hooks, And Plugins](../layers/l13-mcp-hooks-plugins.en.md)
6. [Design Philosophy](../../PHILOSOPHY_EN.MD)

## Which Source Files To Open Next

Open files by boundary theme:

- permissions: `claudecode_src/src/tools/BashTool/bashPermissions.ts`, `claudecode_src/src/tools/BashTool/bashSecurity.ts`
- memory: `claudecode_src/src/services/extractMemories/extractMemories.ts`, `claudecode_src/src/memdir/memdir.ts`
- runtime / coordinator: `claudecode_src/src/coordinator/coordinatorMode.ts`, `claudecode_src/src/bridge/bridgeMain.ts`, `claudecode_src/src/tools/SyntheticOutputTool/SyntheticOutputTool.ts`
- extensions: `claudecode_src/src/utils/hooks/execAgentHook.ts`, `claudecode_src/src/plugins/builtinPlugins.ts`

## What To Ignore For Now

To keep this boundary reading controlled, do not do these things:

- do not jump into P4 if the mainline is not stable yet
- do not trace every plugin, hook, or MCP detail in one pass
- do not execute every memory extraction path end-to-end
- do not read all multi-agent code at once; lock in the coordinator / structured-output boundary first
- if `query.ts`, `QueryEngine.ts`, and `services/api/claude.ts` are still blurry, go back to P3 first

P4 is meant to create boundary sense outside the mainline, not a new flood of information.

## Recommended Reading Mode

### If You Want To Understand “How The System Extends”

Read in this order:

1. `L13`
2. `L6`
3. search `execAgentHook`, `builtinPlugins`, and `ENTRYPOINT_NAME`

### If You Want To Understand “How Long-Lived Context Surrounds The Mainline”

Read in this order:

1. `L14`
2. search `buildMemoryLines` and `extractMemories`
3. then return to how `QueryEngine` consumes context results

### If You Want To Understand “Why It Is Not Just A REPL”

Read in this order:

1. `L15`
2. `L6`
3. search `bridgeMain` and `SYNTHETIC_OUTPUT_TOOL_NAME`

## Must-Search Symbols

- `SYNTHETIC_OUTPUT_TOOL_NAME`
- `execAgentHook`
- `builtinPlugins`
- `ENTRYPOINT_NAME`
- `buildMemoryLines`
- `extractMemories`
- `bridgeMain`

## Only Answer These Three Questions

1. Why does Claude Code keep multiple extension surfaces instead of one universal plugin system?
2. What is the real boundary between memory extraction and context management?
3. Why does Claude Code need print, serve, and bridge in addition to the REPL?

## Recommended Exercises

- [Exercise 6: prompt cache and memory](../exercises.en.md)
- [Exercise 7: REPL vs non-REPL runtime modes](../exercises.en.md)

## Synthesis Task

Write your own architecture summary and cover at least three of these four ideas:

- `extension surfaces`
- `memory index`
- `runtime modes`
- `structured output boundary`

Rules:

- do not only list features
- every conclusion should trace back to concrete source symbols

## Exit Criteria

By the end of this page, you should be able to:

- explain Claude Code’s major architectural boundaries in your own words
- point to the files that carry permissions, memory, runtime modes, and extension surfaces
- explain why “many features” and “clear architecture” are not the same thing
- know clearly that all of this depends on the P1-P3 mainline already being stable

If you cannot, go back to:

- `P3` if the three mainline files are still unstable
- `L6` if multi-agent and structured-output boundaries are still fuzzy
- `L14` if memory still feels like “put more text into the prompt”
- `L15` if Claude Code still feels like only a REPL tool

## After This

At this point, go back to:

- [Layer Deep-Dive Index](../layers/README.en.md)
- [Article Roadmap](../articles/series.en.md)

You should now be able to choose the next source area to study on your own.
