# P1：第一个小时

[English](./p1-first-hour.en.md) | 中文

## 适合谁

- 第一次看这个仓库的人
- 还不熟悉 Claude Code 启动链路的人
- 暂时没有 API Key 的人

## 预计时间

60-90 分钟

## 本阶段只搞懂什么

这一阶段只抓住请求真正进入系统前后的三件事：

1. Claude Code 如何决定当前进入哪种运行模式
2. `setup` 在真正进入 loop 之前完成了哪些初始化
3. 为什么这一步还不该陷入 tools / streaming / memory 的细节

## 你在主线中的位置

**主线位置：** 用户输入 → 启动 / 模式分流

这一页的任务不是追完整请求生命周期，而是把入口站稳：

- 命令行参数、工作目录、运行方式先决定当前要进入哪条运行面
- `setup` 把后续运行需要的基础环境准备好
- 只有这两步稳定了，后面的 `query` / `queryLoop` 才有可靠入口

如果你在这一页就一头扎进工具执行或 UI streaming，认知负担会立刻爆炸。

## 先跑哪个 example

先只把 `l1_startup.py` 跑透：

```bash
python examples/l1_startup.py
python examples/l1_startup.py --print "hello"
python examples/l1_startup.py serve
```

如果你想确认后面确实还有工具和 UI 层，可以只做预览：

```bash
python examples/l3_tool_system.py
python examples/l4_ui_ink.py
```

但这两个现在只用于建立“后面还有层”的直觉，不是这一阶段的主任务。

## 再读哪篇 layer

按这条顺序读：

1. [L1 启动与入口](../layers/l1-startup.md)
2. [源码导图：启动路径](../source-map.md#1-启动路径)
3. [example 到源码的桥接页：l1](../example-source-bridge.md)

如果你只是想知道后面还会发生什么，可以快速预览：

- [L3 工具系统](../layers/l3-tool-system.md)
- [L4 UI / Ink](../layers/l4-ui-ink.md)

## 再开哪些源码文件

这一阶段先只开最贴近入口的两个文件：

- `claudecode_src/src/main.tsx` —— 看 CLI 参数和模式分流如何进入不同运行面
- `claudecode_src/src/setup.ts` —— 看真正进入 loop 之前做了哪些初始化

如果你在搜索时看到 `runHeadless`、`serve`、`REPL`，先把它们当成“分流结果”，不要立刻展开到后面所有实现。

## 这一阶段先不要看什么

现在先主动忽略这些主题：

- 工具系统的完整注册与执行细节
- `query` / `queryLoop` 的完整单轮主循环
- streaming 事件实现
- memory、prompt cache、multi-agent
- REPL 里的细粒度状态组织

这一页的任务是降低认知负担：先把“请求如何进入系统”这根骨架立起来。

## 必搜符号

这一阶段先只搜这 4 个：

- `main_entry`
- `setup`
- `runHeadless`
- `serve`

如果你状态很好，再补搜：

- `buildTool`
- `REPL`

## 这一阶段只回答三个问题

1. Claude Code 在哪里决定进入 REPL、print、serve 等不同运行面？
2. 为什么模式分流必须发生在真正进入 agent loop 之前？
3. `setup.ts` 这类初始化逻辑，为什么不应该散落在后续执行链里？

## 跑完 example 之后下一步怎么接源码

先这样接：

1. 看 [source-map 的启动路径](../source-map.md#1-启动路径)
2. 用 [source-navigation](../source-navigation.md) 里的搜索方式搜 `main_entry` / `setup`
3. 先开 `main.tsx` 和 `setup.ts`

如果你想更细一点，直接看：

- [example 到源码的桥接页](../example-source-bridge.md)

## 完成标准

完成这一页时，你应该能：

- 说清启动入口、初始化、模式分流三者各自负责什么
- 在源码里搜到上面的关键符号
- 用自己的话解释“Claude Code 为什么不是一个单文件脚本”
- 明确知道现在还不该深入 tools / streaming / memory

如果做不到，先回去重看：

- `L1`，如果你还分不清 REPL / print / serve
- `source-map` 的启动路径，如果你还串不起入口调用链

## 没有 API Key 怎么办

这一页默认就是无 API 路线，可以完整做完。

## 下一步

继续去 [P2 Core Loop](./p2-core-loop.md)
