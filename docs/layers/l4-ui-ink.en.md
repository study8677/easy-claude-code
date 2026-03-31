# Layer 4: UI Layer (Ink / React)

[中文](./l4-ui-ink.md) | English

## Core Question

Why can Claude Code render spinners, status bars, and message history in the terminal like a React app?

## Run First

```bash
python examples/l4_ui_ink.py
```

## Read First

- `components/`
- `screens/REPL.tsx`
- `ink.ts`
- `ink/`

## Search Anchors

- `REPL`
- `App`
- `AgentProgressLine`
- `render`

## What To Notice

- how UI state differs from message state
- why declarative rendering still works in a terminal
- why spinner and tool progress do not break scrollback history

## Demo vs Real Source

The demo simulates React/Ink with full redraws. The real implementation has finer component boundaries, input handling, and terminal compatibility details.

## Questions To Answer

1. Why is Claude Code not just a series of `print()` calls?
2. What would go wrong if progress updates were not state-driven?
3. Is `REPL.tsx` more of a product layer while `ink/` is more of a rendering layer?
