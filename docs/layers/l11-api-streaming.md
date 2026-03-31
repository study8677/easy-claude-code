# Layer 11：API Streaming 与事件模型

[English](./l11-api-streaming.en.md) | 中文

## 核心问题

Claude Code 是怎样把底层 API stream 转换成上层统一事件流的？

## 建议先复习

- `l2-agent-loop`
- `l8-streaming`

## 先看源码

- `services/api/claude.ts`
- `query.ts`

## 关键搜索词

- `queryModelWithStreaming`
- `api_request_sent`
- `first_chunk`
- `stream_request_start`
- `message_start`

## 这一层要观察什么

- API 请求发出、收到响应头、收到首个 chunk 的时间点是如何被测量的
- 为什么 `query.ts` 先 `yield { type: 'stream_request_start' }`
- 为什么流式 watchdog、stall detection、fallback timeout 都在 API 层附近处理

## 源码证据

- `services/api/claude.ts:752`：`export async function* queryModelWithStreaming`
- `services/api/claude.ts:1805-1807`：`api_request_sent`
- `services/api/claude.ts:1971-1973`：`first_chunk`
- `query.ts:337`：`stream_request_start`

## 这一层真正学什么

Claude Code 的“streaming”不是单纯把模型文本一段段吐出来，而是把网络层状态、事件边界、错误恢复和性能测量都统一到一个可消费的事件模型里。学这一层，重点不是 Anthropic SDK 怎么用，而是“事件语义”怎么定义。

## 看完后请回答

1. 为什么 `services/api/claude.ts` 需要关心 stall 和 idle timeout？
2. `query.ts` 和 API 层之间最重要的契约是什么？
3. 如果底层 stream 断了，Claude Code 为什么不应该只抛一个普通异常了事？
