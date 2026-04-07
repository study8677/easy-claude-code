# Claude Code 主线源码导图

[English](./source-map.en.md) | 中文

> 这份导图只回答一个问题：一次请求现在走到主线哪一步，下一步该去哪里追源码。

如果你还没抓稳主线，先回到 [学习路径页](./paths/README.md)。如果你是从 example 过来的，先看 [example 到源码的桥接页](./example-source-bridge.md)。

## 一次请求的完整生命周期

```mermaid
flowchart TD
    A([用户输入]) --> B

    subgraph S1[“Step 1 · 启动 / 模式分流”]
        B[“main.tsx → setup.ts → entrypoints/”]
    end

    subgraph S2[“Step 2 · 进入 query / queryLoop”]
        C[“QueryEngine.ts → query.ts\nasync function* query()”]
    end

    subgraph S3[“Step 3 · 调用模型 / 解析输出”]
        D[“services/api/claude.ts\nqueryModelWithStreaming”]
    end

    subgraph S4[“Step 4 · 工具执行”]
        E[“bashPermissions.ts\n语义拒绝 → 规则匹配 → 询问用户”]
    end

    subgraph S5[“Step 5 · tool_result 回流”]
        F[“追回消息历史\n同一轮 queryLoop 继续”]
    end

    subgraph S6[“Step 6 · 状态 / UI 更新”]
        G[“REPL.tsx + bootstrap/state.ts”]
    end

    B --> C
    C --> D
    D -->|”tool_use”| E
    E --> F
    F -->|”继续 while true”| D
    D -->|”end_turn”| G
    G --> H{下一轮？}
    H -->|”用户继续输入”| C
    H -->|”退出”| Z([结束])
```

## 怎么使用这份导图

1. 先定位你现在站在主线的哪一步。
2. 对照该步骤的输入 / 输出，确认这一步到底完成了什么。
3. 只打开 1 到 2 个核心文件，并先搜 2 到 4 个 symbol。
4. 沿着”下一步流向”继续，不要一开始横向散读所有子系统。

<a id="step-1-startup-routing"></a>
## Step 1 — 启动 / 模式分流

- **主线位置：** 用户输入 → 启动 / 模式分流
- **输入：** CLI 参数、当前工作目录、配置 / 环境变量、运行模式选择
- **输出：** 选定 entrypoint、完成基础 setup，并决定是进入交互式会话还是 headless / bridge / 其他运行面
- **先看文件：**
- [`claudecode_src/src/main.tsx`](../claudecode_src/src/main.tsx)
- [`claudecode_src/src/setup.ts`](../claudecode_src/src/setup.ts)
- [`claudecode_src/src/cli/print.ts`](../claudecode_src/src/cli/print.ts)

- **建议先搜的 symbol：**
- `main`
- `setup`
- `runHeadless`

- **下一步流向：**
进入 Step 2，真正把 prompt、history、tool context 送进 `query` / `queryLoop`。

<a id="step-2-enter-query-loop"></a>
## Step 2 — 进入 `query` / `queryLoop`

- **主线位置：** 启动完成 → 进入单轮请求主线
- **输入：** 已经选好的运行模式、当前 session 状态、用户消息 / 初始消息、工具上下文
- **输出：** `QueryEngine` 或 REPL 把一次 turn 交给 `query`，并启动 `queryLoop` 这条 async generator 主线
- **先看文件：**
- [`claudecode_src/src/QueryEngine.ts`](../claudecode_src/src/QueryEngine.ts)
- [`claudecode_src/src/query.ts`](../claudecode_src/src/query.ts)
- [`claudecode_src/src/screens/REPL.tsx`](../claudecode_src/src/screens/REPL.tsx)

- **建议先搜的 symbol：**
- `QueryEngine`
- `query`
- `queryLoop`
- `processInitialMessage`

- **下一步流向：**
进入 Step 3，看模型请求如何被发出，以及返回的 assistant 内容为什么会转成“继续对话”还是“调用工具”。

<a id="step-3-model-output-tool-selection"></a>
## Step 3 — 模型产出 / 工具选择

- **主线位置：** `queryLoop` 内部 → 调模型 → 解析 streaming 事件 → 决定是否发起 `tool_use`
- **输入：** 当前消息历史、system prompt、模型配置、可用工具集合
- **输出：** assistant 文本块、`tool_use` 块、stop reason，以及继续下一步所需的事件流
- **先看文件：**
- [`claudecode_src/src/query.ts`](../claudecode_src/src/query.ts)
- [`claudecode_src/src/services/api/claude.ts`](../claudecode_src/src/services/api/claude.ts)
- [`claudecode_src/src/tools.ts`](../claudecode_src/src/tools.ts)
- [`claudecode_src/src/Tool.ts`](../claudecode_src/src/Tool.ts)

- **建议先搜的 symbol：**
- `queryModelWithStreaming`
- `getTools`
- `buildTool`
- `isWithheldMaxOutputTokens`

- **下一步流向：**
如果模型产出 `tool_use`，进入 Step 4；如果直接形成可展示的 assistant 输出，则跳到 Step 6 / Step 7 看状态更新与退出条件。

<a id="step-4-tool-execution"></a>
## Step 4 — 工具执行

