# Claude Code 设计哲学：源码背后的思考

[English](./PHILOSOPHY_EN.MD) | 中文

> 读懂一行代码容易，读懂它为什么这样写才难。
> 本文从源码中提炼出 Claude Code 的核心设计决策，以及每个决策背后的理由。

---

## 目录

1. [第一原则：可逆性优先](#一可逆性优先measure-twice-cut-once)
2. [Generator 作为核心抽象](#二generator-作为核心抽象)
3. [三层权限模型](#三三层权限模型)
4. [错误不一定要立刻暴露](#四错误不一定要立刻暴露withholding-errors)
5. [缓存稳定性是一等公民](#五缓存稳定性是一等公民)
6. [记忆是索引，不是内容](#六记忆是索引不是内容)
7. [协调者不窥视](#七协调者不窥视coordinator-never-peeks)
8. [全局状态要克制](#八全局状态要克制)
9. [工具是 Schema + 函数的二元组](#九工具是-schema--函数的二元组)
10. [数字 ID 优于字符串名称](#十数字-id-优于字符串名称)

---

## 一、可逆性优先：Measure Twice, Cut Once

**源码位置**：`src/prompts.ts`（系统 Prompt）

这是 Claude Code 最核心的行为准则，也是最容易被忽视的一条。

从系统 Prompt 里摘出来的原话（大意）：

> 操作越难撤销、影响范围越广，就越要在执行前停下来确认。
> 本地的、可逆的操作可以直接做；
> 影响共享系统、难以撤销的操作，默认要先告知用户并等待确认。

**具体体现**：
- 删除文件前会问：`是否删除 foo.txt？`
- Force push 会警告：`这会覆盖远端历史，确定吗？`
- 发送邮件/消息：每次都确认，即使用户之前批准过

**为什么这样设计？**

AI Agent 犯错的代价是不对称的：
- 漏掉一次确认 = 用户丢了工作，很难找回
- 多一次确认 = 用户多按一次 y，几秒钟

这是有意识的产品决策：**宁可多一次打扰，不冒一次不可逆的风险**。

**值得学习的点**：当你构建自己的 Agent 时，这个原则应该比功能完整性更优先。

---

## 二、Generator 作为核心抽象

**源码位置**：`src/query.ts`（`async function* query()`，`async function* queryLoop()`）

Claude Code 的整个 Agent Loop 是一个 **async generator function**，
而不是普通的 async function，也不是回调。

```typescript
// query.ts（简化版）
export async function* query(params): AsyncGenerator<QueryEvent> {
  yield { type: 'stream_request_start' }
  yield* processStream(stream)    // 委托给子 generator！
  yield { type: 'tool_result', ... }
  if (done) return
}
```

**为什么不用 Promise？**

```
Promise:    一次性，只能 await 一个最终结果
Callback:   每个事件注册回调，难以组合，状态分散
Generator:  可以 yield 任意多次，可以 yield* 委托，可以 return 取消
```

Generator 满足了 Agent Loop 的三个同时需要的特性：
1. **流式**：`yield { type: 'text', text: chunk }` 边生成边给 UI
2. **可取消**：调用方调用 `.return()` 或检测 `AbortSignal`，generator 立即停止
3. **可组合**：`yield*` 可以把子 Agent 的事件流直接透传给父 Agent

**`yield*` 的威力**（最容易被忽视）：

```typescript
// 子 Agent 的事件可以直接穿透到顶层 UI
async function* parentAgent() {
  yield* childAgent(subtask)   // 子 Agent 的所有事件都被转发
  yield { type: 'parent_done' }
}
```

这使得多层 Agent 嵌套（coordinator → worker → sub-worker）的事件可以不经中转直接到达 UI，保持响应性。

---

## 三、三层权限模型

**源码位置**：`src/tools/BashTool/bashPermissions.ts`，`src/tools/BashTool/bashSecurity.ts`

Claude Code 在执行任何命令前经过三道检查，从快到慢：

```
第一层：语义安全检查（毫秒级，静态分析）
  → 23 个检查器，每个有数字 ID
  → fork bomb、危险 rm、ZSH 危险模块、混淆 flag...
  → 命中 → 直接拒绝，不问用户，不留日志

第二层：权限规则（微秒级，字符串匹配）
  → 用户定义的 Allow/Deny 规则
  → Bash(git commit:*)、Bash(npm publish)...
  → 命中 → 直接放行或拒绝，不打扰用户

第三层：询问用户（秒级，I/O 等待）
  → 前两层都没命中
  → 展示命令，同时建议一条规则
  → 用户确认后执行
```

**三个关键设计决策**：

**① 数字 ID 而非字符串名称**（见第十节详述）
安全检查器的 ID 是数字（1, 4, 5, 8, 20...），方便遥测统计，不暴露命令内容。

**② 环境变量剥离**
规则匹配前，先去掉 `KEY=VAL` 前缀：
```
NODE_ENV=prod npm run build  →  匹配规则 "npm run:*"
```
这和 bash 的执行语义一致，防止用户必须为每种环境变量组合都写规则。

**③ ZSH 模块被拦截，即使不执行 ZSH**
`zmodload`、`sysread`、`ztcp` 等 ZSH 专属危险模块被列为第一层拦截。
为什么？**防御未来变化**——如果未来 Claude Code 开始支持 ZSH 执行，安全检查已经就位。

---

## 四、错误不一定要立刻暴露（Withholding Errors）

**源码位置**：`src/query.ts`（`isWithheldMaxOutputTokens()`）

这是整个代码库里最"反直觉"的设计，源码注释说这是"一整天的调试和拔头发"的经验总结。

**问题**：当 Claude API 返回 `max_output_tokens` 错误时，
QueryEngine 会尝试升级 token 上限并重试。
但是，SDK 调用方（比如 CI/CD 流水线）看到任何 `error` 字段都可能直接终止会话。

**解决方案**：中间错误先被"扣押"（withheld），不暴露给外部。
等恢复逻辑运行完，确认是否成功，再决定要不要暴露错误。

```typescript
// 简化版逻辑
if (event.type === 'error' && isMaxOutputTokens(event)) {
  withheldError = event  // 先扣押
  if (await tryRecovery()) {
    withheldError = null  // 恢复成功，丢弃错误
  } else {
    yield withheldError  // 恢复失败，现在暴露
  }
}
```

**更广泛的启示**：在构建分布式系统时，"先恢复，再上报"往往比"立刻上报，让调用方处理"更能提高系统稳定性。

---

## 五、缓存稳定性是一等公民

**源码位置**：`src/utils/context.ts`，`src/QueryEngine.ts`，`src/systemPromptSections.ts`

Claude Code 的系统 Prompt 有 50,000~70,000 token。
如果每次 API 调用都重新计算这些 token，费用会翻倍。

**Anthropic 的 Prompt Cache** 可以把这部分的费用降低 90%，
但前提是：**每次调用的系统 Prompt 前缀必须完全一致**。

为此，Claude Code 做了三件事：

**① 静态/动态边界（`SYSTEM_PROMPT_DYNAMIC_BOUNDARY`）**
```
系统 Prompt 前半部分（角色、规则、工具说明）→ 永远不变，跨用户缓存
─────────────── 边界 ───────────────────────
系统 Prompt 后半部分（用户名、cwd、当前时间）→ 每次更新
```

**② 一次性快照（One-Time Snapshot）**
Beta header、feature gate 状态、模型选择在 `QueryEngine` 启动时快照一次，
整个会话期间不再重新读取，即使全局配置发生变化。
原因：中途改变这些值会让系统 Prompt 前缀产生差异，busting 缓存。

**③ Sticky Latch（粘性锁存）**
Fast Mode 一旦激活，对应的 beta header 就"锁定"，不再切换。
即使用户随后关闭了 Fast Mode，header 也保持不变直到会话结束。
原因：同上，保持缓存稳定。

**工程洞见**：Prompt Cache 命中率是 Claude Code 成本的核心指标，
架构上的每一个决策都要问："这会影响缓存命中率吗？"

---

## 六、记忆是索引，不是内容

**源码位置**：`src/memdir/memdir.ts`

Claude Code 的持久化记忆系统（`/memory` 功能）有一个精妙的设计：

```
MEMORY.md          ← 索引文件，≤200 行，永远被加载
  - `user_role.md` — 用户是一名后端工程师
  - `project_ctx.md` — 项目是 teamo-router

user_role.md       ← 内容文件，有 frontmatter，按需加载
project_ctx.md     ← 内容文件，有 frontmatter，按需加载
```

**为什么分开？**

- `MEMORY.md` 每次都加载，但只有几百行 → 消耗少
- 内容文件只有相关时才加载 → 按需消耗
- 强制分离迫使写记忆的人提炼关键词，而不是把一大段文本塞进去

**四种记忆类型**（有意识的类型系统）：
```
user     → 关于用户的信息（角色、喜好、技能）
feedback → 关于工作方式的反馈（避免/重复的行为）
project  → 关于当前项目的信息（目标、截止日期、决策）
reference → 外部资源的指针（Linear 项目、Grafana 仪表盘）
```

**明确排除的内容**（防止记忆腐烂）：
- 代码模式、架构、文件路径 → 直接读代码
- git 历史 → `git log` 是权威来源
- 调试解决方案 → fix 在代码里，commit message 有上下文
- 临时任务状态 → 会话结束就无效了

这个设计的核心思想：**记忆只存储无法从其他来源获取的信息**。

---

## 七、协调者不窥视（Coordinator Never Peeks）

**源码位置**：`src/coordinator/coordinatorMode.ts`，`src/tools/AgentTool/`

当 Claude Code 以 coordinator 模式运行时，它会生成多个 worker Agent 并行处理任务。
这里有一条不成文但严格遵守的规则：**coordinator 不查看 worker 的中间状态**。

```
coordinator Agent
  ├─ 生成 worker 1（任务：读文件分析依赖）→ 等待 SyntheticOutputTool
  ├─ 生成 worker 2（任务：运行测试）→ 等待 SyntheticOutputTool
  └─ 等所有 worker 完成后，汇总结果
```

每个 worker 只有**受限的工具集**，防止子任务越权。
每个 worker 完成后调用 `SyntheticOutputTool` 返回结果，coordinator 读取这个结果。

**为什么不让 coordinator 实时查看 worker 进度？**

1. **隔离性**：worker 可以并行运行，coordinator 不需要串行等待
2. **简单性**：coordinator 的逻辑不依赖于 worker 的实现细节
3. **可替换性**：可以换一个更好的 worker 实现而不影响 coordinator

**值得类比的系统**：这和 Unix 的进程模型很像——父进程不直接读取子进程的内存，只通过 `exit code` 和 `stdout/stderr` 通信。

---

## 八、全局状态要克制

**源码位置**：`src/bootstrap/state.ts`

`bootstrap/state.ts` 是整个项目唯一的全局状态单例。
文件里有一行注释写得非常直接：

```typescript
// DO NOT ADD MORE STATE HERE - BE JUDICIOUS WITH GLOBAL STATE
```

**这里存的东西**（每一项都有充分理由）：
- Session ID（全局唯一标识符）
- API 遥测（token 计数、费用、耗时）
- 模型用量（按模型分类统计）
- 粘性锁存（Fast Mode、beta header）
- Session 创建的 Teams（退出时清理）

**不在这里的东西**（同样重要）：
- 消息历史 → 在 `QueryEngine` 的局部变量里
- UI 状态 → 在 React 组件的 state 里
- 工具配置 → 在 `ToolUseContext` 里（每次查询创建新的）

**工程启示**：全局状态是"债务"——你每增加一项，就让系统更难测试、更难推理。
Claude Code 的全局状态量极少，即使是有几万行 TypeScript 的大型项目。

---

## 九、工具是 Schema + 函数的二元组

**源码位置**：`src/Tool.ts`，`src/tools/*/`

这个设计看起来简单，但背后的区分非常重要：

```typescript
type ToolDef = {
  name: string
  description: string
  inputSchema: JSONSchema     // 给模型看：模型用这个决定怎么调用
  call(input, context): ToolResult  // 给运行时：在本地执行，模型不知道实现
}
```

**Schema 和实现完全分离**意味着：

1. **模型永远看不到工具的实现代码**——只能看到 description 和 schema
2. **你可以随时换掉实现**——只要 schema 不变，模型行为不受影响
3. **Schema 是契约**——你必须认真写 description，这直接影响模型的调用质量

**高质量 description 的重要性**：

BashTool 的 description 有几百个字，详细说明了：
- 什么情况下用
- 有哪些限制
- 什么时候应该用其他工具代替

这不是偶然的——模型的每一个工具选择，都依赖于 description 的质量。

---

## 十、数字 ID 优于字符串名称

**源码位置**：`src/tools/BashTool/bashSecurity.ts`（`BASH_SECURITY_CHECK_IDS`）

```typescript
const BASH_SECURITY_CHECK_IDS = {
  INCOMPLETE_COMMANDS: 1,
  JQ_SYSTEM_FUNCTION: 2,
  OBFUSCATED_FLAGS: 4,
  SHELL_METACHARACTERS: 5,
  DANGEROUS_PATTERNS_COMMAND_SUBSTITUTION: 8,
  ZSH_DANGEROUS_COMMANDS: 20,
  // ...
}
```

为什么用数字而不是字符串？

1. **遥测效率**：发送 `{ check_id: 8 }` 比 `{ check: "DANGEROUS_PATTERNS_COMMAND_SUBSTITUTION" }` 便宜得多
2. **防止日志泄露**：数字 ID 不包含被检查的命令内容，不会把用户命令暴露在日志里
3. **稳定性**：数字 ID 不受重命名影响，跨版本的遥测数据可以对比

**更广泛的应用**：这个模式在任何需要高频发送、长期追踪的事件系统里都值得借鉴。

---

## 总结：Claude Code 的设计信念

通读源码，可以提炼出几条核心信念：

| 信念 | 体现 |
|------|------|
| **安全是架构问题，不是功能问题** | 权限检查在 Tool 层，不在调用层 |
| **错误恢复优于错误上报** | Withheld errors + recovery loop |
| **缓存命中率是一等公民** | 静态边界、一次性快照、sticky latch |
| **组合优于继承** | `yield*` 委托、Tool 注册表 |
| **约束激发创造力** | 全局状态极少、记忆有类型限制 |
| **透明胜过聪明** | 宁可多问一次，不冒不可逆的险 |

这些不只是 Claude Code 的设计原则——也是构建任何 AI Agent 系统时值得深思的问题。

---

*本文基于 Claude Code 源码分析整理，每一节都可以在 `claudecode_src/src/` 中找到对应代码。*
