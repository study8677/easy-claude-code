# Claude Code — Deep Dive

[中文](./README.MD) | English

> A source-reading tutorial repo for Claude Code: first understand how one request moves through the system, then use examples, path pages, and the real call chain to understand the architecture.

## The one request flow to keep in mind

The first goal of this repo is not to memorize every layer, and not to read every document on day one.

Start with the path of **one Claude Code request**:

**user input → startup / mode routing → enter `query` / `queryLoop` → model output → tool call → tool execution → tool result flows back → state / UI update → next turn or exit**

Once that flow is clear, permissions, memory, runtime modes, skills, and coordinators become supporting structures instead of disconnected topics.

## What to ignore for now

On the first pass, do **not** make these your main focus yet:

- do not start by reading `claudecode_src/src/` linearly
- do not treat all of `docs/layers/` as the main course on day one
- do not dive into multi-agent flows, memory systems, runtime modes, or plugin boundaries first
- do not try to memorize every file name; first learn where the request goes next

If you can answer “which part of the request flow am I looking at right now?”, you are learning the right thing first.

## What each set of materials is for

- `examples/`: 9 runnable Python examples that turn the request flow into observable slices
- [`docs/paths/`](./docs/paths/README.en.md): the main study route; explains what to learn in P1-P4
- [`docs/example-source-bridge.en.md`](./docs/example-source-bridge.en.md): connects examples, request-flow positions, source-map sections, and real files
- [docs/source-map.en.md](./docs/source-map.en.md): traces the main call chain and its key branches
- `docs/layers/`: deep-dive notes for when one part of the flow still feels fuzzy

Supporting material:

- [PHILOSOPHY_EN.MD](./PHILOSOPHY_EN.MD): design philosophy and engineering trade-offs
- [docs/source-navigation.en.md](./docs/source-navigation.en.md): symbol-search guide
- [docs/exercises.en.md](./docs/exercises.en.md): study exercises
- [docs/faq.en.md](./docs/faq.en.md): frequently asked questions

## Where the 9 examples fit in the request flow

| Example | Request-flow position | What to notice |
|---|---|---|
| `l1_startup.py` | user input → startup / routing | how the CLI enters the correct run mode and establishes session / entry context |
| `l2_agent_loop.py` | enter `queryLoop` → one turn advances | how one request drives model work, tool use, and exit conditions |
| `l3_tool_system.py` | model output → tool call | why tools are schema plus execute instead of arbitrary JSON |
| `l4_ui_ink.py` | state / UI update | how the terminal UI reflects the current request-flow state |
| `l5_state_commands.py` | state organization / command entry | how state objects and command entrypoints support multi-turn work |
| `l6_advanced.py` | extension boundaries outside the core flow | how coordinators, cost tracking, and skills hang off the core path |
| `l7_permissions.py` | gate before tool execution | how the permission system intervenes before a tool actually runs |
| `l8_streaming.py` | how the flow is carried over time | why the core abstraction is closer to an async generator / event stream |
| `l9_context_mgmt.py` | keeping multi-turn execution alive | how context management keeps the request flow from drifting or exploding |

## Start in 5 minutes

### Track A: No API Key Required

Install the minimal dependency set:

```bash
pip install openai python-dotenv
```

Then run:

```bash
python examples/l1_startup.py
python examples/l3_tool_system.py
python examples/l7_permissions.py
```

You will see:

- `l1_startup.py`: how a request actually enters the system
- `l3_tool_system.py`: why the model does not “just do tools,” but has to go through schema plus execute
- `l7_permissions.py`: why tool execution passes through a permission gate first

Go next to:

- [Learning path: P1 First Hour](./docs/paths/p1-first-hour.en.md)

### Track B: You Have An API Key And Want To See The Core Loop First

```bash
pip install openai python-dotenv
export DEEPSEEK_API_KEY=your_key

python examples/l2_agent_loop.py
python examples/l8_streaming.py
```

You will see:

- `l2_agent_loop.py`: how one request moves through model calls, tool execution, result flow-back, and exit
- `l8_streaming.py`: why the main flow is not just one function call, but an ongoing event stream

Go next to:

- [Learning path: P2 Core Loop](./docs/paths/p2-core-loop.en.md)

## After this page, where should you go next?

- Want the staged learning route? Read [Learning Paths (English)](./docs/paths/README.en.md)
- Want to know where to go after a specific example? Read [Example-To-Source Bridge](./docs/example-source-bridge.en.md)
- Want to trace the real call chain? Read [Source Map](./docs/source-map.en.md)
- Want to search concrete symbols in the source? Read [Source Navigation Guide](./docs/source-navigation.en.md)

## What `claudecode_src/` actually is

`claudecode_src/` is a local study mirror of Claude Code source.

Important points:

- the teaching docs and Python examples can still be read independently
- the full “compare tutorial to real source” workflow assumes you have `claudecode_src/` locally
- `examples/` are pedagogical mappings, not line-by-line recreations of the real codebase
- `claudecode_src/` is gitignored and will not be published with this tutorial repo

## Go deeper

- [Layer Deep-Dive Index (English)](./docs/layers/README.en.md)
- [Layer 深挖目录（中文）](./docs/layers/README.md)
- [Design Philosophy (English)](./PHILOSOPHY_EN.MD)
- [设计哲学（中文）](./PHILOSOPHY.MD)
- [Article Roadmap (English)](./docs/articles/series.en.md)
- [文章选题路线（中文）](./docs/articles/series.md)

## Disclaimer

This repository is for personal learning and technical research only. The `claudecode_src/` directory is gitignored and will not be uploaded with this public repository. Do not use this material for commercial misuse or in ways that violate Anthropic's rights. You are responsible for your own usage.
