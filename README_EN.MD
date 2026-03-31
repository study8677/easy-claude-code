# easy_claude_code — Claude Code Source Code Study Roadmap

English Version | [中文版](./README.MD)

> The Claude Code source code has been leaked. This repo archives it and provides a systematic reading roadmap to help you truly understand how it works.

---

## About the Source Code

The TypeScript source code of Claude Code leaked recently. This repository includes it under the `claudecode_src/` directory. **It is listed in `.gitignore` and will NOT be pushed to GitHub — for local study only.**

```
claudecode_src/
├── src/          # TypeScript / React source code (core)
└── vendor/       # Native module sources (audio, image, URL handling, etc.)
```

---

## Contents

- [How to Start](#how-to-start)
- [Layer 1: Startup & Entry Points](#layer-1-startup--entry-points)
- [Layer 2: Agent Core Loop](#layer-2-agent-core-loop)
- [Layer 3: Tool System](#layer-3-tool-system)
- [Layer 4: UI Layer — Ink/React](#layer-4-ui-layer--inkreact)
- [Layer 5: State & Commands](#layer-5-state--commands)
- [Layer 6: Advanced Mechanisms](#layer-6-advanced-mechanisms)
- [Supplementary Exercises: Python Simplified Versions](#supplementary-exercises-python-simplified-versions)
- [Disclaimer](#disclaimer)

---

## How to Start

**Do not read cover to cover.** The codebase is large. The right approach is to read by module, driven by questions.

Recommended order: Entry → Loop → Tools → UI → State → Advanced

For each module, ask yourself:
- What problem does this file solve?
- If I had to implement this from scratch, how would I do it?
- What is this similar to that I already know?

---

## Layer 1: Startup & Entry Points

**Core question**: What happens after you type the `claude` command?

```
claudecode_src/src/
├── main.tsx                  # Main entry: CLI parsing, initialization, REPL launch
├── entrypoints/              # Different startup modes (interactive, non-interactive, server)
├── bootstrap/                # First-run initialization logic
├── setup.ts                  # Environment detection, config loading
└── replLauncher.tsx          # REPL session launcher
```

**Key things to read:**
- Argument parsing and mode dispatch in `main.tsx`
- How `setup.ts` detects API keys, permissions, and OS differences
- The fork point between interactive and non-interactive modes in `entrypoints/`

---

## Layer 2: Agent Core Loop

**Core question**: How does Claude Code keep looping through tool calls until a task is complete?

```
claudecode_src/src/
├── query.ts                  # Single conversation request handler
├── QueryEngine.ts            # Multi-turn loop engine (where the Agent Loop lives)
├── query/                    # Query sub-modules (streaming, error handling, etc.)
├── Task.ts                   # Data structure for a single task
├── tasks.ts                  # Task registration and management
└── tasks/                    # Sub-tasks, parallel tasks, and extensions
```

**Key things to read:**
- `QueryEngine.ts` is the heart of the entire agent — find where the while loop is
- `query.ts` handles a single API call, including streaming response assembly
- `Task.ts` defines the task state machine: `pending → running → completed/error`
- Compare with `v1_basic_agent.py` (the Python simplified version in this repo) to understand the gap

---

## Layer 3: Tool System

**Core question**: What built-in tools does Claude Code have, and how is each one implemented?

```
claudecode_src/src/
├── Tool.ts                   # Base class / interface for all tools
├── tools.ts                  # Registry of all tools
└── tools/                    # Individual tool implementations
    ├── BashTool/             # Execute shell commands
    ├── FileReadTool/         # Read files
    ├── FileEditTool/         # Precise file editing
    ├── FileWriteTool/        # Write files
    ├── GlobTool/             # File pattern matching
    ├── GrepTool/             # Content search
    ├── AgentTool/            # Sub-agent (most complex)
    ├── MCPTool/              # MCP protocol tool
    ├── TodoWriteTool/        # Todo management
    ├── TaskCreateTool/       # Task creation
    ├── SkillTool/            # Skill invocation
    ├── LSPTool/              # Language Server Protocol integration
    ├── EnterPlanModeTool/    # Plan mode
    └── ...  (30+ tools total)
```

**Key things to read:**
- Start with `Tool.ts` — understand the interface: `name / description / inputSchema / call()`
- Then read `BashTool/` — the most fundamental tool with the most direct logic
- Read `AgentTool/` to understand how sub-agents are nested (most complex)
- Pay attention to each tool's `inputSchema` — that's exactly what the model sees as JSON Schema

---

## Layer 4: UI Layer — Ink/React

**Core question**: How are the pretty output, progress bars, and dialogs rendered in a terminal?

```
claudecode_src/src/
├── ink.ts                    # Ink framework entry (React for CLI)
├── components/               # UI component library
│   ├── App.tsx               # Root component
│   ├── AgentProgressLine.tsx # Agent execution progress display
│   ├── BashModeProgress.tsx  # Bash execution progress
│   ├── CompactSummary.tsx    # Conversation summary
│   └── ...
├── screens/                  # Different screens/pages (onboarding, main UI, etc.)
├── outputStyles/             # Output styles (syntax highlighting, Markdown rendering)
└── dialogLaunchers.tsx       # Dialog trigger logic
```

**Key things to read:**
- `App.tsx` is the root of the React component tree — get the overall layout clear
- Claude Code uses the **Ink** framework to render React components in the terminal — same syntax as web React
- `outputStyles/` explains why code blocks have syntax highlighting

---

## Layer 5: State & Commands

**Core question**: Where is multi-turn conversation history, user settings, and session state stored?

```
claudecode_src/src/
├── state/                    # Global state management
│   ├── AppState.tsx          # Application state definition
│   ├── AppStateStore.ts      # State store (Redux-like)
│   ├── store.ts              # State store entry point
│   └── selectors.ts          # State selectors
├── context/                  # React Context (component-level shared state)
├── context.ts                # Conversation context (message history)
├── history.ts                # History persistence
├── commands.ts               # Slash command registration
└── commands/                 # Each slash command's implementation (/help /clear /model etc.)
```

**Key things to read:**
- `context.ts` manages message history — this is the foundation of the agent's multi-turn memory
- Each `.ts` file in `commands/` corresponds to one `/command`
- `state/AppStateStore.ts` has an architecture close to Redux but without the Redux dependency

---

## Layer 6: Advanced Mechanisms

After finishing the first five layers, dive into these advanced modules:

```
claudecode_src/src/
├── skills/                   # Skills system (reusable agent behaviors)
│   ├── bundled/              # Built-in skills
│   └── bundledSkills.ts      # Skill registration
├── coordinator/              # Multi-agent coordinator
│   └── coordinatorMode.ts    # Coordinator mode (manages multiple sub-agents)
├── buddy/                    # Buddy mode (pair-programming assistant)
├── remote/                   # Remote execution (non-local environments)
├── server/                   # HTTP server mode
├── keybindings/              # Keyboard shortcut system
├── vim/                      # Vim mode support
├── voice/                    # Voice input
├── plugins/                  # Plugin system
├── memdir/                   # Memory directory (persistent memory)
├── cost-tracker.ts           # Token usage and cost tracking
└── costHook.ts               # Cost hooks

claudecode_src/vendor/        # Native modules
├── audio-capture-src/        # Audio capture (voice input backend)
├── image-processor-src/      # Image processing
├── modifiers-napi-src/       # Keyboard modifier key detection (Node.js native addon)
└── url-handler-src/          # URL protocol handling
```

---

## Supplementary Exercises: Python Simplified Versions

This repo also contains three Python files — minimal re-implementations of Claude Code's core mechanisms. Use them as a warm-up before reading the source, or as a reference after studying a module:

| File | Corresponding Source Module | Purpose |
|------|-----------------------------|---------|
| `easy_cil.py` | `tools/BashTool/` | Minimum viable: single tool + safety guardrails |
| `v1_basic_agent.py` | `QueryEngine.ts` + core tools | Full agent loop (synchronous) |
| `v2_async_agent.py` | `Task.ts` + `tasks/` | Async task decoupling (state machine) |

```bash
pip install openai python-dotenv
export DEEPSEEK_API_KEY=your_key
python v1_basic_agent.py
```

---

## Disclaimer

This repository is intended solely for personal learning and technical research. The source code in the `claudecode_src/` directory originates from a leaked version circulating publicly online. This repository makes no representations as to its legal status. The directory is listed in `.gitignore` and will not be uploaded to any public platform alongside this repository.

**Do not use the source code for any commercial purpose. Do not redistribute it. Do not use it in ways that infringe upon Anthropic's rights. All responsibility rests with the user.**
