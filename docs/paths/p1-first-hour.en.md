# P1: First Hour

[中文](./p1-first-hour.md) | English

## Best For

- Readers entering this repo for the first time
- Readers who do not yet understand Claude Code startup flow
- Readers without an API key

## Time

60-90 minutes

## What This Stage Should Understand

This stage narrows the work to the three things that happen before a request really enters the main loop:

1. how Claude Code decides which runtime mode to enter
2. what `setup` finishes before the loop begins
3. why this is the wrong moment to dive into tools, streaming, or memory

## Where You Are On The Mainline

**Mainline position:** user input → startup / mode routing

This page does not ask you to trace the whole request lifecycle yet. It asks you to stabilize the entry:

- CLI arguments, working directory, and run mode decide which surface to enter
- `setup` prepares the baseline environment for later execution
- only after those steps are stable does `query` / `queryLoop` get a trustworthy entry point

If you dive into tool execution or UI streaming here, the cognitive load jumps too early.

## Which Example To Run First

Run `l1_startup.py` until it feels obvious:

```bash
python examples/l1_startup.py
python examples/l1_startup.py --print "hello"
python examples/l1_startup.py serve
```

If you want proof that later layers exist, do a light preview only:

```bash
python examples/l3_tool_system.py
python examples/l4_ui_ink.py
```

Those previews are not obligations in this stage. They only show that more layers come later.

## Which Layer To Read Next

Read in this order:

1. [L1 Startup And Entry Points](../layers/l1-startup.en.md)
2. [Source Map: startup path](../source-map.en.md#1-startup-path)
3. [Example-To-Source Bridge: l1](../example-source-bridge.en.md)

If you only want a preview of later stages, skim:

- [L3 Tool System](../layers/l3-tool-system.en.md)
- [L4 UI / Ink](../layers/l4-ui-ink.en.md)

## Which Source Files To Open Next

Keep this stage tight and open only the two files closest to the entry:

- `claudecode_src/src/main.tsx` — where CLI arguments and mode routing choose a runtime surface
- `claudecode_src/src/setup.ts` — where initialization finishes before the loop begins

If you encounter `runHeadless`, `serve`, or `REPL` while searching, treat them as routing outcomes first instead of expanding into every later implementation.

## What To Ignore For Now

Deliberately ignore these topics for now:

- the full tool registration and execution machinery
- the full single-turn `query` / `queryLoop` path
- streaming implementation details
- memory, prompt cache, and multi-agent
- fine-grained REPL state organization

This page should reduce cognitive load. Build the “how the request enters the system” spine first.

## Must-Search Symbols

In this stage, search these four first:

- `main_entry`
- `setup`
- `runHeadless`
- `serve`

If you still have bandwidth, then add:

- `buildTool`
- `REPL`

## Only Answer These Three Questions

1. Where does Claude Code decide between REPL, print, serve, and other runtime surfaces?
2. Why must mode dispatch happen before the agent loop really begins?
3. Why should setup-style initialization not be scattered later in the execution chain?

## How To Bridge Into The Real Source

Use this sequence:

1. open [source-map: startup path](../source-map.en.md#1-startup-path)
2. use [source-navigation](../source-navigation.en.md) to search `main_entry` and `setup`
3. open `main.tsx` and `setup.ts` first

If you want a tighter handoff, open:

- [Example-To-Source Bridge](../example-source-bridge.en.md)

## Exit Criteria

By the end of this page, you should be able to:

- explain what startup, initialization, and mode dispatch each own
- locate the key symbols above in the source
- explain in your own words why Claude Code is not a single giant script
- know clearly that this is still not the moment to dive into tools, streaming, or memory

If you cannot, go back to:

- `L1` if REPL, print, and serve are still blurred together
- the startup section in `source-map` if the call chain still feels unstable

## No API Key?

This whole stage is designed to work offline.

## Next Step

Continue to [P2 Core Loop](./p2-core-loop.en.md)
