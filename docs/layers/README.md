# Layer 深挖目录

[English](./README.en.md) | 中文

如果你要按阶段学习，优先去 [学习路径页](../paths/README.md)。`docs/layers/` 更适合当参考资料和回查索引。

如果你刚跑完 `examples/`，可以把这份目录当成“例子 -> 概念 -> 源码”的中间站：先对照 layer 文档建立直觉，再去 [源码导图](../source-map.md) 选调用链，最后用 [源码导航手册](../source-navigation.md) 找到具体符号。

如果你已经在读源码，可以直接把这份目录当索引来回查；L10-L15 更偏向已经进入实现细节的读者。

按顺序阅读：

1. [L1 启动与入口](./l1-startup.md)
2. [L2 Agent 核心循环](./l2-agent-loop.md)
3. [L3 工具系统](./l3-tool-system.md)
4. [L4 UI / Ink](./l4-ui-ink.md)
5. [L5 状态与命令](./l5-state-commands.md)
6. [L6 高级机制](./l6-advanced.md)
7. [L7 权限系统](./l7-permissions.md)
8. [L8 Streaming](./l8-streaming.md)
9. [L9 Context 管理](./l9-context.md)

进阶专题：

10. [L10 QueryEngine 与系统 Prompt 拼装](./l10-query-engine.md)
11. [L11 API Streaming 与事件模型](./l11-api-streaming.md)
12. [L12 REPL 主界面与输入系统](./l12-repl-ui.md)
13. [L13 MCP / Hooks / Plugins 扩展面](./l13-mcp-hooks-plugins.md)
14. [L14 Memory 提取与 Team Memory](./l14-memory-system.md)
15. [L15 Print / Serve / Bridge 等运行模式](./l15-runtime-modes.md)

建议搭配：

- [学习路径](../paths/README.md)
- [源码导图](../source-map.md)
- [源码导航手册](../source-navigation.md)
- [设计哲学](../../PHILOSOPHY.MD)
