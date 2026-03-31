# Claude Code — Deep Dive

[中文](./README.MD) | English

> The most systematic guide to reading the Claude Code source — from startup entry to multi-agent coordination, with runnable examples at every layer.
>
> 📖 **Design Philosophy**: [PHILOSOPHY.MD](./PHILOSOPHY.MD) — Understand the *why* behind the code

---

## What This Is

This repo includes the Claude Code TypeScript source (`claudecode_src/`, gitignored for local study only) and a **9-layer progressive reading roadmap** plus a deep design philosophy document.

Each layer includes:
- The core question and key files
- A runnable Python example (`examples/` directory)
- Annotated source snippets

After working through the layers, read [PHILOSOPHY.MD](./PHILOSOPHY.MD) to understand the *why* behind each design decision.

```
claudecode_src/src/       ← TypeScript source (local only, not pushed)
PHILOSOPHY.MD             ← ★ Design philosophy: the "why" behind the code
examples/                 ← 9 runnable Python examples
├── l1_startup.py         ← Startup & entry
├── l2_agent_loop.py      ← Agent core loop ★
├── l3_tool_system.py     ← Tool system
├── l4_ui_ink.py          ← UI layer (with animation)
├── l5_state_commands.py  ← State & slash commands
├── l6_advanced.py        ← Skills / multi-agent / cost tracking
├── l7_permissions.py     ← 3-layer permission system
├── l8_streaming.py       ← Async generator streaming architecture
└── l9_context_mgmt.py    ← Context window management & cache optimization
v1_basic_agent.py         ← Full agent in 200 lines (recommended warm-up)
v2_async_agent.py         ← Async agent version
```

---

## Quick Warm-Up (5 minutes)

Before reading the source, run this 200-line simplified version to build intuition:

```bash
pip install openai python-dotenv
export DEEPSEEK_API_KEY=your_key

python v1_basic_agent.py
# Try: list current directory
# Try: read README_EN.MD first 20 lines
# Try: create hello.txt with "hello world"
```

After running this you'll understand 70% of Claude Code's core mechanics. The rest is in the source.

---

## 6-Layer Reading Roadmap

### Layer 1 — Startup & Entry Points
**Key files**: `main.tsx` · `entrypoints/` · `setup.ts`

**Core question**: What actually happens after you type `claude`?

Claude Code does three things before showing you the REPL:

```python
# l1_startup.py core (maps to main.tsx + setup.ts)

def startup_checkpoint(name):
    # Claude Code timestamps each startup phase to track where time is spent
    print(f"[{name}] +{elapsed_ms:.1f}ms")

def main():
    startup_checkpoint("main_entry")   # profileCheckpoint('main_tsx_entry')
    config = load_config()             # setup.ts: read config, detect API key
    session_id = setup(config)         # generate session_id, inject env vars
    startup_checkpoint("ready")

    # Mode dispatch (maps to entrypoints/ directory)
    if "--print" in sys.argv:          # claude --print "..." → run and exit
        run_non_interactive(prompt)
    elif "serve" in sys.argv:          # claude serve → HTTP server
        run_server_mode()
    else:                              # claude → interactive REPL
        run_interactive_repl()
```

> Run the example: `python examples/l1_startup.py`
> Source: `claudecode_src/src/main.tsx`, `claudecode_src/src/setup.ts`

---

### Layer 2 — Agent Core Loop ★
**Key files**: `query.ts` · `QueryEngine.ts` · `Task.ts`

**Core question**: How does Claude Code keep looping through tool calls until done?

This is the heart of all of Claude Code. Everything else is scaffolding around it:

```python
# l2_agent_loop.py core (maps to query.ts async function* queryLoop())

def query_loop(messages):
    while True:                          # ← query.ts line 307: while (true)

        response = call_model(messages)
        reply = response.choices[0].message

        if not reply.tool_calls:
            return reply.content         # model says "done" → exit loop

        # Execute tool calls, append results, continue loop
        messages.append(assistant_msg(reply))
        for tc in reply.tool_calls:
            result = run_tool(tc.function.name, tc.function.arguments)
            messages.append(tool_result(tc.id, result))
        # ↑ That's it: results go back into history, model sees them next turn
```

The real `query.ts` makes this an `async generator function*` so it can `yield` each step as an event (`stream_request_start` · `tool_use` · `tool_result` · `done`), letting the UI update in real time.

