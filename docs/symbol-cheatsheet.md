# 符号速查卡

[English](./symbol-cheatsheet.en.md) | 中文

> 每行是一个经过源码验证的真实符号。搜索前先看这张表，避免盲目翻文件。

使用方式：在 `claudecode_src/src/` 里用 IDE 的全局搜索（⌘P / Ctrl+P 找文件，⌘F / Ctrl+F 找符号）。

---

## 核心循环

| 符号 | 文件 | 行号 | 说明 |
|------|------|------|------|
| `export async function* query` | `query.ts` | 219 | 主 generator 入口，外层处理启动和收尾 |
| `async function* queryLoop` | `query.ts` | 241 | 内层循环，`while(true)` 所在 |
| `while (true)` | `query.ts` | 307 | Agent Loop 本体，每轮调用模型 + 执行工具 |
| `isWithheldMaxOutputTokens` | `query.ts` | 175 | 错误扣押机制：中间错误先隐藏，等确认无法恢复才暴露 |
| `queryModelWithStreaming` | `services/api/claude.ts` | — | 发起 API 调用，返回 streaming 事件流 |
| `first_chunk` | `services/api/claude.ts` | — | streaming 首包事件，标志模型开始响应 |
| `stream_request_start` | `query.ts` | — | 每轮 queryLoop 开始时 yield 的事件类型 |
| `tool_result` | `query.ts` | — | 工具执行结果写回消息历史时使用的角色/类型 |
| `normalizeMessagesForAPI` | `utils/contentArray.ts` | — | 把内部消息格式转换为 API 可接受的格式 |

---

## 启动 / 模式分流

| 符号 | 文件 | 行号 | 说明 |
|------|------|------|------|
| `main` | `main.tsx` | — | CLI 入口，调用 setup 然后分流到 entrypoints |
| `setup` | `setup.ts` | — | 检测工作目录、API Key、权限模式，建立 session_id |
| `runHeadless` | `entrypoints/` | — | 非交互式运行模式入口 |
| `bridgeMain` | `entrypoints/` | — | Bridge 模式入口（用于 IDE 扩展等外部集成） |
| `processInitialMessage` | `screens/REPL.tsx` | — | 把启动时传入的消息注入交互流程 |

---

## 工具系统

| 符号 | 文件 | 行号 | 说明 |
|------|------|------|------|
| `getTools` | `tools.ts` | — | 返回当前 session 可用的完整工具列表（含 MCP 工具） |
| `buildTool` | `tools.ts` | — | 把工具定义包装成模型可用的 JSON schema |
| `canUseTool` | `tools/BashTool/bashPermissions.ts` | — | 权限检查入口：决定工具是否被允许执行 |
| `MCPTool` | `tools/MCPTool/` | — | 将 MCP 工具包装成与内置工具相同的 Tool 接口 |
| `ASYNC_AGENT_ALLOWED_TOOLS` | `coordinator/coordinatorMode.ts` | 2 | 多 Agent 模式下子 agent 允许使用的工具白名单 |
| `SyntheticOutputTool` | `coordinator/coordinatorMode.ts` | 88–97 | 协调者看到的输出：子 agent 只暴露最终结果，不暴露中间状态 |

---

## 权限系统

| 符号 | 文件 | 行号 | 说明 |
|------|------|------|------|
| `checkBashSecurity` | `tools/BashTool/bashSecurity.ts` | — | 23 个安全检查器的入口（第一层：语义拒绝） |
| `BASH_SECURITY_CHECK_IDS` | `tools/BashTool/bashSecurity.ts` | — | 23 个检查器的数字 ID 枚举（用数字不用字符串名） |
| `getCommandPermission` | `tools/BashTool/bashPermissions.ts` | — | 规则匹配层：对照已有的 allow/deny 规则 |
| `askPermission` | `tools/BashTool/bashPermissions.ts` | — | 用户确认层：弹出确认框，等待用户批准或拒绝 |

---

## 状态 / UI

| 符号 | 文件 | 行号 | 说明 |
|------|------|------|------|
| `DO NOT ADD MORE STATE HERE` | `bootstrap/state.ts` | 31 | 全局状态纪律边界，禁止随意扩充 |
| `setAppState` | `bootstrap/state.ts` | — | 修改全局 AppState 的唯一入口 |
| `REPL` | `screens/REPL.tsx` | — | 交互式终端的根组件，驱动 QueryEngine |

---

## Prompt Cache / Context

| 符号 | 文件 | 行号 | 说明 |
|------|------|------|------|
| `SYSTEM_PROMPT_DYNAMIC_BOUNDARY` | `constants/prompts.ts` | 114–115 | 静态前缀与动态部分的分界标记，保护 prompt cache 命中率 |
| `CONTEXT_1M_BETA_HEADER` | `constants/prompts.ts` | — | 开启 1M context 窗口的 beta header |
| `reversibility and blast radius` | `constants/prompts.ts` | 258 | system prompt 里"可逆性优先"的原文表述 |

---

## 记忆系统

| 符号 | 文件 | 行号 | 说明 |
|------|------|------|------|
| 四类型记忆定义 | `memdir/memdir.ts` | 189 | `user / feedback / project / reference` 四种类型 |
| MEMORY.md 限制 | `memdir/memdir.ts` | 34–37 | 200 行上限 + 字节限制，防止 context 膨胀 |
| `buildMemoryLines` | `memdir/memdir.ts` | — | 把记忆文件内容格式化并注入 system prompt |
| `extractMemories` | `services/extractMemories/` | — | 对话结束后异步提取值得记住的信息 |
| `ENTRYPOINT_NAME` | `constants/prompts.ts` | — | 记忆系统用来区分当前 session 入口类型的标识 |

---

## Sticky Latch（缓存稳定机制）

| 符号 | 文件 | 行号 | 说明 |
|------|------|------|------|
| `AFK_MODE` latch | `bootstrap/state.ts` | 226–233 | 一旦开启就不自动关闭，防止 system prompt 变化破坏 cache |
| `FAST_MODE` latch | `bootstrap/state.ts` | 226–233 | 同上，注释原文提到 `~50-70K token prompt cache` |

---

## 如何搜这些符号

```bash
# 在 claudecode_src/src/ 里搜精确符号名
grep -r "queryModelWithStreaming" claudecode_src/src/ --include="*.ts"

# 搜特定文件
grep -n "while (true)" claudecode_src/src/query.ts

# 搜注释原文
grep -r "DO NOT ADD MORE STATE" claudecode_src/src/
```

或直接用 IDE 的全局符号搜索（VS Code: ⌘T / Ctrl+T）。
