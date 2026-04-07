# P3：源码阅读

[English](./p3-source-reading.en.md) | 中文

## 适合谁

- 已经理解基础 loop，准备真正穿透源码的人
- 想把“会跑示例”升级成“能解释真实实现”的人

## 预计时间

2-3 小时

## 本阶段只搞懂什么

这一阶段不再停留在概念层，而是沿着已经稳定的主线直接读关键源码：

1. `query.ts` 怎样把单轮主线串起来
2. `QueryEngine.ts` 为什么是会话 orchestration 中心，而不是多余包裹层
3. `services/api/claude.ts` 怎样把 provider streaming 转成上层事件流

## 你在主线中的位置

**主线位置：** 主线概念已经稳定 → 直接阅读 `query.ts` → `QueryEngine.ts` → `services/api/claude.ts`

P2 帮你建立了“单轮如何推进”的直觉；P3 的目标是把这条直觉压到真实源码上。

这时你不再只是“知道有这些概念”，而是要沿主线直接阅读关键文件，确认：

- 一轮请求在哪里开始推进
- orchestration 在哪里集中管理
- streaming 事件在哪里被抬升成上层可消费的流

## 先跑哪个 example

先回到最贴主线的 example：

```bash
python examples/l2_agent_loop.py
```

如果你有 API Key，再补：

```bash
python examples/l8_streaming.py
```

这里跑 example 的目的不是学新概念，而是让你在打开真实源码前重新抓稳主线节奏。

## 再读哪篇 layer

按这条顺序读：

1. [L10 QueryEngine 与系统 Prompt 拼装](../layers/l10-query-engine.md)
2. [L11 API Streaming 与事件模型](../layers/l11-api-streaming.md)
3. [源码导航手册](../source-navigation.md)
4. [example 到源码的桥接页：l2 / l8](../example-source-bridge.md)

只有在主线源码已经稳定后，再把这些当第二层补充：

- [L5 状态与命令](../layers/l5-state-commands.md)
- [L12 REPL 主界面与输入系统](../layers/l12-repl-ui.md)
- [L9 Context 管理](../layers/l9-context.md)

## 再开哪些源码文件

这一阶段直接开主线三件套：

- `claudecode_src/src/query.ts`
- `claudecode_src/src/QueryEngine.ts`
- `claudecode_src/src/services/api/claude.ts`

如果你已经把这三者的分工说清，再把 UI 当第二层补充：

- `claudecode_src/src/screens/REPL.tsx`

## 这一阶段先不要看什么

现在先不要把注意力分散到这些边界专题：

- memory 提取细节
- hooks / plugins / MCP 扩展面
- print / serve / bridge 等 runtime modes
- coordinator / structured output 边界
- 如果你还没把三件主线文件读稳，也先不要展开 REPL 的细粒度状态树

P3 的意义是：只有主线稳定后，才值得向外分支。

## 推荐阅读顺序

### 第一遍：两深一浅

1. `query.ts` 深读
2. `QueryEngine.ts` 深读
3. `services/api/claude.ts` 先抓事件流主线

### 第二遍：需要时再补

1. `screens/REPL.tsx`
2. `L5`
3. `L12`
4. `L9`

不要一开始就试图把 4 个核心文件和 5 篇 deep-dive 一次吃掉。

## 必搜符号

- `system_message_yielded`
- `before_getSystemPrompt`
- `after_getSystemPrompt`
- `queryModelWithStreaming`
- `api_request_sent`
- `processInitialMessage`
- `DO NOT ADD MORE STATE HERE`

如果你准备补 context，再加：

- `SYSTEM_PROMPT_DYNAMIC_BOUNDARY`

## 这一阶段只回答三个问题

1. QueryEngine 为什么不是多余包裹层，而是会话 orchestration 中心？
2. API streaming 是如何被转成上层事件流的？
3. `query.ts`、`QueryEngine.ts`、`services/api/claude.ts` 三者是如何分工的？

## 推荐练习

- [练习 2：为什么 QueryEngine 不是多余抽象](../exercises.md)
- [练习 4：streaming 事件](../exercises.md)
- 如果你已经补看 REPL，再做 [练习 5：REPL 状态边界](../exercises.md)

## 完成标准

完成这一页时，你应该能：

- 解释 `query.ts`、`QueryEngine.ts`、`services/api/claude.ts` 之间的分工
- 说清系统 Prompt 拼装和事件流分别在哪一层发生
- 在源码里独立搜索并定位上面的关键符号
- 明确知道 permissions / memory / runtime modes / coordinator 还属于下一阶段的边界专题

如果还不稳，先回去补：

- `P2`，如果 loop、permissions、streaming 还没连起来
- `L10`，如果你还看不清 QueryEngine 的职责
- `L11`，如果事件流仍然像“API 细节”

## 下一步

继续去 [P4 高级架构](./p4-advanced-architecture.md)
