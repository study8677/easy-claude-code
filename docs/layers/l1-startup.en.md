# Layer 1: Startup And Entry Points

[中文](./l1-startup.md) | English

## Core Question

What happens after a user types `claude`, and how does Claude Code decide which mode to enter?

## Run First

```bash
python examples/l1_startup.py
python examples/l1_startup.py --print "hello"
python examples/l1_startup.py serve
```

## Read First

- `main.tsx`
- `setup.ts`
- `entrypoints/`
- `QueryEngine.ts`

## Search Anchors

- `main_entry`
- `setup`
- `runHeadless`
- `serve`

## What To Notice

- why startup uses checkpoints
- where config, session, and environment are initialized
- why mode dispatch happens before the main agent loop starts

## Demo vs Real Source

The demo keeps only the startup skeleton. The real source also wires global config, model capabilities, tool assembly, and structured output setup.

## Questions To Answer

1. Where does the startup path connect to the actual query path?
2. Why are REPL, print, and serve separate entrypoints instead of branches inside one giant function?
3. If you added a new mode, where would it most likely be introduced?
