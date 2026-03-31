# Layer 5: State Management And Slash Commands

[中文](./l5-state-commands.md) | English

## Core Question

How does Claude Code organize and update conversation history, user settings, and command behavior?

## Run First

```bash
python examples/l5_state_commands.py
```

## Read First

- `state/`
- `commands/`
- `history.ts`
- `context.ts`

## Search Anchors

- `AppStateStore`
- `setState`
- `compact`
- `history`

## What To Notice

- which state needs immutable updates
- why slash commands look like a command registry instead of special syntax
- how history, UI state, and QueryEngine-local state are separated

## Demo vs Real Source

The demo keeps the store and command shape. The real implementation has many more fields, longer lifetimes, and stricter persistence/effect boundaries.

## Questions To Answer

1. Why should message history not simply live inside a global singleton?
2. Is `/compact` more like a tool, a UI event, or a state transition?
3. What kinds of state should persist across sessions, and what kinds should not?
