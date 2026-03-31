# Agent Handoff Document — easy-claude-code

## 项目定位

这是一个 **Claude Code 源码学习仓库**。目标是帮助开发者通过可运行的 Python 示例 + 设计哲学文档，系统性地读懂 Claude Code 的 TypeScript 源码。

GitHub 地址：https://github.com/study8677/easy-claude-code

---

## 仓库结构（当前状态）

```
easy_claude_code/
├── README.MD                  # 中文主 README（学习路线入口）
├── README_EN.MD               # 英文 README
├── PHILOSOPHY.MD              # Claude Code 设计哲学（10节深度解析）
├── PHILOSOPHY_EN.MD           # 英文版设计哲学
├── .gitignore                 # claudecode_src/ 已排除，不上传
│
├── examples/                  # 9 个可运行的 Python 示例
│   ├── l1_startup.py          # Layer 1：启动与入口（main.tsx + setup.ts）
│   ├── l2_agent_loop.py       # Layer 2：Agent 核心循环（query.ts）★需要API Key
│   ├── l3_tool_system.py      # Layer 3：工具系统（Tool.ts + tools/）
│   ├── l4_ui_ink.py           # Layer 4：UI 层 Ink/React（含 spinner 动画）
│   ├── l5_state_commands.py   # Layer 5：状态管理 & 斜杠命令
│   ├── l6_advanced.py         # Layer 6：技能 / 多Agent / 费用追踪
│   ├── l7_permissions.py      # Layer 7：三层权限系统（bashPermissions.ts）
│   ├── l8_streaming.py        # Layer 8：Async Generator 流式架构 ★需要API Key
│   └── l9_context_mgmt.py     # Layer 9：Context Window 管理 & Prompt Cache
│
├── docs/
│   ├── source-map.md          # 中文源码导图（调用链入口）
│   ├── source-map.en.md       # 英文源码导图
│   ├── layers/                # 9 层双语深挖文档
│   └── articles/              # 双语文章选题路线
│
└── claudecode_src/            # Claude Code TypeScript 源码（本地，已 gitignore）
    ├── src/                   # 主源码目录
    └── vendor/                # Native 模块（音频、图像等）
```

---

## 各示例对应的源码文件

| 示例文件 | 对应源码 | 核心内容 | 需要 API Key |
|---------|---------|---------|------------|
| `l1_startup.py` | `src/main.tsx`, `src/setup.ts`, `src/entrypoints/` | CLI 启动 + 模式分流 | 否 |
| `l2_agent_loop.py` | `src/query.ts` line 307 `while(true)` | Agent Loop 核心循环 | 是 |
| `l3_tool_system.py` | `src/Tool.ts`, `src/tools.ts`, `src/tools/BashTool/` | 工具注册表 + 分发 | 否 |
| `l4_ui_ink.py` | `src/components/App.tsx`, `src/ink.ts` | 状态驱动终端渲染 | 否 |
| `l5_state_commands.py` | `src/state/AppStateStore.ts`, `src/commands/` | 不可变状态 + 斜杠命令 | 否 |
| `l6_advanced.py` | `src/skills/`, `src/coordinator/`, `src/cost-tracker.ts` | 技能/多Agent/费用 | 否 |
| `l7_permissions.py` | `src/tools/BashTool/bashPermissions.ts`, `bashSecurity.ts` | 三层权限（语义→规则→询问）| 否 |
| `l8_streaming.py` | `src/query.ts`（async generator + yield* 委托）| 流式事件架构 | 是 |
| `l9_context_mgmt.py` | `src/utils/context.ts`, `src/constants/prompts.ts` | Context 监控 + Prompt Cache | 否 |

---

## 已验证的源码事实（可直接引用）

以下内容均已在源码中核实：

