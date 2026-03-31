"""
Layer 4 — UI 层（Ink/React）
对应源码：claudecode_src/src/components/ + screens/ + outputStyles/ + ink.ts

核心问题：Claude Code 的进度条、spinner、彩色输出是怎么渲染的？

答：Claude Code 用 Ink 框架在终端里跑 React 组件树。
  核心思想：UI = f(state)，状态变了就重新渲染，React 负责 diff。
  这和浏览器里写 React 没有本质区别——只不过渲染目标是终端而非 DOM。

  真实 App.tsx 结构：
    <App>
      <MessageList messages={state.messages} />      ← 历史消息
      <ToolProgressLine tool={state.activeTool} />   ← 当前工具进度
      <CostBar cost={state.cost} />                  ← 费用状态栏
      <InputBox />                                   ← 用户输入
    </App>

这个文件用 Python 模拟 Ink 的"状态驱动重渲染"思路，无需 Node.js。
"""

import sys
import time
import threading
from dataclasses import dataclass, field

# ─────────────────────────────────────────────
# 应用状态（对应 AppState.tsx）
# 所有 UI 数据都在这里，不允许组件直接修改
# ─────────────────────────────────────────────
@dataclass
class UIState:
    messages: list = field(default_factory=list)
    active_tool: str | None = None    # 正在执行的工具名
    spinner_frame: int = 0
    cost_usd: float = 0.0
    status: str = "idle"              # idle | thinking | running_tool | done


# ─────────────────────────────────────────────
# ANSI 颜色工具（对应 outputStyles/ + chalk 库）
# ─────────────────────────────────────────────
class Color:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    GREEN  = "\033[32m"
    YELLOW = "\033[33m"
    BLUE   = "\033[34m"
    CYAN   = "\033[36m"
    WHITE  = "\033[37m"
    GRAY   = "\033[90m"

def c(color: str, text: str) -> str:
    return f"{color}{text}{Color.RESET}"


# ─────────────────────────────────────────────
# Spinner 组件（对应 components/Spinner.tsx）
# Ink 里的 spinner 就是一个每 80ms 更新一帧的组件
# ─────────────────────────────────────────────
SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

def Spinner(frame: int) -> str:
    return c(Color.YELLOW, SPINNER_FRAMES[frame % len(SPINNER_FRAMES)])


# ─────────────────────────────────────────────
# 渲染函数（对应 React 组件树的 render()）
#
# 关键点：这是一个【纯函数】——给定相同的 state，永远输出相同的 UI。
# Ink 的 React reconciler 负责计算 diff，只更新变化的部分。
# 这里我们用"清屏+重绘"模拟，效果等价。
# ─────────────────────────────────────────────
def render(state: UIState):
    """
    UI = f(state)
    每次调用都完整重绘终端，不保留任何本地 UI 状态。
    """
    # 移动光标到顶部，清屏（对应 Ink 的完整重渲染）
    sys.stdout.write("\033[H\033[J")
    sys.stdout.flush()

    # ── 标题栏 ──────────────────────────────────────
    print(c(Color.BOLD, "  Claude Code  ") + c(Color.GRAY, "Layer 4 · UI 演示"))
    print(c(Color.GRAY, "  " + "─" * 50))

    # ── MessageList（对应 components/MessageList.tsx）──
    recent = state.messages[-8:]          # 只显示最近 8 条
    for msg in recent:
        role = msg["role"]
        content = msg["content"]
        if role == "user":
            prefix = c(Color.CYAN + Color.BOLD, "  You  ")
            text = c(Color.WHITE, content[:80])
        elif role == "assistant":
            prefix = c(Color.GREEN + Color.BOLD, "  AI   ")
            text = c(Color.WHITE, content[:80])
        else:
            prefix = c(Color.GRAY, "  tool ")
            text = c(Color.GRAY, content[:80])
        print(f"{prefix}  {text}")

    print()

    # ── ToolProgressLine（对应 components/AgentProgressLine.tsx）──
    if state.active_tool:
        spinner = Spinner(state.spinner_frame)
        tool_text = c(Color.YELLOW, f"运行中: {state.active_tool}")
        print(f"  {spinner}  {tool_text}")
    elif state.status == "thinking":
        spinner = Spinner(state.spinner_frame)
        print(f"  {spinner}  {c(Color.BLUE, '思考中...')}")
    elif state.status == "done":
        print(f"  {c(Color.GREEN, '✓')}  {c(Color.GRAY, '任务完成')}")

    # ── 状态栏（对应 components/StatusBar.tsx）─────────
    print()
    cost_str = c(Color.GRAY, f"  费用: ${state.cost_usd:.4f}")
    msg_count = c(Color.GRAY, f"  消息: {len(state.messages)}")
    print(f"{cost_str}  {msg_count}")


# ─────────────────────────────────────────────
# 状态更新（对应 React setState + useEffect 组合）
# 每次更新状态后立即重渲染
# ─────────────────────────────────────────────
def update(state: UIState, **kwargs) -> UIState:
    for k, v in kwargs.items():
        setattr(state, k, v)
    render(state)
    return state


# ─────────────────────────────────────────────
# 动画：Spinner 在后台线程更新帧（对应 Ink 的定时器）
# ─────────────────────────────────────────────
def start_spinner(state: UIState, stop_event: threading.Event):
    while not stop_event.is_set():
        state.spinner_frame += 1
        render(state)
        time.sleep(0.08)


# ─────────────────────────────────────────────
# 演示：模拟一次完整的 Agent 交互流程
# ─────────────────────────────────────────────
def demo():
    state = UIState()
    render(state)
    time.sleep(0.5)

    # 1. 用户发送消息
    state = update(state,
        messages=[{"role": "user", "content": "帮我列出当前目录的文件"}],
        status="thinking"
    )
    time.sleep(0.3)

    # 2. 模型开始思考 + spinner 动画
    stop = threading.Event()
    t = threading.Thread(target=start_spinner, args=(state, stop), daemon=True)
    t.start()
    time.sleep(1.2)

    # 3. 模型决定调用 bash 工具
    stop.set()
    t.join()
    state = update(state,
        status="running_tool",
        active_tool="bash: ls -la",
    )
    stop = threading.Event()
    t = threading.Thread(target=start_spinner, args=(state, stop), daemon=True)
    t.start()
    time.sleep(1.0)

    # 4. 工具执行完成，追加结果
    stop.set()
    t.join()
    state = update(state,
        messages=state.messages + [
            {"role": "tool", "content": "README.MD  PHILOSOPHY.MD  examples/..."},
        ],
        active_tool=None,
        cost_usd=0.0003,
    )
    time.sleep(0.5)

    # 5. 模型给出最终回答
    state = update(state,
        messages=state.messages + [
            {"role": "assistant", "content": "当前目录包含：README.MD、示例文件和 examples/ 目录"},
        ],
        status="done",
        cost_usd=0.0007,
    )
    time.sleep(2)
    print()


if __name__ == "__main__":
    try:
        demo()
    except KeyboardInterrupt:
        print()
