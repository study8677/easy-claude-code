# Layer 7: The Three-Layer Permission System

[中文](./l7-permissions.md) | English

## Core Question

Why does Claude Code split command permission into semantic checks, rule matching, and explicit user confirmation?

## Run First

```bash
python examples/l7_permissions.py
```

## Read First

- `tools/BashTool/bashPermissions.ts`
- `tools/BashTool/bashSecurity.ts`

## Search Anchors

- `BASH_SECURITY_CHECK_IDS`
- `canUseTool`
- `zmodload`
- `OBFUSCATED_FLAGS`

## What To Notice

- which commands are denied immediately and why they do not need a prompt
- why user rules happen after semantic safety checks
- why numeric IDs are better than string labels for telemetry and privacy

## Demo vs Real Source

The demo implements only representative checks. The real source has more detectors, more edge-case handling, and stricter shell-semantics alignment.

## Questions To Answer

1. Why is “just ask the user every time” not a good permission system?
2. Why are dangerous ZSH modules blocked even if the current shell is not ZSH?
3. What kind of problem is each of the three layers trying to stop?
