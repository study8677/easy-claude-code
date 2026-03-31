# Claude Code Tutorial FAQ

[中文](./faq.md) | English

## 1. Can I use this repo if I do not know TypeScript well?

Yes. Start with `examples/` for intuition, then read `docs/layers/`. The goal is not to master syntax first, but to understand what each subsystem is solving.

## 2. What can I still learn without an API key?

You can start with `l1`, `l3`, `l4`, `l5`, `l6`, `l7`, and `l9`. For `l2` and `l8`, read the matching layer docs and the source map first, then search the suggested symbols in the source.

## 3. Why not explain the repo file by file in order?

Because Claude Code was not designed to be learned linearly by directory order. A better way is to read by problem, call chain, and design decision.

## 4. Should I read QueryEngine first or query.ts first?

If you are new, read `query.ts` first to understand the loop. Then move to `QueryEngine.ts` to understand how system prompts, skills, plugins, and slash commands are staged before the loop begins.

## 5. Why does the repo have both 9 layers and L10-L15?

The first 9 layers are the main course with runnable examples. L10-L15 are source-heavy deep-dive topics for readers who are already inside the codebase.

## 6. What is the best reading workflow?

Run one example, read the matching layer note, then search the listed symbols in `claudecode_src/src/`. Do not start by reading the source tree from top to bottom. If you get lost in the source, keep the [Source Navigation Guide](./source-navigation.en.md) open next to it.

## 7. What should I do if I want to move from "I kind of get it" to real source analysis?

Use the [Study Exercises](./exercises.en.md). They force you to record the symbols you searched, the files you inspected, and the argument you can defend from the code.