- `query.ts` 第 219 行：`export async function* query()`
- `query.ts` 第 241 行：`async function* queryLoop()`
- `query.ts` 第 307 行：`while (true)` — Agent Loop 所在
- `bashSecurity.ts`：恰好 **23 个**安全检查器（唯一 ID 枚举，已全部列出）
- `bootstrap/state.ts` 第 31 行：`// DO NOT ADD MORE STATE HERE - BE JUDICIOUS WITH GLOBAL STATE`
- `bootstrap/state.ts` 第 226-233 行：Sticky-on latch（AFK_MODE / FAST_MODE），注释原文提到 `~50-70K token prompt cache`
- `constants/prompts.ts` 第 114-115 行：`SYSTEM_PROMPT_DYNAMIC_BOUNDARY`
- `constants/prompts.ts` 第 258 行："reversibility and blast radius"（原文引用）
- `query.ts` 第 175 行：`isWithheldMaxOutputTokens()` — 错误扣押机制
- `memdir/memdir.ts` 第 189 行：四类型记忆（user / feedback / project / reference）
- `memdir/memdir.ts` 第 34-37 行：MEMORY.md 200 行 + 字节限制
- `coordinator/coordinatorMode.ts` 第 2、13、88-97 行：ASYNC_AGENT_ALLOWED_TOOLS + SyntheticOutputTool

---

## PHILOSOPHY.MD 的 10 个主题

1. **可逆性优先**（reversibility and blast radius）— 源自 `constants/prompts.ts`
2. **Generator 作为核心抽象** — `async function*` + `yield*` 委托
3. **三层权限模型** — 语义拒绝 → 规则匹配 → 询问用户
4. **错误不一定立刻暴露** — `isWithheldMaxOutputTokens` 机制
5. **缓存稳定性是一等公民** — 静态/动态边界 + sticky latch
6. **记忆是索引，不是内容** — MEMORY.md 分离设计
7. **协调者不窥视** — coordinator 只读 SyntheticOutput，不看中间状态
8. **全局状态要克制** — `bootstrap/state.ts` 里那行注释
9. **工具是 Schema + 函数的二元组** — 模型看 schema，运行时执行函数
10. **数字 ID 优于字符串名称** — 23 个安全检查器的数字 ID 设计

---

## 约束与规则

- `claudecode_src/` 已在 `.gitignore` 中，**绝对不能提交到 GitHub**
- README 中**不能出现"泄漏/leaked"等字眼**，用"源码研究"替代
- 免责声明保留在 README 底部
- 示例文件默认使用 DeepSeek API（OpenAI 兼容），环境变量 `DEEPSEEK_API_KEY`
- 语言风格：面向初学者，每个示例文件顶部有详细 docstring 说明对应源码位置

---

## 潜在的后续工作方向

以下是还可以继续做的事情，供接手的 Agent 参考：

1. **补全 Layer 2 / Layer 8 的示例**：这两个需要 API Key，可以加入模拟模式（不调用真实 API）让初学者也能跑起来
2. **添加 `examples/l10_mcp.py`**：MCP 协议是 Claude Code 扩展工具的方式，还没有专门示例
3. **添加源码阅读笔记**：为 `claudecode_src/src/` 的关键文件加内联注释，帮助阅读（本地文件，不上传）
4. **制作学习路线图**：用 Mermaid 图把 9 层学习路线和对应源码文件画出来，放进 README
5. **增加"常见问题"部分**：整理初学者读源码时最容易卡住的地方
6. **补更深的源码主题**：例如 QueryEngine / API streaming / REPL / MCP-Hooks / Bridge 模式

---

## 运行环境

```bash
pip install openai python-dotenv

# DeepSeek（推荐）
export DEEPSEEK_API_KEY=你的key

# 或 Anthropic
export ANTHROPIC_API_KEY=你的key
```

需要 API Key 的文件：`l2_agent_loop.py`、`l8_streaming.py`

其余示例无需 API Key，直接 `python examples/lX_xxx.py` 运行。

---

## Git 状态

- 主分支：`main`
- 远端：`https://github.com/study8677/easy-claude-code.git`
- 当前工作区：干净，无未提交改动
- 最近三次提交：
  - `ec83226` add layers 7-9 examples + PHILOSOPHY.MD design deep-dive
  - `29456d2` add 6-layer examples + rewrite READMEs as beginner learning guide
  - `7dceef5` reposition repo as Claude Code source code study roadmap
