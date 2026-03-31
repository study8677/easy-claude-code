# Claude Code 深度解析

[English](./README_EN.MD) | 中文

> 最系统的 Claude Code 源码阅读指南 — 从启动入口到多 Agent 协调，每一层都有可运行的示例。

---

## 这是什么

本仓库收录了 Claude Code 的 TypeScript 源码（`claudecode_src/`，已加入 `.gitignore` 仅供本地研究），并整理了一份**6 层递进的源码学习路线**。

每一层都附有：
- 核心问题与关键文件
- 对应的可运行 Python 示例（`examples/` 目录）
- 源码关键片段解读

```
claudecode_src/src/       ← TypeScript 源码（本地，不上传）
examples/                 ← 6 个可运行的 Python 示例
├── l1_startup.py         ← 启动与入口
├── l2_agent_loop.py      ← Agent 核心循环 ★
├── l3_tool_system.py     ← 工具系统
├── l4_ui_ink.py          ← UI 层
├── l5_state_commands.py  ← 状态管理 & 斜杠命令
└── l6_advanced.py        ← 技能 / 多Agent / 费用追踪
v1_basic_agent.py         ← 完整 Agent（200行，推荐热身）
v2_async_agent.py         ← 异步版 Agent
```

---

## 快速热身（5 分钟）

在读源码之前，先跑一遍这个 200 行的简化版，建立直觉：

```bash
pip install openai python-dotenv
export DEEPSEEK_API_KEY=你的key

python v1_basic_agent.py
# 试着输入：列出当前目录
# 试着输入：读取 README.MD 前 20 行
# 试着输入：创建 hello.txt 写入 "hello world"
```

跑完以后你已经理解了 Claude Code 70% 的核心机制。剩下的在源码里。

---

## 6 层学习路线

### Layer 1 — 启动与入口
**核心文件**：`main.tsx` · `entrypoints/` · `setup.ts`

**核心问题**：`claude` 命令敲下去后，真正发生了什么？

Claude Code 启动时做三件事，然后才进入你看到的 REPL：

```python
# l1_startup.py 的核心（对应 main.tsx + setup.ts）

def startup_checkpoint(name):
    # Claude Code 在每个启动阶段打时间戳，追踪耗时
    print(f"[{name}] +{elapsed_ms:.1f}ms")

def main():
    startup_checkpoint("main_entry")   # profileCheckpoint('main_tsx_entry')
    config = load_config()             # setup.ts：读取配置、检测 API Key
    session_id = setup(config)         # 生成 session_id，注入环境变量
    startup_checkpoint("ready")

    # 根据参数分流（对应 entrypoints/ 目录）
    if "--print" in sys.argv:          # claude --print "..." → 执行后退出
        run_non_interactive(prompt)
    elif "serve" in sys.argv:          # claude serve → HTTP 服务器
        run_server_mode()
    else:                              # claude → 交互式 REPL
        run_interactive_repl()
```

> 运行示例：`python examples/l1_startup.py`
> 对应源码：`claudecode_src/src/main.tsx`，`claudecode_src/src/setup.ts`

---

### Layer 2 — Agent 核心循环 ★
**核心文件**：`query.ts` · `QueryEngine.ts` · `Task.ts`

**核心问题**：Claude Code 怎么一直循环调用工具直到任务完成？

这是整个 Claude Code 的心脏，所有其他代码都是围绕它的脚手架：

```python
# l2_agent_loop.py 的核心（对应 query.ts 的 async function* queryLoop()）

def query_loop(messages):
    while True:                          # ← query.ts line 307: while (true)

        response = call_model(messages)
        reply = response.choices[0].message

        if not reply.tool_calls:
            return reply.content         # 模型说"做完了" → 退出循环

        # 执行工具调用，追加结果，继续循环
        messages.append(assistant_msg(reply))
        for tc in reply.tool_calls:
            result = run_tool(tc.function.name, tc.function.arguments)
            messages.append(tool_result(tc.id, result))
        # ↑ 就这么简单：把结果塞回历史，模型下一轮能看到
```

真实 `query.ts` 里这个循环是 `async generator function*`，所以可以用 `yield` 流式吐出每一步的事件（`stream_request_start` · `tool_use` · `tool_result` · `done`），让 UI 实时响应。

> 运行示例：`python examples/l2_agent_loop.py`（需要 API Key）
> 对应源码：`claudecode_src/src/query.ts`，搜索 `while (true)`

---

### Layer 3 — 工具系统
**核心文件**：`Tool.ts` · `tools.ts` · `tools/BashTool/` · `tools/FileReadTool/` · ...

