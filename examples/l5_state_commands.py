"""
Layer 5 — 状态管理 & 斜杠命令
对应源码：claudecode_src/src/state/ + context.ts + commands/ + history.ts
配套深挖：
  - 中文：docs/layers/l5-state-commands.md
  - English: docs/layers/l5-state-commands.en.md

核心问题：Claude Code 的多轮记忆、用户设置、斜杠命令存在哪里？怎么工作的？

你会看到：两个相互配合的系统：

  1. AppStateStore（state/ 目录）
     类 Redux 的不可变状态存储。状态永远不直接修改，
     只通过 setState(prev => newState) 替换。
     每次状态变化触发 onChangeAppState() 钩子（保存、更新 UI 等）。

  2. 斜杠命令（commands/ 目录）
     /clear /compact /model /cost 等不是硬编码的特殊逻辑，
     而是统一注册在命令表里的对象，和工具的架构完全一致。
     命令可以修改状态、注入消息、或直接返回文字。

无需 API Key 即可运行。

运行后请回答：
  - 为什么 slash command 更像命令注册表，而不是特殊语法？
  - 哪些状态应该进 store，哪些不应该？

跑完后下一步：
  1. 读 docs/layers/l5-state-commands.md
  2. 看 docs/source-map.md 的“UI / 状态 / REPL 路径”
  3. 搜 `history`、`commands`、`processInitialMessage`
  4. 先开 `history.ts`、`commands/` 和 `screens/REPL.tsx`
"""

from dataclasses import dataclass, replace
from typing import Callable
import json
import os
from pathlib import Path

# ─────────────────────────────────────────────
# 1. 不可变状态（对应 AppState.tsx）
#
# 真实 AppState 包含 100+ 字段，这里只保留核心字段演示原理。
# frozen=True 确保不能直接修改，必须通过 replace() 创建新实例。
# ─────────────────────────────────────────────
@dataclass(frozen=True)
class AppState:
    messages: tuple = ()           # 消息历史（tuple 不可变）
    model: str = "deepseek-chat"
    permission_mode: str = "default"  # default | acceptEdits | bypassPermissions
    cost_usd: float = 0.0
    is_thinking: bool = False


# ─────────────────────────────────────────────
# 2. 状态存储（对应 AppStateStore.ts + store.ts）
#
# 核心契约：状态变更只能通过 set_state(old => new) 进行。
# 这让 on_change 钩子能精确感知每一次变化，
# 也让"撤销""会话回放"等功能成为可能。
# ─────────────────────────────────────────────
class AppStateStore:
    def __init__(self, initial: AppState, on_change: Callable | None = None):
        self._state = initial
        self._on_change = on_change
        self._history: list[AppState] = [initial]   # 支持 undo

    def get(self) -> AppState:
        return self._state

    def set(self, updater: Callable[[AppState], AppState]):
        """
        对应 store.ts 的 setState(fn)。
        传入一个函数 old_state -> new_state，而不是直接传新值。
        这样调用方拿到的是最新状态，避免并发更新丢失。
        """
        old = self._state
        new = updater(old)
        if old is new:
            return   # 没变化，不触发 on_change
        self._state = new
        self._history.append(new)
        if self._on_change:
            self._on_change(old, new)

    def undo(self) -> bool:
        """调试用：回退到上一个状态"""
        if len(self._history) < 2:
            return False
        self._history.pop()
        self._state = self._history[-1]
        return True


# ─────────────────────────────────────────────
# 3. 状态变化钩子（对应 onChangeAppState.ts）
#
# 每次 set_state 都会触发这里，做持久化/日志/UI 更新等副作用。
# ─────────────────────────────────────────────
def on_change(old: AppState, new: AppState):
    if len(new.messages) > len(old.messages):
        latest = new.messages[-1]
        print(f"  [state] +消息 [{latest['role']}]: {str(latest['content'])[:50]}")
    if new.model != old.model:
        print(f"  [state] 模型切换: {old.model} → {new.model}")
    if new.cost_usd != old.cost_usd:
        print(f"  [state] 费用更新: ${new.cost_usd:.4f}")


# ─────────────────────────────────────────────
# 4. 消息历史（对应 context.ts）
#
# 多轮记忆的全部秘密就在这里：
# 永远追加，从不删除（除非用户 /clear）。
# ─────────────────────────────────────────────
def add_message(store: AppStateStore, role: str, content) -> None:
    """追加一条消息到历史"""
    store.set(lambda s: replace(s,
        messages=s.messages + ({"role": role, "content": content},)
    ))

def add_tool_result(store: AppStateStore, tool_use_id: str, result: str) -> None:
    """
    工具结果以特殊格式追回——模型必须看到结果才能继续推理。
    对应 context.ts 里 addToolResult() 的消息格式。
    """
    store.set(lambda s: replace(s,
        messages=s.messages + ({
            "role": "user",
            "content": [{"type": "tool_result", "tool_use_id": tool_use_id, "content": result}]
        },)
    ))


