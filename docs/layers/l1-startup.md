# Layer 1：启动与入口

[English](./l1-startup.en.md) | 中文

## 核心问题

用户敲下 `claude` 后，Claude Code 先做了哪些初始化，再决定进入哪种模式？

## 先运行

```bash
python examples/l1_startup.py
python examples/l1_startup.py --print "hello"
python examples/l1_startup.py serve
```

## 先看源码

- `main.tsx`
- `setup.ts`
- `entrypoints/`
- `QueryEngine.ts`

## 关键搜索词

- `main_entry`
- `setup`
- `runHeadless`
- `serve`

## 这一层要观察什么

- 启动阶段为什么要打 checkpoint
- 配置、session、环境变量在哪一步建立
- 模式分流为什么发生在真正进入 agent loop 之前

## 示例和真实源码的差异

示例只保留了入口分流和初始化骨架。真实源码还会处理更多全局配置、模型能力、工具装配和 structured output 初始化。

## 看完后请回答

1. 启动路径和单轮 query 路径是在哪个阶段接上的？
2. 为什么 REPL、print、serve 是不同入口而不是同一个大函数里的分支？
3. 如果你要给 Claude Code 增加一种新模式，最可能改哪一层？
