# Layer 8：流式架构与 Async Generator

[English](./l8-streaming.en.md) | 中文

## 核心问题

为什么 Claude Code 用 async generator 作为 query 核心抽象，而不是 callback 或普通 async function？

## 先运行

```bash
python examples/l8_streaming.py
```

需要 `DEEPSEEK_API_KEY`。

## 先看源码

- `query.ts`
- `services/api/claude.ts`

## 关键搜索词

- `yield`
- `yield*`
- `queryModelWithStreaming`
- `stream_request_start`

## 这一层要观察什么

- 文本 chunk、tool_use、tool_result 是怎么统一成事件流的
- 取消和中断为什么更适合 generator 语义
- `yield*` 为什么让多层 Agent 组合变简单

## 示例和真实源码的差异

示例只保留了事件形状和最小 streaming loop。真实实现还负责 SDK 事件转换、错误恢复、吞吐和 UI 联动。

## 看完后请回答

1. Promise、callback、generator 在 Claude Code 这个场景下分别缺什么？
2. 为什么 `yield*` 是多 Agent / 多层事件穿透的关键？
3. `services/api/claude.ts` 和 `query.ts` 的边界在哪里？