- **主线位置：** 模型已经选中工具 → 权限检查 / 安全检查 → 实际执行工具
- **输入：** `tool_use` blocks、tool registry、permission context、当前工作目录与安全策略
- **输出：** 工具成功结果、拒绝结果、错误结果，最终都会变成可回流的 `tool_result`
- **先看文件：**
- [`claudecode_src/src/query.ts`](../claudecode_src/src/query.ts)
- [`claudecode_src/src/tools.ts`](../claudecode_src/src/tools.ts)
- [`claudecode_src/src/tools/BashTool/bashPermissions.ts`](../claudecode_src/src/tools/BashTool/bashPermissions.ts)
- [`claudecode_src/src/tools/BashTool/bashSecurity.ts`](../claudecode_src/src/tools/BashTool/bashSecurity.ts)

- **建议先搜的 symbol：**
- `canUseTool`
- `checkBashSecurity`
- `getCommandPermission`
- `askPermission`

- **下一步流向：**
进入 Step 5，把工具结果重新插回同一轮 assistant 轨迹，准备下一次模型续跑。

<a id="step-5-tool-result-reentry"></a>
## Step 5 — 工具结果回流到主线

- **主线位置：** 工具执行完成 → 结果写回消息历史 → 同一轮 `queryLoop` 继续推进
- **输入：** 工具输出、拒绝 / 错误信息、已有 assistant trajectory
- **输出：** 带 `tool_result` 的用户侧消息、更新后的 turn history，以及下一次模型调用的输入
- **先看文件：**
- [`claudecode_src/src/query.ts`](../claudecode_src/src/query.ts)
- [`claudecode_src/src/services/api/claude.ts`](../claudecode_src/src/services/api/claude.ts)
- [`claudecode_src/src/utils/contentArray.ts`](../claudecode_src/src/utils/contentArray.ts)

- **建议先搜的 symbol：**
- `tool_result`
- `queryLoop`
- `normalizeMessagesForAPI`
- `insertBlockAfterToolResults`

- **下一步流向：**
Step 5 说的是同一轮控制流怎样继续：工具结果被塞回消息历史后，`queryLoop` 会回到 Step 3 继续请求模型。Step 6 不是另一条控制流，而是对这些同一批事件的 UI / state 观察面。

<a id="step-6-state-ui-update"></a>
## Step 6 — 状态 / UI 更新

- **主线位置：** 每轮事件推进时，REPL 和全局状态把“现在发生了什么”呈现出来
- **输入：** query events、消息历史、loading / permission / notification 状态、初始消息和命令入口
- **输出：** 终端 UI 渲染、session state 更新、用户可见的消息 / 工具结果 / 交互提示
- **先看文件：**
- [`claudecode_src/src/bootstrap/state.ts`](../claudecode_src/src/bootstrap/state.ts)
- [`claudecode_src/src/screens/REPL.tsx`](../claudecode_src/src/screens/REPL.tsx)
- [`claudecode_src/src/components/Messages.tsx`](../claudecode_src/src/components/Messages.tsx)
- [`claudecode_src/src/history.ts`](../claudecode_src/src/history.ts)

- **建议先搜的 symbol：**
- `DO NOT ADD MORE STATE HERE`
- `REPL`
- `processInitialMessage`
- `setAppState`

- **下一步流向：**
如果当前 turn 还在跑，继续跟 Step 3 / Step 5 的事件往前走；如果当前 turn 收束，就进入 Step 7 看是继续下一轮还是退出。

<a id="step-7-next-turn-or-exit"></a>
## Step 7 — 下一轮 / 退出条件

- **主线位置：** 一轮结束 → 判断是否继续、多轮上下文如何保住、退出前做什么收尾
- **输入：** stop reason、累积 history、context trimming / prompt cache 状态、memory extraction 触发条件
- **输出：** 进入下一轮用户输入、完成收尾后退出，或在后台做 memory / context 维护
- **先看文件：**
- [`claudecode_src/src/query.ts`](../claudecode_src/src/query.ts)
- [`claudecode_src/src/constants/prompts.ts`](../claudecode_src/src/constants/prompts.ts)
- [`claudecode_src/src/utils/context.ts`](../claudecode_src/src/utils/context.ts)
- [`claudecode_src/src/memdir/memdir.ts`](../claudecode_src/src/memdir/memdir.ts)
- [`claudecode_src/src/services/extractMemories/extractMemories.ts`](../claudecode_src/src/services/extractMemories/extractMemories.ts)

- **建议先搜的 symbol：**
- `SYSTEM_PROMPT_DYNAMIC_BOUNDARY`
- `CONTEXT_1M_BETA_HEADER`
- `ENTRYPOINT_NAME`
- `buildMemoryLines`
- `extractMemories`

- **下一步流向：**
如果用户继续输入，就回到 Step 2 再跑下一轮；如果 runtime 结束，就沿着当前模式退出；如果你要追主线外的扩展，再去看 [layers/README.md](./layers/README.md) 和 [source-navigation.md](./source-navigation.md)。

## 主线外但常见的延伸

- 想看多 agent / structured output 怎么挂到主线上：先读 [L6 高级机制](./layers/l6-advanced.md)
- 想看 memory / context 为什么影响“能不能继续下一轮”：先读 [L14 Memory 提取与 Team Memory](./layers/l14-memory-system.md)
- 想看 runtime modes 为什么改变入口但不改主线核心：先读 [L15 Print / Serve / Bridge 等运行模式](./layers/l15-runtime-modes.md)
