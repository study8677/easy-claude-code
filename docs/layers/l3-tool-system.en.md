# Layer 3: Tool System

[中文](./l3-tool-system.md) | English

## Core Question

How does Claude Code define tools, register them, and dispatch model tool calls into local execution?

## Run First

```bash
python examples/l3_tool_system.py
```

## Read First

- `Tool.ts`
- `tools.ts`
- `tools/BashTool/`
- `tools/FileReadTool/`

## Search Anchors

- `buildTool`
- `getTools`
- `inputSchema`
- `call`

## What To Notice

- why the model only sees schema and description
- why the implementation stays hidden from the model
- why registration and filtering live in their own layer

## Demo vs Real Source

The demo keeps only a few tools and simplified permission logic. The real repo adds richer tool context, UI components, error handling, and filtering.

## Questions To Answer

1. Why is the “schema plus function” boundary so important?
2. If you change implementation but not schema, does the model’s calling strategy change?
3. Why is a tool registry better than scattering tool logic everywhere?
