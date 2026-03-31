# Layer 6：高级机制

[English](./l6-advanced.en.md) | 中文

## 核心问题

Claude Code 如何在主循环之外扩展出技能、多 Agent、记忆和费用统计这些“产品层能力”？

## 先运行

```bash
python examples/l6_advanced.py
```

## 先看源码

- `skills/`
- `coordinator/`
- `tools/AgentTool/`
- `tools/SyntheticOutputTool/`
- `memdir/`
- `cost-tracker.ts`

## 关键搜索词

- `SYNTHETIC_OUTPUT_TOOL_NAME`
- `createSyntheticOutputTool`
- `MEMORY.md`
- `cost`

## 这一层要观察什么

- 什么能力是“复用 prompt”的产品机制
- 多 Agent 的边界是如何被 structured output 固化的
- 记忆为什么是索引系统而不是日志堆积

## 示例和真实源码的差异

示例把多个高级特性压缩到一个文件里。真实源码中这些能力彼此解耦，但会在会话级 orchestration 中相互协作。

## 看完后请回答

1. 技能、工具、命令之间的边界分别是什么？
2. 为什么 coordinator 不该直接窥视 worker 中间状态？
3. 为什么 memory 更接近“目录索引”而不是“长期聊天记录”？
