# Claude Code 教程 FAQ

[English](./faq.en.md) | 中文

## 1. 我不懂 TypeScript，能读这个仓库吗？

可以。先跑 `examples/` 建立直觉，再看 `docs/layers/`。目标不是一上来读懂所有语法，而是先知道每个模块在解决什么问题。

## 2. 我没有 API Key，哪些内容还能学？

可以先学 `l1`、`l3`、`l4`、`l5`、`l6`、`l7`、`l9`。`l2` 和 `l8` 没 key 时，先看对应 layer 文档和 source map，再去源码里搜关键符号。

## 3. 为什么不直接把源码按文件顺序讲完？

因为 Claude Code 不是按目录结构设计给读者看的。更有效的方式是按“问题 -> 调用链 -> 设计决策”来读。

## 4. 先看 QueryEngine，还是先看 query.ts？

初学者先看 `query.ts`，先理解 loop。进阶读者再去 `QueryEngine.ts`，理解系统 Prompt、skills、plugins、slash commands 如何在进入 loop 前被组装。

## 5. 为什么仓库里既有 9 层，又有 L10-L15？

前 9 层是“有示例支撑的课程主线”。L10-L15 是“源码专题深挖”，主要服务已经进入源码阅读阶段的读者。

## 6. 这个仓库的最佳阅读方式是什么？

先跑一个 example，再读对应 layer 文档，然后去 `claudecode_src/src/` 搜里面列出的关键符号。不要先把源码从头翻到尾。如果你容易在源码里迷路，直接配合 [源码导航手册](./source-navigation.md) 一起看。

## 7. 想把“看懂”变成“真的会分析”，应该做什么？

去做 [学习练习册](./exercises.md)。它要求你写出搜索过的符号、看过的文件和自己的结论，这比只看文档更能暴露理解漏洞。
