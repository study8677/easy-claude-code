# Claude Code 学习练习册

[English](./exercises.en.md) | 中文

> 这些练习不要求你一次读完所有源码。目标是带着问题进入代码，再带着证据出来。

它们也不是“只给初学者”的练习：新读者可以用它们把例子和源码接起来，熟悉源码的人可以用它们检查自己是否真的能解释边界，而不是只会复述概念。

## 使用方式

1. 先跑一个 example，或者先读一篇 layer 文档。
2. 再去看对应的 source map，确认自己要追的是哪条调用链。
3. 只做当前主题的 1 到 2 个练习。
4. 回答时必须写出你搜索过的符号和看到的文件。

## 练习 1：追一条最小调用链

推荐阶段：`P2`

目标：从用户输入一路追到模型调用，再追到最终回答。

步骤：

1. 先读 [source-map](./source-map.md) 的“单轮查询主链路”。
2. 搜 `query` 和 `queryLoop`。
3. 再搜 `queryModelWithStreaming`。
4. 用自己的话写出一条链：

`谁发起这一轮 -> 谁调用模型 -> 谁处理工具 -> 谁决定退出`

完成标准：

- 你能说清 `QueryEngine.ts` 和 `query.ts` 的边界。
- 你能指出工具结果是在哪一层追回消息历史的。

## 练习 2：解释为什么 QueryEngine 不是多余抽象

推荐阶段：`P3`

目标：弄清楚 QueryEngine 到底增加了什么能力。

步骤：

1. 搜 `class QueryEngine`。
2. 搜 `before_getSystemPrompt`、`after_getSystemPrompt`、`system_message_yielded`。
3. 对照 [L10](./layers/l10-query-engine.md) 写下：

- 它在主循环开始前做了哪三件事
- 哪些事情如果塞进 `query.ts` 会让结构变差

完成标准：

- 你的答案里至少出现 `system prompt assembly`、`session state`、`slash commands` 三个概念中的两个。

## 练习 3：画出工具和权限的边界

推荐阶段：`P2`

目标：不要把“工具调用”和“安全审批”混成一层。

步骤：

1. 搜 `buildTool`、`getTools`。
2. 再搜 `BASH_SECURITY_CHECK_IDS`。
3. 解释下面三个层分别做什么：

- 工具 schema
- 工具可用性/审批
- 命令安全检测

完成标准：

- 你能指出 `Tool.ts`、`tools.ts`、`tools/BashTool/bashSecurity.ts` 至少这三个位置。
- 你能解释为什么 Claude Code 用三层权限，而不是一次性弹窗。

## 练习 4：解释 streaming 事件为什么不是普通回调

推荐阶段：`P2`

目标：理解 async generator 的工程价值。

步骤：

1. 搜 `stream_request_start`。
2. 搜 `queryModelWithStreaming`、`first_chunk`。
3. 对照 [L8](./layers/l8-streaming.md) 和 [L11](./layers/l11-api-streaming.md)，回答：

- API 流的原始输出先变成了什么
- 上层 loop 为什么适合 `yield*`
- 取消、错误和最终文本为什么适合统一放进事件流

完成标准：

- 你的答案不能只写“因为 streaming 很方便”。
- 必须能说出至少两个事件名或事件阶段。

## 练习 5：找出 REPL 的状态边界

推荐阶段：`P3`

目标：理解终端 UI 不是“一个巨型组件随便堆”。

步骤：

1. 搜 `DO NOT ADD MORE STATE HERE`。
2. 搜 `export function REPL` 和 `processInitialMessage`。
3. 解释：

- 哪些状态必须共享
- 哪些状态适合局部持有
- 初始消息是如何进入交互流程的

完成标准：

- 你能说明全局状态和 REPL 内部状态为什么不能全部混在一起。

## 练习 6：解释 prompt cache 和 memory 的关系

推荐阶段：`P4`

目标：不要把 memory 理解成“把更多文本塞进 system prompt”。

步骤：

1. 搜 `SYSTEM_PROMPT_DYNAMIC_BOUNDARY`。
2. 搜 `ENTRYPOINT_NAME`、`buildMemoryLines`、`extractMemories`。
3. 解释：

- 稳定前缀和动态部分为什么要分开
- memory 为什么更像索引，而不是日志堆积

完成标准：

- 你的答案里要明确区分 context 管理、prompt cache、memory 提取三个概念。

## 练习 7：比较 REPL 和非 REPL 运行模式

推荐阶段：`P4`

目标：知道 Claude Code 不只是一个交互式终端壳。

步骤：

1. 搜 `runHeadless`。
2. 搜 `bridgeMain`。
3. 搜 `entrypoints/cli.tsx`。
4. 对照 [L15](./layers/l15-runtime-modes.md)，解释：

- 哪些模式共享 QueryEngine
- 哪些模式绕过 REPL
- 为什么这些分流必须发生在入口处

完成标准：

- 你能至少比较 `REPL`、`print`、`bridge` 三个运行面中的两个。

## 做完这些以后

如果你已经能完成前 4 个练习，说明你已经从“看例子”进入到“读源码”了。再去看这些内容会更有收获：

- [源码导航手册](./source-navigation.md)
- [Layer 深挖目录](./layers/README.md)
- [设计哲学](../PHILOSOPHY.MD)