# ─────────────────────────────────────────────
# 5. 斜杠命令（对应 commands/ 目录）
#
# 每个 /command 就是一个 SlashCommand 对象：
#   name        → 触发词（不含 /）
#   description → /help 里显示的说明
#   execute     → 接收 store + 参数，返回要显示的文本（或 None）
#
# 对比工具系统（Layer 3）：架构完全一致，只是触发方式不同
#   工具 → 模型决定调用
#   命令 → 用户手动输入 /xxx
# ─────────────────────────────────────────────
@dataclass
class SlashCommand:
    name: str
    description: str
    execute: Callable  # (store: AppStateStore, args: str) -> str | None


def cmd_clear(store: AppStateStore, _args: str) -> str:
    """对应 commands/clear.ts：清空消息历史，但保留配置"""
    count = len(store.get().messages)
    store.set(lambda s: replace(s, messages=(), cost_usd=0.0))
    return f"已清空 {count} 条消息"

def cmd_model(store: AppStateStore, args: str) -> str:
    """对应 commands/model.ts：切换使用的模型"""
    model = args.strip()
    if not model:
        return f"当前模型: {store.get().model}"
    store.set(lambda s: replace(s, model=model))
    return f"已切换到: {model}"

def cmd_cost(store: AppStateStore, _args: str) -> str:
    """对应 commands/cost.ts：显示本次会话费用"""
    return f"本次会话费用: ${store.get().cost_usd:.4f}"

def cmd_help(store: AppStateStore, _args: str) -> str:
    """对应 commands/help.ts：列出所有可用命令"""
    lines = ["可用命令：\n"]
    for cmd in COMMANDS.values():
        lines.append(f"  /{cmd.name:15s}  {cmd.description}")
    return "\n".join(lines)

def cmd_compact(store: AppStateStore, _args: str) -> str:
    """
    对应 commands/compact.ts：压缩对话历史（保留摘要，节省 context window）。
    真实实现会调用模型生成摘要后替换历史；这里只做演示。
    """
    count = len(store.get().messages)
    store.set(lambda s: replace(s,
        messages=({"role": "system", "content": f"[已压缩 {count} 条历史消息]"},)
    ))
    return f"已将 {count} 条消息压缩为摘要"


COMMANDS: dict[str, SlashCommand] = {
    c.name: c for c in [
        SlashCommand("clear",   "清空对话历史",           cmd_clear),
        SlashCommand("model",   "查看/切换模型",           cmd_model),
        SlashCommand("cost",    "显示本次会话费用",         cmd_cost),
        SlashCommand("help",    "显示所有可用命令",         cmd_help),
        SlashCommand("compact", "压缩历史消息节省 context", cmd_compact),
    ]
}


def handle_input(text: str, store: AppStateStore) -> str | None:
    """
    统一处理用户输入：斜杠命令 or 普通消息。
    对应 processUserInput.ts 的分流逻辑。
    """
    if text.startswith("/"):
        parts = text[1:].split(None, 1)
        name, args = parts[0], parts[1] if len(parts) > 1 else ""
        cmd = COMMANDS.get(name)
        if cmd:
            return cmd.execute(store, args)
        return f"未知命令: /{name}  (输入 /help 查看所有命令)"

    # 普通消息 → 追加到历史
    add_message(store, "user", text)
    return None


# ─────────────────────────────────────────────
# 演示
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("Layer 5 — 状态管理 & 斜杠命令演示\n")
    print("试试：/help  /model claude-opus-4  /cost  /clear  普通消息  exit\n")

    store = AppStateStore(AppState(), on_change=on_change)

    while True:
        try:
            text = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            break
        if text in ("exit", "quit"):
            break
        if not text:
            continue

        result = handle_input(text, store)
        if result:
            print(f"  → {result}\n")
        else:
            # 模拟模型回复 + 费用累积
            store.set(lambda s: replace(s, cost_usd=s.cost_usd + 0.0002))
            add_message(store, "assistant", f"(模拟回复 '{text}')")
            print()


# ═══════════════════════════════════════════════════════════
# 自检问题（跑完后回答，不要查代码）
# ═══════════════════════════════════════════════════════════
#
# 1. /model、/cost 这类斜杠命令为什么在发给模型之前就被拦截处理？
#    如果让模型来解析斜杠命令，会有什么问题？
#
# 2. AppStateStore 为什么用 replace(s, field=value) 的不可变方式更新，
#    而不是直接 s.field = value？
#
# 3. 如果现在要加一个 /export 命令，你会在哪个文件的哪个位置添加？
