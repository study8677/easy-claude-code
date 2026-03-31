# Layer 12：REPL 主界面与输入系统

[English](./l12-repl-ui.en.md) | 中文

## 核心问题

`REPL.tsx` 这种超大入口组件在 Claude Code 里到底承担什么职责？

## 建议先复习

- `l4-ui-ink`
- `l5-state-commands`

## 先看源码

- `screens/REPL.tsx`
- `replLauncher.tsx`
- `components/PromptInput/*`

## 关键搜索词

- `export function REPL`
- `processInitialMessage`
- `pendingInitialQuery`
- `onSubmit`

## 这一层要观察什么

- REPL 为什么既像页面控制器，又像交互总线
- 初始消息、plan mode 退出消息、hook 驱动消息是怎么进入 REPL 的
- 用户输入为什么不总是直接变成一次 query，有时要先过 command / hook / history / buffer 处理

## 源码证据

- `screens/REPL.tsx:572`：`export function REPL`
- `screens/REPL.tsx:3035`：`processInitialMessage`
- `screens/REPL.tsx:3140`：触发 `processInitialMessage`

## 这一层真正学什么

不要把 REPL 只理解成“界面层”。在 Claude Code 里，REPL 也是交互编排层：它要接收用户输入、处理初始消息、协调 hooks、维护本地 UI 状态，还要决定什么时候真正把东西送进 QueryEngine。

## 看完后请回答

1. 为什么 `onSubmit` 和 `onQuery` 不是同一个概念？
2. `processInitialMessage` 解决了什么“不是用户当场输入”的场景？
3. 为什么 REPL 里允许存在大量本地 state，而不是全塞给全局状态？