> Run the example: `python examples/l2_agent_loop.py` (requires API key)
> Source: `claudecode_src/src/query.ts` — search for `while (true)`

---

### Layer 3 — Tool System
**Key files**: `Tool.ts` · `tools.ts` · `tools/BashTool/` · `tools/FileReadTool/` · ...

**Core question**: What built-in tools does Claude Code have and how is each one implemented?

A tool = **JSON Schema (for the model) + a function (runs locally)**. That's it:

```python
# l3_tool_system.py core (maps to Tool.ts ToolDef + buildTool())

@dataclass
class ToolDef:
    name: str
    description: str
    schema: dict       # ← sent to the model (all the model ever sees)
    execute: Callable  # ← runs on your machine (model never sees this)
    needs_permission: bool = False

# Registry (maps to tools.ts getTools())
TOOL_REGISTRY = {
    "bash":       ToolDef("bash",       "Run shell command",  bash_schema,  run_bash,   needs_permission=True),
    "read_file":  ToolDef("read_file",  "Read a file",        read_schema,  read_file,  needs_permission=False),
    "write_file": ToolDef("write_file", "Write a file",       write_schema, write_file, needs_permission=True),
    "edit_file":  ToolDef("edit_file",  "Edit a file",        edit_schema,  edit_file,  needs_permission=True),
}

def dispatch(name, args):
    tool = TOOL_REGISTRY[name]
    if tool.needs_permission and not ask_permission(name, args):
        return "Permission denied by user"
    return tool.execute(args)   # ← Tool.ts call()
```

Claude Code has **30+ tools** in production. Each subdirectory in `tools/` is a complete tool implementation including UI components, permission checks, and error handling.

> Run the example: `python examples/l3_tool_system.py` (no API key needed)
> Source: `claudecode_src/src/Tool.ts`, `claudecode_src/src/tools/BashTool/BashTool.tsx`

---

### Layer 4 — UI Layer (Ink/React)
**Key files**: `components/App.tsx` · `components/AgentProgressLine.tsx` · `outputStyles/` · `ink.ts`

**Core question**: How are the spinner, progress bars, and colored output rendered in the terminal?

Claude Code uses the **Ink** framework to run a React component tree in the terminal. The core idea: `UI = f(state)` — when state changes, re-render:

```python
# l4_ui_ink.py core (simulates Ink's state-driven rendering)

@dataclass
class UIState:
    messages: list        # conversation history
    active_tool: str      # tool currently running
    spinner_frame: int    # animation frame
    cost_usd: float       # session cost

def render(state: UIState):
    """
    Pure function: same state → same terminal output.
    Ink's React reconciler diffs and updates only changed parts.
    This is why spinner animation and scrollback history coexist.
    """
    clear_screen()
    for msg in state.messages[-8:]:
        print_message(msg)                                           # MessageList.tsx
    if state.active_tool:
        print(f"{spinner(state.spinner_frame)} {state.active_tool}") # AgentProgressLine.tsx
    print(f"Cost: ${state.cost_usd:.4f}")                           # StatusBar.tsx
```

> Run the example: `python examples/l4_ui_ink.py` (no API key, shows animation)
> Source: `claudecode_src/src/components/App.tsx`, `claudecode_src/src/ink.ts`

---

### Layer 5 — State & Slash Commands
**Key files**: `state/AppStateStore.ts` · `context.ts` · `commands/` · `history.ts`

**Core question**: Where is conversation history stored? How are `/clear`, `/model` implemented?

```python
# l5_state_commands.py core

# ── 1. Immutable state (maps to AppStateStore.ts) ─────────
@dataclass(frozen=True)   # frozen = cannot mutate directly
class AppState:
    messages: tuple = ()   # tuple (immutable) — replace the whole thing to update
    model: str = "deepseek-chat"
    cost_usd: float = 0.0

store = AppStateStore(AppState(), on_change=save_to_disk)
store.set(lambda s: replace(s, model="claude-sonnet-4-6"))  # only legal update path

# ── 2. Slash commands (maps to commands/ directory) ────────
# /clear /model /cost /help all share the same structure, registered in a dict
@dataclass
class SlashCommand:
    name: str
    description: str
    execute: Callable   # (store, args) -> str | None

COMMANDS = {
    "clear":   SlashCommand("clear",   "Clear history",     cmd_clear),
    "model":   SlashCommand("model",   "Switch model",      cmd_model),
    "compact": SlashCommand("compact", "Compress history",  cmd_compact),
}
```

