# Layer 4：UI 层（Ink / React）

[English](./l4-ui-ink.en.md) | 中文

## 核心问题

Claude Code 为什么能在终端里做到近似 React 应用一样的重渲染、spinner、状态栏和消息列表？

## 先运行

```bash
python examples/l4_ui_ink.py
```

## 先看源码

- `components/`
- `screens/REPL.tsx`
- `ink.ts`
- `ink/`

## 关键搜索词

- `REPL`
- `App`
- `AgentProgressLine`
- `render`

## 这一层要观察什么

- UI 状态和消息状态是怎么分开的
- 为什么终端 UI 也适合声明式渲染
- spinner 和工具进度为什么不会打断消息历史

## 示例和真实源码的差异

示例用“清屏重绘”模拟 React/Ink 的 diff。真实实现有更细的组件边界、输入处理和终端兼容逻辑。

## 看完后请回答

1. Claude Code 的 UI 为什么不是简单地 `print()` 一行行输出？
2. 如果没有状态驱动渲染，工具执行进度会出现什么问题？
3. `REPL.tsx` 和 `ink/` 各自更像“产品层”还是“渲染层”？
