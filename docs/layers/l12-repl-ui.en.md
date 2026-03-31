# Layer 12: The REPL Screen And Input System

[中文](./l12-repl-ui.md) | English

## Core Question

What role does a huge entry component like `REPL.tsx` actually play inside Claude Code?

## Review First

- `l4-ui-ink`
- `l5-state-commands`

## Read First

- `screens/REPL.tsx`
- `replLauncher.tsx`
- `components/PromptInput/*`

## Search Anchors

- `export function REPL`
- `processInitialMessage`
- `pendingInitialQuery`
- `onSubmit`

## What To Notice

- why REPL is both a screen controller and an interaction bus
- how initial messages, plan-mode exit messages, and hook-driven messages enter the session
- why user input does not always become a query immediately and may pass through command, hook, history, or buffer handling first

## Source Evidence

- `screens/REPL.tsx:572`: `export function REPL`
- `screens/REPL.tsx:3035`: `processInitialMessage`
- `screens/REPL.tsx:3140`: invocation of `processInitialMessage`

## What You Should Actually Learn

Do not think of the REPL as “just UI.” In Claude Code it is also an interaction-orchestration layer: it receives user input, processes initial messages, coordinates hooks, manages local UI state, and decides when something should actually be sent into QueryEngine.

## Questions To Answer

1. Why are `onSubmit` and `onQuery` not the same concept?
2. What kind of non-immediate-input cases does `processInitialMessage` solve?
3. Why is it acceptable for REPL to own a lot of local state instead of forcing everything into global state?