**The secret of multi-turn memory**: message history only ever grows — nothing is deleted (except on `/clear`). Every API call passes the full history in — that's how the model "remembers" what was said.

> Run the example: `python examples/l5_state_commands.py` (no API key, interactive)
> Source: `claudecode_src/src/state/AppStateStore.ts`, `claudecode_src/src/commands/`

---

### Layer 6 — Advanced Mechanisms
**Key files**: `skills/` · `coordinator/coordinatorMode.ts` · `cost-tracker.ts` · `buddy/` · `memdir/`

The first 5 layers cover Claude Code's skeleton. This layer is the flesh.

**Skills system**: a `.md` file is a skill, compiled into a slash command at startup
```markdown
---
name: run-tests
description: Run tests and show failures
allowed_tools: [bash]
---
Run `pytest -x --tb=short`, show failures, suggest fixes.
```

**Multi-agent coordination**: coordinator splits big tasks across parallel workers
```
coordinator Claude
  ├── AgentTool → worker 1 (restricted toolset) → SyntheticOutputTool
  ├── AgentTool → worker 2 (restricted toolset) → SyntheticOutputTool
  └── collect results, produce final answer
```

**Cost tracking**: token usage accumulates per API call, displayed live in the status bar
```python
tracker.record(input_tokens=1500, output_tokens=300)
print(f"${tracker.total_cost_usd():.6f}")   # precise to the micro-dollar
```

> Run the example: `python examples/l6_advanced.py` (no API key needed)
> Source: `claudecode_src/src/skills/`, `claudecode_src/src/coordinator/`, `claudecode_src/src/cost-tracker.ts`

---

## Source Directory Quick Reference

```
claudecode_src/src/
├── main.tsx              ← L1  CLI entry point
├── entrypoints/          ← L1  interactive / non-interactive / server modes
├── setup.ts              ← L1  environment initialization
│
├── query.ts              ← L2  ★ Agent Loop (while(true) lives here)
├── QueryEngine.ts        ← L2  multi-turn loop engine
├── Task.ts / tasks/      ← L2  task state machine
│
├── Tool.ts               ← L3  tool interface definition
├── tools.ts              ← L3  tool registry
├── tools/                ← L3  30+ tool implementations
│   ├── BashTool/         ← L3  maps to l3 example bash tool
│   ├── FileReadTool/     ← L3  maps to l3 example read_file
│   ├── FileEditTool/     ← L3  maps to l3 example edit_file
│   ├── AgentTool/        ← L6  sub-agent (most complex)
│   └── MCPTool/          ← ext MCP protocol tools
│
├── ink.ts                ← L4  Ink framework entry
├── components/           ← L4  React components (App.tsx, progress lines, etc.)
├── screens/              ← L4  screens (onboarding, main UI)
├── outputStyles/         ← L4  syntax highlighting, Markdown rendering
│
├── state/                ← L5  AppStateStore (Redux-like)
├── context.ts            ← L5  message history
├── history.ts            ← L5  persistence
├── commands/             ← L5  slash command implementations
│
├── skills/               ← L6  skills system
├── coordinator/          ← L6  multi-agent coordination
├── cost-tracker.ts       ← L6  token cost accounting
├── memdir/               ← L6  persistent memory (/memory command)
├── buddy/                ← L6  buddy pair-programming mode
└── server/               ← L6  HTTP server mode
```

---

## How to Read

1. **Run** `v1_basic_agent.py` first — build intuition for the agent loop
2. **Work through** examples in order (`l1_` → `l6_`), each runs standalone
3. **Cross-reference** the comments in each example to find the corresponding source
4. **Read with questions** — don't read the TypeScript source linearly
5. Each example file's docstring lists exactly which source files it maps to

---

## Setup

```bash
pip install openai python-dotenv

# DeepSeek (recommended — generous free tier, compatible with v1/v2/l2)
export DEEPSEEK_API_KEY=your_key
export DEEPSEEK_MODEL=deepseek-chat   # optional

# Or Anthropic Claude (edit base_url and model in examples)
export ANTHROPIC_API_KEY=your_key
```

---

## Disclaimer

This repository is for personal learning and technical research only. The source code in `claudecode_src/` is listed in `.gitignore` and will not be pushed to any public platform. Do not use it for commercial purposes or in ways that infringe upon Anthropic's rights. All responsibility rests with the user.