**核心问题**：Claude Code 内置了哪些工具？每个是怎么实现的？

工具 = **JSON Schema（给模型）+ 函数（在本地执行）**，就这么简单：

```python
# l3_tool_system.py 的核心（对应 Tool.ts 的 ToolDef + buildTool()）

@dataclass
class ToolDef:
    name: str
    description: str
    schema: dict       # ← 这一份发给模型（模型看到的全部）
    execute: Callable  # ← 这一份在你的电脑上跑（模型看不到）
    needs_permission: bool = False

# 注册表（对应 tools.ts 的 getTools()）
TOOL_REGISTRY = {
    "bash":       ToolDef("bash",      "执行 shell 命令", bash_schema,  run_bash,   needs_permission=True),
    "read_file":  ToolDef("read_file", "读取文件",        read_schema,  read_file,  needs_permission=False),
    "write_file": ToolDef("write_file","写入文件",        write_schema, write_file, needs_permission=True),
    "edit_file":  ToolDef("edit_file", "精确编辑文件",    edit_schema,  edit_file,  needs_permission=True),
}

def dispatch(name, args):
    tool = TOOL_REGISTRY[name]
    if tool.needs_permission and not ask_permission(name, args):
        return "用户拒绝了权限请求"
    return tool.execute(args)   # ← Tool.ts 里的 call()
```

Claude Code 实际有 **30+ 个工具**，`tools/` 目录下每个子目录就是一个工具的完整实现（包括 UI 组件、权限检查、错误处理）。

> 运行示例：`python examples/l3_tool_system.py`（无需 API Key）
> 对应源码：`claudecode_src/src/Tool.ts`，`claudecode_src/src/tools/BashTool/BashTool.tsx`

---

### Layer 4 — UI 层（Ink/React）
**核心文件**：`components/App.tsx` · `components/AgentProgressLine.tsx` · `outputStyles/` · `ink.ts`

**核心问题**：命令行里的 spinner、进度条、彩色输出是怎么渲染的？

Claude Code 用 **Ink** 框架在终端里跑 React 组件树。核心思想：`UI = f(state)`，状态变了自动重渲染：

```python
# l4_ui_ink.py 的核心（模拟 Ink 的状态驱动渲染）

@dataclass
class UIState:
    messages: list        # 消息历史
    active_tool: str      # 正在执行的工具
    spinner_frame: int    # 动画帧
    cost_usd: float       # 费用

def render(state: UIState):
    """
    纯函数：相同的 state → 相同的终端输出。
    Ink 的 React reconciler 计算 diff，只更新变化的部分。
    这就是 spinner 动画 + 历史消息同时存在的原因。
    """
    clear_screen()
    for msg in state.messages[-8:]:
        print_message(msg)                 # MessageList.tsx
    if state.active_tool:
        print(f"{spinner(state.spinner_frame)} {state.active_tool}")   # AgentProgressLine.tsx
    print(f"费用: ${state.cost_usd:.4f}") # StatusBar.tsx
```

> 运行示例：`python examples/l4_ui_ink.py`（无需 API Key，有动画效果）
> 对应源码：`claudecode_src/src/components/App.tsx`，`claudecode_src/src/ink.ts`

---

### Layer 5 — 状态管理 & 斜杠命令
**核心文件**：`state/AppStateStore.ts` · `context.ts` · `commands/` · `history.ts`

**核心问题**：多轮对话的历史存在哪里？`/clear` `/model` 这些命令怎么实现的？

```python
# l5_state_commands.py 的核心

# ── 1. 不可变状态（对应 AppStateStore.ts）────────────────
@dataclass(frozen=True)   # frozen = 不可直接修改
class AppState:
    messages: tuple = ()   # tuple 不可变，只能替换整个元组
    model: str = "deepseek-chat"
    cost_usd: float = 0.0

store = AppStateStore(AppState(), on_change=save_to_disk)
store.set(lambda s: replace(s, model="claude-sonnet-4-6"))  # 唯一合法的更新方式

# ── 2. 斜杠命令（对应 commands/ 目录）────────────────────
# /clear /model /cost /help 都是同一种结构，注册在字典里
@dataclass
class SlashCommand:
    name: str
    description: str
    execute: Callable   # (store, args) -> str | None

COMMANDS = {
    "clear":   SlashCommand("clear",   "清空对话历史", cmd_clear),
    "model":   SlashCommand("model",   "切换模型",     cmd_model),
    "compact": SlashCommand("compact", "压缩历史",     cmd_compact),
    ...
}
```

