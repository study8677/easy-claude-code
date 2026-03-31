# Layer 3：工具系统

[English](./l3-tool-system.en.md) | 中文

## 核心问题

Claude Code 是如何定义工具、注册工具，再把模型的工具调用分发到本地执行逻辑的？

## 先运行

```bash
python examples/l3_tool_system.py
```

## 先看源码

- `Tool.ts`
- `tools.ts`
- `tools/BashTool/`
- `tools/FileReadTool/`

## 关键搜索词

- `buildTool`
- `getTools`
- `inputSchema`
- `call`

## 这一层要观察什么

- 为什么模型只看到 schema 和 description
- 工具执行函数为什么不暴露给模型
- 工具注册和过滤为什么是单独一层

## 示例和真实源码的差异

示例只保留少量工具和简化权限。真实仓库有更复杂的工具上下文、UI 组件、错误处理和过滤逻辑。

## 看完后请回答

1. 为什么“工具 = schema + 函数”的边界特别重要？
2. 如果只改工具实现、不改 schema，会影响模型调用策略吗？
3. 工具注册表为什么比把逻辑散在各处更适合 Agent 系统？
