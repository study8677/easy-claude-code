# Layer 15：Print / Serve / Bridge 等运行模式

[English](./l15-runtime-modes.en.md) | 中文

## 核心问题

Claude Code 为什么不是只有一个交互式 REPL，而是同时支持 print、MCP serve、direct connect、bridge 等多种运行面？

## 建议先复习

- `l1-startup`
- `l12-repl-ui`

## 先看源码

- `main.tsx`
- `cli/print.ts`
- `replLauncher.tsx`
- `setup.ts`
- `bridge/bridgeMain.ts`

## 关键搜索词

- `runHeadless`
- `launchRepl`
- `mcp serve`
- `CLAUDE_CODE_ENTRYPOINT`
- `bridgeMain`

## 这一层要观察什么

- 同一个核心系统如何被包装成不同入口
- 为什么有些能力适合 REPL，有些更适合 headless / print
- bridge 为什么更像一个长期运行的会话服务，而不是一次性命令

## 源码证据

- `main.tsx`：入口判定、`--print`、`mcp serve`、connect/ssh/assistant 等早期 argv 处理
- `replLauncher.tsx`：交互式 REPL 启动包装
- `setup.ts:86-92`：messaging server 与 simple / bare 模式差异
- `bridge/bridgeMain.ts:1980`：`export async function bridgeMain`

## 这一层真正学什么

Claude Code 的核心能力不是“绑定在 REPL 里”的，而是被多个运行面消费。理解这一层后，你会更容易看懂为什么很多初始化逻辑写在 `main.tsx` 和 `setup.ts`，而不是写死在 REPL 组件里。

## 看完后请回答

1. 为什么 `--print` 不是“静默版 REPL”，而是独立运行面？
2. `bridgeMain` 这种长期运行模式和普通 CLI 单次执行在设计上有什么根本差异？
3. 如果要增加一种新的运行入口，最可能落在哪几个文件？
