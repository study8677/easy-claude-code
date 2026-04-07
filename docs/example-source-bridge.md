# Example 到主线源码的桥接页

[English](./example-source-bridge.en.md) | 中文

> 先问：这个 example 在主线哪一步？再问：真实源码在这一步额外加了哪些复杂度？

如果你还没定位主线步骤，先回到 [主线源码导图](./source-map.md)。如果你想继续按阶段学习，再回到 [学习路径页](./paths/README.md)。

## Example → 主线步骤 → 下一跳源码

> 下表列的是第一跳应该先开的源码文件，不是这些功能的完整 ownership 边界。

| Example | 主线步骤 | 这个 example 刻意简化了什么 | 下一步先开哪些源码文件 |
|---|---|---|---|
| `l1_startup.py` | [Step 1 — 启动 / 模式分流](./source-map.md#step-1-startup-routing) | 把 CLI 参数解析、全局配置、runtime mode 分发压成一条启动骨架 | [`main.tsx`](../claudecode_src/src/main.tsx), [`setup.ts`](../claudecode_src/src/setup.ts), [`cli/print.ts`](../claudecode_src/src/cli/print.ts) |
| `l2_agent_loop.py` | [Step 2 — 进入 `query` / `queryLoop`](./source-map.md#step-2-enter-query-loop) | 把 QueryEngine、turn state、history 拼装收缩成最小单轮 loop | [`QueryEngine.ts`](../claudecode_src/src/QueryEngine.ts), [`query.ts`](../claudecode_src/src/query.ts) |
| `l3_tool_system.py` | [Step 3 — 模型产出 / 工具选择](./source-map.md#step-3-model-output-tool-selection) | 把真实工具池、schema、模式过滤压成少量工具定义与注册逻辑 | [`Tool.ts`](../claudecode_src/src/Tool.ts), [`tools.ts`](../claudecode_src/src/tools.ts), [`query.ts`](../claudecode_src/src/query.ts) |
| `l4_ui_ink.py` | [Step 6 — 状态 / UI 更新](./source-map.md#step-6-state-ui-update) | 把 Ink 组件树、状态切片、消息渲染缩成最小可视反馈回路 | [`bootstrap/state.ts`](../claudecode_src/src/bootstrap/state.ts), [`screens/REPL.tsx`](../claudecode_src/src/screens/REPL.tsx), [`components/Messages.tsx`](../claudecode_src/src/components/Messages.tsx) |
| `l5_state_commands.py` | [Step 6 — 状态 / UI 更新](./source-map.md#step-6-state-ui-update) | 把 pending message、命令分发、history 同步压成简化状态机 | [`screens/REPL.tsx`](../claudecode_src/src/screens/REPL.tsx), [`history.ts`](../claudecode_src/src/history.ts), [`commands/`](../claudecode_src/src/commands) |
| `l6_advanced.py` | [Step 3 — 模型产出 / 工具选择](./source-map.md#step-3-model-output-tool-selection) | 把多 agent / structured output 的真实边界压成“受控工具 + 受限 worker”示意 | [`tools/SyntheticOutputTool/`](../claudecode_src/src/tools/SyntheticOutputTool), [`coordinator/coordinatorMode.ts`](../claudecode_src/src/coordinator/coordinatorMode.ts), [`cli/print.ts`](../claudecode_src/src/cli/print.ts) |
| `l7_permissions.py` | [Step 4 — 工具执行](./source-map.md#step-4-tool-execution) | 把多层权限、自动批准、危险命令检查压成最小 gatekeeper | [`tools/BashTool/bashPermissions.ts`](../claudecode_src/src/tools/BashTool/bashPermissions.ts), [`tools/BashTool/bashSecurity.ts`](../claudecode_src/src/tools/BashTool/bashSecurity.ts), [`query.ts`](../claudecode_src/src/query.ts) |
| `l8_streaming.py` | [Step 3 — 模型产出 / 工具选择](./source-map.md#step-3-model-output-tool-selection) | 把 provider 事件流、chunk repair、stop reason 处理压成可读的 async generator 示例 | [`services/api/claude.ts`](../claudecode_src/src/services/api/claude.ts), [`query.ts`](../claudecode_src/src/query.ts) |
| `l9_context_mgmt.py` | [Step 7 — 下一轮 / 退出条件](./source-map.md#step-7-next-turn-or-exit) | 把 prompt cache、context trimming、memory extraction 压成”如何让多轮继续”这一条线 | [`constants/prompts.ts`](../claudecode_src/src/constants/prompts.ts), [`utils/context.ts`](../claudecode_src/src/utils/context.ts), [`memdir/memdir.ts`](../claudecode_src/src/memdir/memdir.ts), [`services/extractMemories/extractMemories.ts`](../claudecode_src/src/services/extractMemories/extractMemories.ts) |
| `l10_mcp.py` | 主线外扩展（工具注册层） | 把 MCP JSON-RPC 协议、McpClient、工具注册合并压成 in-process demo，去掉 stdio/SSE 通信 | [`tools/MCPTool/`](../claudecode_src/src/tools/MCPTool), [`services/mcp/`](../claudecode_src/src/services/mcp) |

## 怎么沿着桥继续走

1. 先用表格定位 example 对应的主线步骤。
2. 再打开该步骤对应的 [source-map](./source-map.md) 小节，核对输入 / 输出。
3. 然后只开表格里给你的 1 到 3 个源码文件，不要立刻散开。
4. 读完这些文件后，再决定要不要去对应 layer 或 [source-navigation](./source-navigation.md) 扩展搜索。

## 两条常用拼接路线

- `l1 -> l2 -> l8 -> l7 -> l4/l5 -> l9`：按一次请求真正流动的顺序读。
- `l3 -> l7 -> l6`：先抓工具与权限，再看受控多 agent 怎样挂回主线。
