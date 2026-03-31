# Layer 15: Print, Serve, Bridge, And Other Runtime Modes

[中文](./l15-runtime-modes.md) | English

## Core Question

Why is Claude Code not just an interactive REPL? Why does it also support print mode, MCP serve, direct connect, bridge, and other runtime surfaces?

## Review First

- `l1-startup`
- `l12-repl-ui`

## Read First

- `main.tsx`
- `cli/print.ts`
- `replLauncher.tsx`
- `setup.ts`
- `bridge/bridgeMain.ts`

## Search Anchors

- `runHeadless`
- `launchRepl`
- `mcp serve`
- `CLAUDE_CODE_ENTRYPOINT`
- `bridgeMain`

## What To Notice

- how one core system is wrapped into multiple entry surfaces
- why some capabilities make more sense in REPL while others fit headless/print
- why bridge behaves more like a long-lived session service than a one-shot CLI command

## Source Evidence

- `main.tsx`: entry detection for `--print`, `mcp serve`, connect/ssh/assistant, and other early argv rewrites
- `replLauncher.tsx`: interactive REPL launch wrapper
- `setup.ts:86-92`: messaging server and bare/simple mode differences
- `bridge/bridgeMain.ts:1980`: `export async function bridgeMain`

## What You Should Actually Learn

Claude Code’s core behavior is not bound to the REPL. It is consumed by multiple runtime surfaces. Once you understand this, it becomes clearer why so much initialization logic lives in `main.tsx` and `setup.ts` instead of being hardcoded into the REPL screen.

## Questions To Answer

1. Why is `--print` not just a quiet version of the REPL?
2. What is fundamentally different about a long-lived mode like `bridgeMain` versus a normal one-shot CLI run?
3. If you added a new runtime entrypoint, which files would you expect to change first?
