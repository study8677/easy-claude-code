# Layer 9：Context Window 管理与 Prompt Cache

[English](./l9-context.en.md) | 中文

## 核心问题

Claude Code 如何在长对话里控制 context budget，同时尽量保住 prompt cache 命中率？

## 先运行

```bash
python examples/l9_context_mgmt.py
```

## 先看源码

- `utils/context.ts`
- `constants/prompts.ts`
- `utils/api.ts`
- `memdir/memdir.ts`

## 关键搜索词

- `SYSTEM_PROMPT_DYNAMIC_BOUNDARY`
- `context_1m_beta`
- `MEMORY.md`
- `ENTRYPOINT_NAME`

## 这一层要观察什么

- static / dynamic boundary 为什么重要
- snapshot 和 sticky latch 为什么能保护 cache
- auto-compact 和 memory index 分别在解决什么问题

## 示例和真实源码的差异

示例只演示 token 预算和 compact 思路。真实源码要同时兼顾模型窗口能力、缓存边界、系统提示词装配和 memory 注入规则。

## 看完后请回答

1. 为什么 prompt cache 命中率会反过来影响架构设计？
2. `MEMORY.md` 为什么必须保持短小且索引化？
3. auto-compact 解决的是“历史太长”，memory 解决的是什么？
