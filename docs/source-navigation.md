# Claude Code 源码导航手册

[English](./source-navigation.en.md) | 中文

> `source-map` 解决“先读哪条调用链”，这份手册解决“在源码里怎么快速找到它”。

如果你是从 `examples/` 或某篇 layer 文档过来的，这里就是例子和源码之间的落点：先把概念映射成符号，再去源码里验证边界和约束。

## 1. 最有用的搜索命令

先在仓库根目录执行这些命令：

```bash
rg -n "export async function\\* query|async function\\* queryLoop" claudecode_src/src/query.ts
rg -n "class QueryEngine|before_getSystemPrompt|system_message_yielded" claudecode_src/src/QueryEngine.ts
rg -n "queryModelWithStreaming|api_request_sent|first_chunk" claudecode_src/src/services/api/claude.ts
rg -n "buildTool|getTools|canUseTool" claudecode_src/src -S
rg -n "BASH_SECURITY_CHECK_IDS|canAutoApprove" claudecode_src/src/tools/BashTool -S
rg -n "REPL|processInitialMessage" claudecode_src/src/screens/REPL.tsx -S
rg -n "buildMemoryLines|ENTRYPOINT_NAME|extractMemories" claudecode_src/src -S
rg -n "bridgeMain|runHeadless|serve" claudecode_src/src/main.tsx claudecode_src/src/bridge -S
```

如果你只愿意记一个工具，就记住 `rg -n`。这个仓库最有效的阅读方式不是点目录，而是先抓符号。

## 2. 按问题找入口

### 我想搞懂 Claude Code 的主循环

- 先看：`query.ts`
- 再看：`QueryEngine.ts`
- 先搜：
  - `export async function* query`
  - `async function* queryLoop`
  - `tool_result`
- 要回答：
  - 谁在维护一轮对话的状态
  - 工具结果为什么要追回消息历史
  - 什么时候退出循环

### 我想搞懂系统 Prompt 是怎么拼出来的

- 先看：`QueryEngine.ts`
- 再看：`constants/prompts.ts`
- 先搜：
  - `before_getSystemPrompt`
  - `after_getSystemPrompt`
  - `fetchSystemPromptParts`
  - `SYSTEM_PROMPT_DYNAMIC_BOUNDARY`
- 要回答：
  - 哪些部分是稳定前缀
  - 哪些部分是动态追加
  - 为什么这种分层对 prompt cache 有利

### 我想搞懂工具系统和权限系统

- 先看：`Tool.ts`, `tools.ts`
- 再看：`tools/BashTool/`
- 先搜：
  - `buildTool`
  - `getTools`
  - `BASH_SECURITY_CHECK_IDS`
  - `canUseTool`
- 要回答：
  - 工具 schema 和执行函数在哪里拼起来
  - 权限判断在哪层做
  - 安全检查和审批策略为什么拆开

### 我想搞懂 streaming 和事件模型

- 先看：`query.ts`
- 再看：`services/api/claude.ts`
- 先搜：
  - `stream_request_start`
  - `queryModelWithStreaming`
  - `api_request_sent`
  - `first_chunk`
- 要回答：
  - API 字节流怎么变成上层事件
  - query loop 如何消费这些事件
  - 为什么 async generator 比 callback 更适合这里

### 我想搞懂 REPL 和终端 UI

- 先看：`screens/REPL.tsx`
- 再看：`bootstrap/state.ts`, `components/`
- 先搜：
  - `export function REPL`
  - `processInitialMessage`
  - `DO NOT ADD MORE STATE HERE`
- 要回答：
  - 什么状态必须全局共享
  - 什么状态故意留在组件内部
  - 首条消息是怎样进入 REPL 的

### 我想搞懂 memory 和 context

- 先看：`memdir/memdir.ts`
- 再看：`services/extractMemories/`, `constants/prompts.ts`
- 先搜：
  - `ENTRYPOINT_NAME`
  - `buildMemoryLines`
  - `extractMemories`
  - `SYSTEM_PROMPT_DYNAMIC_BOUNDARY`
- 要回答：
  - memory 怎么变成系统提示的一部分
  - 为什么 memory 不直接无限追加
  - context 管理和 memory 提取的边界在哪里

### 我想搞懂 print / serve / bridge 模式

- 先看：`main.tsx`
- 再看：`entrypoints/cli.tsx`, `bridge/bridgeMain.ts`
- 先搜：
  - `runHeadless`
  - `serve`
  - `bridgeMain`
- 要回答：
  - 哪些模式共用 QueryEngine
  - 哪些模式绕开 REPL
  - 为什么 runtime mode 要在入口就分流

## 3. 关键符号索引

| 主题 | 先看文件 | 先搜什么 | 为什么它重要 |
|---|---|---|---|
| 启动入口 | `main.tsx`, `setup.ts` | `main_entry`, `setup`, `runHeadless` | 决定 CLI 如何进入不同运行模式 |
| 主循环 | `query.ts` | `query`, `queryLoop`, `tool_result` | Claude Code 最核心的控制流 |
| 会话编排 | `QueryEngine.ts` | `class QueryEngine`, `system_message_yielded` | 主循环之前的 staging 区 |
| API 流式层 | `services/api/claude.ts` | `queryModelWithStreaming`, `first_chunk` | 把模型流变成统一事件 |
| 工具注册 | `Tool.ts`, `tools.ts` | `buildTool`, `getTools` | 决定工具如何暴露给模型 |
| Bash 安全 | `tools/BashTool/bashSecurity.ts` | `BASH_SECURITY_CHECK_IDS` | 命令注入和危险模式检测的核心 |
| REPL | `screens/REPL.tsx` | `REPL`, `processInitialMessage` | 终端 UI 和交互主屏 |
| Hook / Plugin | `utils/hooks/*`, `plugins/*` | `execAgentHook`, `builtinPlugins` | 扩展点如何接入主流程 |
| Memory | `memdir/memdir.ts` | `ENTRYPOINT_NAME`, `buildMemoryLines` | memory 如何进入系统上下文 |
| 多 Agent | `tools/SyntheticOutputTool/*`, `coordinator/coordinatorMode.ts` | `SYNTHETIC_OUTPUT_TOOL_NAME` | 受控 structured output 的边界 |
| Runtime modes | `bridge/bridgeMain.ts`, `entrypoints/cli.tsx` | `bridgeMain`, `serve` | REPL 外的运行面 |

## 4. 一条高效的源码阅读流程

1. 先选一个问题，不要先选一个目录。
2. 如果你刚跑完 example，先回头确认它对应哪条 layer / 调用链。
3. 用 `docs/source-map.md` 找到对应调用链。
4. 用这份手册里的搜索词定位函数和常量。
5. 先读“入口函数 + 返回/退出点 + finally/cleanup”。
6. 再去比较 `examples/` 的教学简化版和真实源码多了哪些约束。

如果你已经比较熟悉代码，可以把第 2 步和第 5 步压缩成一次快速回查，但不要省掉“例子 -> 符号 -> 边界”这条线。

## 5. 不要这样读

- 不要从 `claudecode_src/src/` 第一层目录开始线性翻。
- 不要一次追 8 个 import。先把当前文件里最关键的 2 个符号看懂。
- 不要把 demo 当成源码等价实现。demo 是教学映射，不是逐行复刻。

## 6. 搭配阅读

- [学习路径](./paths/README.md)
- [源码导图](./source-map.md)
- [Layer 深挖目录](./layers/README.md)
- [学习练习册](./exercises.md)
- [FAQ](./faq.md)
