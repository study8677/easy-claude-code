# Layer 7：三层权限系统

[English](./l7-permissions.en.md) | 中文

## 核心问题

Claude Code 为什么把命令执行权限拆成“语义检查 -> 规则匹配 -> 询问用户”三层？

## 先运行

```bash
python examples/l7_permissions.py
```

## 先看源码

- `tools/BashTool/bashPermissions.ts`
- `tools/BashTool/bashSecurity.ts`

## 关键搜索词

- `BASH_SECURITY_CHECK_IDS`
- `canUseTool`
- `zmodload`
- `OBFUSCATED_FLAGS`

## 这一层要观察什么

- 哪些命令是“直接拒绝”，为什么不需要问用户
- 用户规则为什么要在语义检查之后
- 数字 ID 为什么比字符串名称更适合遥测和隐私

## 示例和真实源码的差异

示例只实现代表性的检查器。真实源码中检查器更多、边界条件更细，也更强调环境变量剥离与 shell 语义一致性。

## 看完后请回答

1. 为什么“每次都问用户”不是一个好的权限系统？
2. 为什么危险的 ZSH 模块要在当前 shell 不是 ZSH 时也拦截？
3. 第一层、第二层、第三层各自拦的是什么类型的问题？
