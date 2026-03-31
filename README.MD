# easy_claude_code — Claude Code 源码学习路线

[English Version](./README_EN.MD) | 中文版

> Claude Code 源码已泄漏。本仓库收录了源码并整理了一份系统化的阅读路线，帮你真正搞懂它是怎么工作的。

---

## 关于源码

Claude Code 的 TypeScript 源码已于近期泄漏。本仓库将其收录在 `claudecode_src/` 目录下，**已加入 `.gitignore`，不会上传至 GitHub，仅供本地学习使用**。

```
claudecode_src/
├── src/          # TypeScript / React 源码（核心）
└── vendor/       # Native 模块源码（音频、图像、URL 处理等）
```

---

## 目录

- [如何开始](#如何开始)
- [第一层：启动与入口](#第一层启动与入口)
- [第二层：Agent 核心循环](#第二层agent-核心循环)
- [第三层：工具系统](#第三层工具系统)
- [第四层：UI 层 Ink/React](#第四层ui-层-inkreact)
- [第五层：状态与命令](#第五层状态与命令)
- [第六层：高级机制](#第六层高级机制)
- [辅助练习：Python 简化版](#辅助练习python-简化版)
- [免责声明](#免责声明)

---

## 如何开始

**不要从头读到尾**。源码很大，正确的方式是带着问题、按模块拆解阅读。

推荐顺序：入口 → 循环 → 工具 → UI → 状态 → 高级

每读一个模块，问自己：
- 这个文件解决什么问题？
- 如果让我从零实现，我会怎么写？
- 它和我之前知道的什么东西类似？

---

## 第一层：启动与入口

**核心问题**：`claude` 命令敲下去之后，发生了什么？

```
claudecode_src/src/
├── main.tsx                  # 主入口，CLI 解析、初始化、启动 REPL
├── entrypoints/              # 不同启动模式（交互式、非交互式、服务器模式）
├── bootstrap/                # 首次运行初始化逻辑
├── setup.ts                  # 环境检测、配置加载
└── replLauncher.tsx          # REPL 会话启动器
```

**阅读重点**：
- `main.tsx` 里的参数解析和模式分发
- `setup.ts` 如何检测 API Key、权限、操作系统差异
- `entrypoints/` 里交互模式与非交互模式的分叉点

---

## 第二层：Agent 核心循环

**核心问题**：Claude Code 怎么一直循环调用工具直到任务完成？

```
claudecode_src/src/
├── query.ts                  # 单次对话请求的处理逻辑
├── QueryEngine.ts            # 多轮循环引擎（Agent Loop 所在）
├── query/                    # 查询相关子模块（流式处理、错误处理等）
├── Task.ts                   # 单个任务的数据结构
├── tasks.ts                  # 任务注册与管理
└── tasks/                    # 子任务、并行任务等扩展
```

**阅读重点**：
- `QueryEngine.ts` 是整个 Agent 的心脏，找到 while 循环的位置
- `query.ts` 处理单次 API 调用，包括流式响应的拼装
- `Task.ts` 定义了任务状态机：`pending → running → completed/error`
- 对照 `v1_basic_agent.py`（仓库里的 Python 简化版），理解差距在哪

---

## 第三层：工具系统

**核心问题**：Claude Code 内置了哪些工具？每个工具怎么实现的？

```
claudecode_src/src/
├── Tool.ts                   # 工具基类/接口定义
├── tools.ts                  # 所有工具的注册表
└── tools/                    # 每个工具的具体实现目录
    ├── BashTool/             # 执行 Shell 命令
    ├── FileReadTool/         # 读取文件
    ├── FileEditTool/         # 精确编辑文件
    ├── FileWriteTool/        # 写入文件
    ├── GlobTool/             # 文件模式匹配
    ├── GrepTool/             # 内容搜索
    ├── AgentTool/            # 子 Agent（最复杂）
    ├── MCPTool/              # MCP 协议工具
    ├── TodoWriteTool/        # Todo 管理
    ├── TaskCreateTool/       # 任务创建
    ├── SkillTool/            # 技能调用
    ├── LSPTool/              # 语言服务器协议集成
    ├── EnterPlanModeTool/    # 规划模式
    └── ...（共 30+ 个工具）
```

**阅读重点**：
- 先读 `Tool.ts`，搞懂工具的接口：`name / description / inputSchema / call()`
- 再读 `BashTool/`，这是最基础的工具，逻辑最直接
- 读 `AgentTool/`，理解子 Agent 是怎么嵌套调用的（最复杂）
- 注意每个工具的 `inputSchema`：这就是模型看到的 JSON Schema

---

## 第四层：UI 层 Ink/React

**核心问题**：命令行里那些漂亮的输出、进度条、对话框是怎么渲染的？

```
claudecode_src/src/
├── ink.ts                    # Ink 框架入口（React for CLI）
├── components/               # UI 组件库
│   ├── App.tsx               # 根组件
│   ├── AgentProgressLine.tsx # Agent 执行进度展示
│   ├── BashModeProgress.tsx  # Bash 执行进度
│   ├── CompactSummary.tsx    # 对话摘要
│   └── ...
├── screens/                  # 不同屏幕/页面（onboarding、主界面等）
├── outputStyles/             # 输出样式（代码高亮、Markdown 渲染等）
└── dialogLaunchers.tsx       # 弹出对话框的触发逻辑
```

**阅读重点**：
- `App.tsx` 是 React 组件树的根，看清楚整体布局
- Claude Code 用 **Ink** 框架在命令行里渲染 React 组件，和 Web React 写法一样
- `outputStyles/` 解释了为什么代码块有语法高亮

---

## 第五层：状态与命令

**核心问题**：多轮对话的历史、用户设置、会话状态存在哪里？

```
claudecode_src/src/
├── state/                    # 全局状态管理
│   ├── AppState.tsx          # 应用状态定义
│   ├── AppStateStore.ts      # 状态存储（类 Redux）
│   ├── store.ts              # 状态 store 入口
│   └── selectors.ts          # 状态选择器
├── context/                  # React Context（组件间共享状态）
├── context.ts                # 对话上下文（消息历史）
├── history.ts                # 历史记录持久化
├── commands.ts               # 斜杠命令注册
└── commands/                 # 每个斜杠命令的实现（/help /clear /model 等）
```

**阅读重点**：
- `context.ts` 管理消息历史，这是 Agent 多轮记忆的基础
- `commands/` 里每个 `.ts` 文件对应一个 `/command`
- `state/AppStateStore.ts` 的架构接近 Redux，但没有 Redux 依赖

---

## 第六层：高级机制

完成前五层后，可以深入这些高级模块：

```
claudecode_src/src/
├── skills/                   # 技能系统（可复用的 Agent 行为）
│   ├── bundled/              # 内置技能
│   └── bundledSkills.ts      # 技能注册
├── coordinator/              # 多 Agent 协调器
│   └── coordinatorMode.ts    # 协调者模式（管理多个子 Agent）
├── buddy/                    # Buddy 模式（结对编程助手）
├── remote/                   # 远程执行（非本地环境）
├── server/                   # HTTP 服务器模式
├── keybindings/              # 键盘快捷键系统
├── vim/                      # Vim 模式支持
├── voice/                    # 语音输入
├── plugins/                  # 插件系统
├── memdir/                   # 内存目录（持久化记忆）
├── cost-tracker.ts           # Token 用量与费用追踪
└── costHook.ts               # 费用钩子

claudecode_src/vendor/        # Native 模块
├── audio-capture-src/        # 音频捕获（语音输入底层）
├── image-processor-src/      # 图像处理
├── modifiers-napi-src/       # 键盘修饰键检测（Node.js 原生插件）
└── url-handler-src/          # URL 协议处理
```

---

## 辅助练习：Python 简化版

仓库里还有三个 Python 文件，是 Claude Code 核心机制的极简复刻，适合在读源码前热身，或读完某个模块后对照验证：

| 文件 | 对应源码模块 | 用途 |
|------|------------|------|
| `easy_cil.py` | `tools/BashTool/` | 最小可跑：单工具 + 安全护栏 |
| `v1_basic_agent.py` | `QueryEngine.ts` + 核心工具 | 完整 Agent 闭环（同步版） |
| `v2_async_agent.py` | `Task.ts` + `tasks/` | 异步任务解耦（状态机版） |

```bash
pip install openai python-dotenv
export DEEPSEEK_API_KEY=你的key
python v1_basic_agent.py
```

---

## 免责声明

本仓库仅供个人学习和技术研究使用。`claudecode_src/` 目录中的源码来源于网络公开流传的泄漏版本，本仓库不对其合法性作任何担保。该目录已加入 `.gitignore`，不会随本仓库上传至任何公开平台。

**请勿将源码用于任何商业目的，请勿二次传播，请勿用于侵犯 Anthropic 相关权益的行为。一切责任由使用者自行承担。**
