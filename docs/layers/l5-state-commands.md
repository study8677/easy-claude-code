# Layer 5：状态管理与斜杠命令

[English](./l5-state-commands.en.md) | 中文

## 核心问题

Claude Code 的多轮消息、用户设置、命令行为是如何组织和更新的？

## 先运行

```bash
python examples/l5_state_commands.py
```

## 先看源码

- `state/`
- `commands/`
- `history.ts`
- `context.ts`

## 关键搜索词

- `AppStateStore`
- `setState`
- `compact`
- `history`

## 这一层要观察什么

- 哪些状态需要不可变更新
- slash command 为什么像“命令注册表”而不是特殊语法
- 历史记录、UI 状态、QueryEngine 局部变量之间怎么分层

## 示例和真实源码的差异

示例保留了 store 和 command 的结构。真实实现字段更多，生命周期更长，也更强调持久化与副作用边界。

## 看完后请回答

1. 为什么消息历史不应该直接挂进全局单例？
2. `/compact` 这类命令更像工具、UI 事件，还是状态变换？
3. 什么类型的状态适合持久化，什么类型不适合？
