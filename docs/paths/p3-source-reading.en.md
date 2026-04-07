# P3: Source Reading

[中文](./p3-source-reading.md) | English

## Best For

- Readers who already understand the basic loop and are ready for the real source
- Readers who want to move from “I can run the demos” to “I can explain the implementation”

## Time

2-3 hours

## What This Stage Should Understand

This stage leaves concept-only understanding behind and reads the stabilized mainline directly:

1. how `query.ts` carries the single-turn mainline
2. why `QueryEngine.ts` is the session orchestration center instead of a redundant wrapper
3. how `services/api/claude.ts` turns provider streaming into the higher-level event stream

## Where You Are On The Mainline

**Mainline position:** mainline concept is stable → read `query.ts` → `QueryEngine.ts` → `services/api/claude.ts` directly

P2 built the intuition for how one turn moves. P3 compresses that intuition down into the real source.

You are no longer just learning that these concepts exist. You are directly reading the key files to confirm:

- where one request starts advancing
- where orchestration is centralized
- where streaming events are lifted into the upper-level flow

## Which Example To Run First

Return to the example closest to the mainline:

```bash
python examples/l2_agent_loop.py
```

If you have an API key, then add:

```bash
python examples/l8_streaming.py
```

The goal here is not new concepts. It is to re-anchor the mainline rhythm before you open the real source.

## Which Layer To Read Next

Read in this order:

1. [L10 QueryEngine And System Prompt Assembly](../layers/l10-query-engine.en.md)
2. [L11 API Streaming And The Event Model](../layers/l11-api-streaming.en.md)
3. [Source Navigation Guide](../source-navigation.en.md)
4. [Example-To-Source Bridge: l2 / l8](../example-source-bridge.en.md)

Only after the mainline source feels stable should these become second-layer additions:

- [L5 State And Commands](../layers/l5-state-commands.en.md)
- [L12 The REPL Screen And Input System](../layers/l12-repl-ui.en.md)
- [L9 Context Management](../layers/l9-context.en.md)

## Which Source Files To Open Next

Open the three-file mainline set directly:

- `claudecode_src/src/query.ts`
- `claudecode_src/src/QueryEngine.ts`
- `claudecode_src/src/services/api/claude.ts`

Only after you can explain their division of labor should UI become a second-layer addition:

- `claudecode_src/src/screens/REPL.tsx`

## What To Ignore For Now

Do not spread your attention across these boundary topics yet:

- memory extraction details
- hooks / plugins / MCP extension surfaces
- print / serve / bridge runtime modes
- coordinator / structured-output boundaries
- if the three mainline files are not stable in your head yet, do not open the fine-grained REPL state tree either

P3 exists to keep the mainline stable before you branch outward.

## Recommended Reading Order

### Pass One: two deep, one lighter

1. read `query.ts` deeply
2. read `QueryEngine.ts` deeply
3. read `services/api/claude.ts` for the main event-stream path first

### Pass Two: add UI only when needed

1. `screens/REPL.tsx`
2. `L5`
3. `L12`
4. `L9`

Do not try to swallow four core files and five deep dives all at once.

## Must-Search Symbols

- `system_message_yielded`
- `before_getSystemPrompt`
- `after_getSystemPrompt`
- `queryModelWithStreaming`
- `api_request_sent`
- `processInitialMessage`
- `DO NOT ADD MORE STATE HERE`

If you are ready to add context, then also search:

- `SYSTEM_PROMPT_DYNAMIC_BOUNDARY`

## Only Answer These Three Questions

1. Why is QueryEngine not a redundant wrapper, but the session orchestration center?
2. How does API streaming become the higher-level event stream?
3. How do `query.ts`, `QueryEngine.ts`, and `services/api/claude.ts` divide the work?

## Recommended Exercises

- [Exercise 2: why QueryEngine is not redundant](../exercises.en.md)
- [Exercise 4: streaming events](../exercises.en.md)
- if you already added REPL, then do [Exercise 5: REPL state boundary](../exercises.en.md)

## Exit Criteria

By the end of this page, you should be able to:

- explain the division of labor between `query.ts`, `QueryEngine.ts`, and `services/api/claude.ts`
- explain where system prompt assembly and event streaming each happen
- search and locate the key symbols above without help
- know clearly that permissions, memory, runtime modes, and coordinator topics belong to the next stage

If this still feels unstable, go back to:

- `P2` if loop, permissions, and streaming still do not connect cleanly
- `L10` if QueryEngine’s role is still blurry
- `L11` if the event stream still feels like only API detail

## Next Step

Continue to [P4 Advanced Architecture](./p4-advanced-architecture.en.md)
