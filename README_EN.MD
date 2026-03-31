# Claude Code — Deep Dive

[中文](./README.MD) | English

> A source-reading tutorial repo for Claude Code: runnable examples for intuition, plus real call-chain analysis for deeper architectural understanding.

## What This Repo Is

This repo is organized around two learning paths:

- `Quick Understanding`: run examples first and build intuition for startup, the agent loop, tools, and permissions.
- `Deep Source Dive`: follow the real TypeScript call chain, key symbols, and design decisions in the source.

The repository has four layers of material:

- `examples/`: 9 runnable Python examples for intuition
- [docs/source-map.en.md](./docs/source-map.en.md): the global source call-chain map
- `docs/layers/`: bilingual deep-dive notes for each layer
- [PHILOSOPHY_EN.MD](./PHILOSOPHY_EN.MD): design philosophy and engineering trade-offs

`claudecode_src/` is for local study only and is gitignored.

## Where To Start

### Track A: Quick Understanding

1. Run `python examples/l1_startup.py`
2. Read [docs/layers/l1-startup.en.md](./docs/layers/l1-startup.en.md)
3. Continue with `l2`, `l3`, and `l7` to build intuition for the loop, tools, and permissions
4. Return to [PHILOSOPHY_EN.MD](./PHILOSOPHY_EN.MD) to understand the reasoning behind the design

### Track B: Deep Source Dive

1. Start with [docs/source-map.en.md](./docs/source-map.en.md)
2. Then read `l2 -> l8 -> l7 -> l9 -> l6`
3. Search these symbols directly in `claudecode_src/src/`:
   - `query`
   - `queryLoop`
   - `SYSTEM_PROMPT_DYNAMIC_BOUNDARY`
   - `BASH_SECURITY_CHECK_IDS`
   - `SyntheticOutputTool`

## Quick Warm-Up

```bash
pip install openai python-dotenv
export DEEPSEEK_API_KEY=your_key

python examples/l1_startup.py
python examples/l1_startup.py --print "hello"
python examples/l1_startup.py serve
```

If you do not have an API key yet, you can still learn a lot from the offline layers:

- `l1_startup.py`
- `l3_tool_system.py`
- `l4_ui_ink.py`
- `l5_state_commands.py`
- `l6_advanced.py`
- `l7_permissions.py`
- `l9_context_mgmt.py`

## 9-Layer Learning Map

| Layer | Run First | Key Source | What You Should Actually Learn |
|---|---|---|---|
| L1 Startup & Entry | `examples/l1_startup.py` | `main.tsx`, `setup.ts`, `entrypoints/` | How Claude Code boots, dispatches modes, and creates a session |
| L2 Agent Loop | `examples/l2_agent_loop.py` | `query.ts`, `QueryEngine.ts` | How tool calls drive the main loop and how the loop exits |
| L3 Tool System | `examples/l3_tool_system.py` | `Tool.ts`, `tools.ts`, `tools/*/` | Why tools are schema plus execution, not magic |
| L4 UI / Ink | `examples/l4_ui_ink.py` | `components/`, `ink.ts` | Why terminal UI can behave like React |
| L5 State & Commands | `examples/l5_state_commands.py` | `state/`, `commands/`, `history.ts` | How history, user settings, and slash commands are organized |
| L6 Advanced Mechanisms | `examples/l6_advanced.py` | `skills/`, `coordinator/`, `memdir/` | The boundaries of skills, multi-agent orchestration, memory, and cost tracking |
| L7 Permissions | `examples/l7_permissions.py` | `bashPermissions.ts`, `bashSecurity.ts` | Why Claude Code uses a 3-layer permission model |
| L8 Streaming | `examples/l8_streaming.py` | `query.ts`, `services/api/claude.ts` | Why async generators are the core streaming abstraction |
| L9 Context Management | `examples/l9_context_mgmt.py` | `utils/context.ts`, `constants/prompts.ts` | How Claude Code protects context budget and prompt cache hit rate |

See the deep-dive notes in:

- Chinese index: [`docs/layers/README.md`](./docs/layers/README.md)
- English index: [`docs/layers/README.en.md`](./docs/layers/README.en.md)

## Essential Maps And Deep Dives

- [Source Map (English)](./docs/source-map.en.md)
- [源码导图（中文）](./docs/source-map.md)
- [Design Philosophy (English)](./PHILOSOPHY_EN.MD)
- [设计哲学（中文）](./PHILOSOPHY.MD)
- [Article Roadmap (English)](./docs/articles/series.en.md)
- [文章选题路线（中文）](./docs/articles/series.md)

## Setup

```bash
pip install openai python-dotenv

# DeepSeek (recommended, compatible with l2 / l8)
export DEEPSEEK_API_KEY=your_key
export DEEPSEEK_MODEL=deepseek-chat   # optional
```

Examples that require an API key:

- `examples/l2_agent_loop.py`
- `examples/l8_streaming.py`

## How To Read This Repo Well

- If you are new: run the examples first, then read the layer notes, then search symbols in the source
- If you already build agents: start with the source map, then walk the call chains directly
- Do not read `claudecode_src/src/` linearly
- After each layer, explain to yourself what concrete engineering problem it solves

## Disclaimer

This repository is for personal learning and technical research only. The `claudecode_src/` directory is gitignored and will not be uploaded with this public repository. Do not use this material for commercial misuse or in ways that violate Anthropic's rights. You are responsible for your own usage.
