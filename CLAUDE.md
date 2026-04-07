# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

An educational resource for studying Claude Code's TypeScript source architecture. It teaches the system through a **request-flow-first** approach: trace one complete request through the system before branching into specialized topics.

The repo contains:
- **9 standalone Python examples** (`examples/l1_startup.py` through `l9_context_mgmt.py`) — pedagogical mappings, not line-by-line ports
- **Bilingual docs** (`*.md` = Chinese, `*.en.md` = English) covering 15 deep-dive layers, 4-stage learning paths, exercises, and FAQs
- **`claudecode_src/`** — a gitignored local mirror of the actual Claude Code TypeScript source (not published)

## Running Examples

No build step. All examples are standalone Python scripts:

```bash
# Most examples run without any API key
python examples/l1_startup.py

# l2 and l8 require a live model call
# Set ANTHROPIC_API_KEY or DEEPSEEK_API_KEY in .env
python examples/l2_agent_loop.py
python examples/l8_streaming.py
```

Dependencies: `pip install openai python-dotenv`

## Repository Structure

```
examples/          9 teaching layers (l1–l9), each maps to specific source files
docs/
  paths/           4-stage learning curriculum (p1–p4), each has .md and .en.md
  layers/          15 deep-dive topic docs (l1–l15), each has .md and .en.md
  superpowers/     Design specs and implementation plans
  source-navigation.*  How to search symbols in the real source
  example-source-bridge.*  Maps each example to its source file counterparts
PHILOSOPHY.MD      10 core design principles of Claude Code
agent.md           Handoff document: verified source facts, themes, constraints
```

## Content Conventions

- Every `.md` content file has an `.en.md` English counterpart — keep both in sync when editing.
- All explanations must be tied to verifiable lines/symbols in `claudecode_src/` (cited by file path and line number).
- Examples are pedagogical abstractions — they illustrate patterns, not exact implementations.
- The teaching progression is: P1 → P2 → P3 → P4 (learning paths), with examples l1–l9 as hands-on supplements.

## Core Architecture Taught Here

The central teaching spine is the **request lifecycle**:

```
User Input → Startup/Mode Routing (main.tsx + entrypoints/)
→ queryLoop (QueryEngine.ts) → query() async generator (query.ts)
→ Model streaming → Tool schema selection → Tool execution
→ Tool result reentry → State/UI update → Next turn or exit
```

Key patterns explained across examples and docs:
1. **`async function* query()`** — the agent loop is an async generator, not callbacks
2. **`yield*` delegation** — child agent events propagate transparently to parent/UI
3. **Tool = Schema + Function** — model sees JSON schema; runtime executes the function
4. **Three-layer permissions** — semantic denial → rule matching → user confirmation
5. **Prompt cache stability** — static/dynamic boundary, sticky latches protect cache hits
6. **`claudecode_src/src/bootstrap/state.ts`** — global state with explicit "DO NOT ADD MORE STATE HERE" discipline

## Authoring New Content

- When adding a new layer doc or path doc, create both `*.md` and `*.en.md` versions.
- New examples follow the `l{N}_{topic}.py` naming pattern and must include a source file map in their header comments.
- Update `docs/example-source-bridge.md` and `.en.md` when adding new examples.
- Cross-reference `agent.md` for verified source facts (line numbers, symbol names) before citing them.