**多轮记忆的秘密**：消息历史永远只追加，从不删除（除非 `/clear`）。每次 API 调用都把完整历史传进去——模型就能"记住"之前说了什么。

> 运行示例：`python examples/l5_state_commands.py`（无需 API Key，交互演示）
> 对应源码：`claudecode_src/src/state/AppStateStore.ts`，`claudecode_src/src/commands/`

---

### Layer 6 — 高级机制
**核心文件**：`skills/` · `coordinator/coordinatorMode.ts` · `cost-tracker.ts` · `buddy/` · `memdir/`

前 5 层覆盖了 Claude Code 的骨架，这一层是肉。

**技能系统**：一个 `.md` 文件就是一个技能，启动时编译成斜杠命令
```markdown
---
name: run-tests
description: 运行测试并展示失败用例
allowed_tools: [bash]
---
执行 `pytest -x --tb=short`，展示失败信息，给出修复建议。
```

**多 Agent 协调**：coordinator 把大任务拆给多个 worker 并行处理
```
coordinator Claude
  ├── AgentTool → worker 1（工具集受限）→ SyntheticOutputTool
  ├── AgentTool → worker 2（工具集受限）→ SyntheticOutputTool
  └── 汇总结果，给出最终答案
```

**费用追踪**：每次 API 调用后累加 token，实时显示在状态栏
```python
tracker.record(input_tokens=1500, output_tokens=300)
print(f"${tracker.total_cost_usd():.6f}")  # 精确到微分
```

> 运行示例：`python examples/l6_advanced.py`（无需 API Key）
> 对应源码：`claudecode_src/src/skills/`，`claudecode_src/src/coordinator/`，`claudecode_src/src/cost-tracker.ts`

---

## 源码目录速查

```
claudecode_src/src/
├── main.tsx              ← L1  CLI 入口
├── entrypoints/          ← L1  交互/非交互/服务器模式
├── setup.ts              ← L1  环境初始化
│
├── query.ts              ← L2  ★ Agent Loop（while true 在这里）
├── QueryEngine.ts        ← L2  多轮循环引擎
├── Task.ts / tasks/      ← L2  任务状态机
│
├── Tool.ts               ← L3  工具接口定义
├── tools.ts              ← L3  工具注册表
├── tools/                ← L3  30+ 工具实现
│   ├── BashTool/         ← L3  对应 l3 示例的 bash
│   ├── FileReadTool/     ← L3  对应 l3 示例的 read_file
│   ├── FileEditTool/     ← L3  对应 l3 示例的 edit_file
│   ├── AgentTool/        ← L6  子 Agent（最复杂）
│   └── MCPTool/          ← 扩展 MCP 工具
│
├── ink.ts                ← L4  Ink 框架入口
├── components/           ← L4  React 组件（App.tsx、进度条等）
├── screens/              ← L4  页面（onboarding、主界面）
├── outputStyles/         ← L4  代码高亮、Markdown 渲染
│
├── state/                ← L5  AppStateStore（Redux-like）
├── context.ts            ← L5  消息历史
├── history.ts            ← L5  持久化
├── commands/             ← L5  斜杠命令实现
│
├── skills/               ← L6  技能系统
├── coordinator/          ← L6  多 Agent 协调
├── cost-tracker.ts       ← L6  Token 费用统计
├── memdir/               ← L6  持久化记忆（/memory 命令）
├── buddy/                ← L6  Buddy 配对模式
└── server/               ← L6  HTTP 服务器模式
```

---

## 推荐阅读策略

1. **先跑** `v1_basic_agent.py`，对 Agent Loop 建立直觉
2. **按层** 读示例文件（`examples/l1_` → `l6_`），每个都能独立运行
3. **对照** 示例里的注释，找到真实源码里对应的函数/文件
4. **带问题读**，不要从头到尾线性阅读源码
5. 每个示例文件顶部的 docstring 写明了"对应哪些源码文件"

---

## 环境配置

```bash
pip install openai python-dotenv

# DeepSeek（推荐，免费额度高，与 v1/v2/l2 示例兼容）
export DEEPSEEK_API_KEY=你的key
export DEEPSEEK_MODEL=deepseek-chat   # 可选

# 或 Anthropic Claude（修改示例里的 base_url 和 model 即可）
export ANTHROPIC_API_KEY=你的key
```

---

## 免责声明

本仓库仅供个人学习与技术研究使用。`claudecode_src/` 目录中的源码已加入 `.gitignore`，不会随本仓库上传至任何公开平台。请勿将相关内容用于商业目的或侵犯 Anthropic 相关权益的行为，一切责任由使用者自行承担。
