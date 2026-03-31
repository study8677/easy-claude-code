# Layer 2：Agent 核心循环

[English](./l2-agent-loop.en.md) | 中文

## 核心问题

Claude Code 如何在“模型回复”和“工具执行”之间持续循环，直到任务完成？

## 先运行

```bash
python examples/l2_agent_loop.py
```

需要 `DEEPSEEK_API_KEY`。

## 先看源码

- `query.ts`
- `QueryEngine.ts`
- `tasks/`

## 关键搜索词

- `export async function* query`
- `async function* queryLoop`
- `while (true)`
- `tool_result`

## 这一层要观察什么

- 谁在维护消息历史
- 工具结果为什么必须追回历史
- loop 的退出条件是什么
- 事件流和最终回答之间是什么关系

## 示例和真实源码的差异

示例只展示最小循环。真实源码会处理流式事件、错误恢复、取消、权限、任务状态和 UI 事件发射。

## 看完后请回答

1. 为什么 Agent Loop 更像“状态机 + 事件流”，而不是普通的 `while`？
2. 如果模型返回多个工具调用，Claude Code 如何保持上下文一致？
3. QueryEngine 和 `query.ts` 分别承担什么职责？
