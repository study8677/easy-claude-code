# Claude Code Study Exercises

[中文](./exercises.md) | English

> These exercises are not meant to make you read every file. The goal is to enter the codebase with a question and leave with evidence.

They are not only for beginners: new readers can use them to connect examples to source, while experienced readers can use them to check whether they can explain the boundary instead of just repeating the concept.

## How To Use This

1. Run one example or read one layer note first.
2. Then open the matching source map and confirm which call chain you are following.
3. Do only one or two exercises for the current topic.
4. When you answer, write down the symbols you searched and the files you checked.

## Exercise 1: Trace One Minimal Call Chain

Recommended stage: `P2`

Goal: follow one user input all the way to model execution and back to the final answer.

Steps:

1. Read the "Main Query Path" section in [the source map](./source-map.en.md).
2. Search `query` and `queryLoop`.
3. Search `queryModelWithStreaming`.
4. Write one chain in your own words:

`who starts the turn -> who calls the model -> who handles tools -> who exits the loop`

Done when:

- You can explain the boundary between `QueryEngine.ts` and `query.ts`.
- You can point to the layer where tool results are appended back into history.

## Exercise 2: Explain Why QueryEngine Is Not Redundant

Recommended stage: `P3`

Goal: understand what QueryEngine adds beyond "just one more wrapper."

Steps:

1. Search `class QueryEngine`.
2. Search `before_getSystemPrompt`, `after_getSystemPrompt`, and `system_message_yielded`.
3. Using [L10](./layers/l10-query-engine.en.md), write down:

- three things it does before the main loop starts
- what would become worse if those responsibilities lived directly inside `query.ts`

Done when:

- Your answer uses at least two of these ideas: `system prompt assembly`, `session state`, `slash commands`.

## Exercise 3: Draw The Boundary Between Tools And Permissions

Recommended stage: `P2`

Goal: stop treating "tool calls" and "safety approval" as the same layer.

Steps:

1. Search `buildTool` and `getTools`.
2. Search `BASH_SECURITY_CHECK_IDS`.
3. Explain what each of these layers does:

- tool schema
- tool availability and approval
- command safety checks

Done when:

- You can point to at least `Tool.ts`, `tools.ts`, and `tools/BashTool/bashSecurity.ts`.
- You can explain why Claude Code uses a 3-layer permission model instead of a single prompt.

## Exercise 4: Explain Why Streaming Is Not Just A Callback

Recommended stage: `P2`

Goal: understand the engineering value of async generators.

Steps:

1. Search `stream_request_start`.
2. Search `queryModelWithStreaming` and `first_chunk`.
3. Using [L8](./layers/l8-streaming.en.md) and [L11](./layers/l11-api-streaming.en.md), answer:

- what raw API output becomes first
- why the upper loop benefits from `yield*`
- why cancellation, errors, and final text fit naturally into one event stream

Done when:

- Your answer is more specific than "streaming is convenient."
- You can name at least two concrete events or event stages.

## Exercise 5: Find The REPL State Boundary

Recommended stage: `P3`

Goal: understand why the terminal UI is not just one giant component.

Steps:

1. Search `DO NOT ADD MORE STATE HERE`.
2. Search `export function REPL` and `processInitialMessage`.
3. Explain:

- which state must be shared
- which state should stay local
- how the initial message enters the interaction flow

Done when:

- You can explain why global state and REPL-local state should not all be merged together.

## Exercise 6: Explain The Relationship Between Prompt Cache And Memory

Recommended stage: `P4`

Goal: avoid treating memory as "just put more text into the system prompt."

Steps:

1. Search `SYSTEM_PROMPT_DYNAMIC_BOUNDARY`.
2. Search `ENTRYPOINT_NAME`, `buildMemoryLines`, and `extractMemories`.
3. Explain:

- why the stable prefix and dynamic suffix are separated
- why memory behaves more like an index than a growing log

Done when:

- Your answer clearly separates context management, prompt cache, and memory extraction.

## Exercise 7: Compare REPL And Non-REPL Runtime Modes

Recommended stage: `P4`

Goal: understand that Claude Code is not only an interactive terminal shell.

Steps:

1. Search `runHeadless`.
2. Search `bridgeMain`.
3. Search `entrypoints/cli.tsx`.
4. Using [L15](./layers/l15-runtime-modes.en.md), explain:

- which modes share QueryEngine
- which modes bypass the REPL
- why dispatch must happen at the entrypoint

Done when:

- You can compare at least two of these surfaces: `REPL`, `print`, `bridge`.

## After You Finish These

If you can finish the first four exercises, you have already moved from “understanding examples” to “reading source.” These documents become much more useful:

- [Source Navigation Guide](./source-navigation.en.md)
- [Layer Deep-Dive Index](./layers/README.en.md)
- [Design Philosophy](../PHILOSOPHY_EN.MD)
