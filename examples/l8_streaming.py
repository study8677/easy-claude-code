"""
Layer 8 — Async Generator：Claude Code 的流式架构
对应源码：claudecode_src/src/query.ts（async function* query()）
配套深挖：
  - 中文：docs/layers/l8-streaming.md
  - English: docs/layers/l8-streaming.en.md

核心问题：为什么 Claude Code 用 async generator 而不是回调或 Promise？

你会看到：因为 Agent Loop 需要同时满足三个要求：
  1. 流式输出（边生成边显示，不等全部完成）
  2. 可取消（用户按 Ctrl+C 时立即停止）
  3. 可组合（子 Agent 的事件可以 yield* 传递给父 Agent）

回调做不到 #3，Promise 做不到 #1，只有 generator 三者都满足。

真实源码中 query.ts 的结构：
  export async function* query(params)     ← 外层，处理启动和收尾
    async function* queryLoop(params)       ← 内层，真正的 while(true)
      yield { type: 'stream_request_start' }
      yield* processStream(stream)          ← 嵌套 generator！
      yield { type: 'tool_result', ... }
      if (done) return

事件类型（yield 出来的东西）：
  stream_request_start  → 开始一轮 API 调用
  text                  → 模型输出一段文字
  tool_use              → 模型要调用工具
  tool_result           → 工具执行完成
  done                  → 整个任务结束
  error                 → 出错（但有时会被 withheld，等待恢复）

运行方式：
  无需 API Key（DRY_RUN 模式，观察完整事件序列）：
    python examples/l8_streaming.py

  有 API Key（真实 streaming）：
    export DEEPSEEK_API_KEY=你的key
    python examples/l8_streaming.py

跑完后下一步：
  1. 读 docs/paths/p2-core-loop.md
  2. 看 docs/source-map.md 的“单轮查询主链路”
  3. 搜 `stream_request_start`、`queryModelWithStreaming`、`first_chunk`
  4. 先开 `query.ts` 和 `services/api/claude.ts`
"""

import os
import json
import subprocess
from typing import AsyncGenerator
import asyncio
from openai import AsyncOpenAI

# ─────────────────────────────────────────────────────────────
# DRY_RUN 模式：没有 API Key 时自动启用
# 用预设事件序列走完完整的 async generator loop，
# 让你不依赖真实 API 也能观察每一个 yield 事件的类型和顺序。
# ─────────────────────────────────────────────────────────────
DRY_RUN = not os.environ.get("DEEPSEEK_API_KEY", "").strip()

client = AsyncOpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY", "no-key"),
    base_url="https://api.deepseek.com/v1",
)
MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

# ─────────────────────────────────────────────────────────────
# Mock 响应序列（DRY_RUN 时使用）
# 两轮：第 1 轮发起 bash 工具调用，第 2 轮给出最终文本（end_turn）
# ─────────────────────────────────────────────────────────────
_MOCK_CALL_ID = "mock_stream_001"
_mock_stream_turn = 0

_MOCK_STREAM_SCRIPT = [
    {   # 轮 1：tool_use
        "content": "我来查一下...",
        "tool_calls": [{
            "id": _MOCK_CALL_ID,
            "type": "function",
            "function": {"name": "bash",
                         "arguments": json.dumps({"command": "echo '[mock stream] ls result'"})}
        }]
    },
    {   # 轮 2：end_turn
        "content": "[DRY_RUN] 看到了！这就是 async generator 的完整事件序列：\n"
                   "  stream_request_start → text → tool_use → tool_result → stream_request_start → text → done\n"
                   "每个 yield 都是一个独立事件，UI 层 async for 消费，可取消、可组合。\n"
                   "现在去 query.ts 搜 'yield { type' 看真实的事件类型定义。",
        "tool_calls": None
    },
]


async def mock_api_call(messages):
    """模拟 API 返回，结构与真实 response 一致。"""
    global _mock_stream_turn
    script = _MOCK_STREAM_SCRIPT[min(_mock_stream_turn, len(_MOCK_STREAM_SCRIPT) - 1)]
    _mock_stream_turn += 1
    await asyncio.sleep(0.05)  # 模拟网络延迟

    class FakeFunction:
        def __init__(self, name, arguments): self.name = name; self.arguments = arguments

    class FakeToolCall:
        def __init__(self, d):
            self.id = d["id"]; self.type = d["type"]
            self.function = FakeFunction(d["function"]["name"], d["function"]["arguments"])
        def model_dump(self):
            return {"id": self.id, "type": self.type,
                    "function": {"name": self.function.name, "arguments": self.function.arguments}}

    class FakeMessage:
        def __init__(self, s):
            self.content = s["content"]
            self.tool_calls = [FakeToolCall(tc) for tc in s["tool_calls"]] if s.get("tool_calls") else None

    class FakeChoice:
        def __init__(self, s): self.message = FakeMessage(s)

    class FakeResponse:
        def __init__(self, s): self.choices = [FakeChoice(s)]

    return FakeResponse(script)

TOOLS = [{
    "type": "function",
    "function": {
        "name": "bash",
        "description": "执行 shell 命令",
        "parameters": {
            "type": "object",
            "properties": {"command": {"type": "string"}},
            "required": ["command"],
        },
    },
}]


# ─────────────────────────────────────────────────────────────
# 事件类型（对应 query.ts 里 yield 出来的各种类型）
# ─────────────────────────────────────────────────────────────
def event_stream_start(turn: int) -> dict:
    return {"type": "stream_request_start", "turn": turn}

def event_text(text: str) -> dict:
    return {"type": "text", "text": text}

def event_tool_use(name: str, args: dict, call_id: str) -> dict:
    return {"type": "tool_use", "name": name, "args": args, "id": call_id}

def event_tool_result(name: str, result: str, call_id: str) -> dict:
    return {"type": "tool_result", "name": name, "result": result, "id": call_id}

def event_done(final_text: str) -> dict:
    return {"type": "done", "text": final_text}

def event_error(message: str, withheld: bool = False) -> dict:
    """
    withheld=True 表示错误被"暂时隐藏"，等待恢复逻辑处理。
    对应 query.ts 里 isWithheldMaxOutputTokens() 的机制——
    SDK 调用方看到 error 可能直接终止会话，
    所以中间错误要先隐藏，等确认无法恢复才暴露。
    """
    return {"type": "error", "message": message, "withheld": withheld}


# ─────────────────────────────────────────────────────────────
# 工具执行（async 版本，不阻塞事件循环）
# ─────────────────────────────────────────────────────────────
async def run_bash_async(command: str) -> str:
    proc = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    output = (stdout + stderr).decode(errors="replace").strip()
    return output[:2000] if len(output) > 2000 else output or "(无输出)"


# ─────────────────────────────────────────────────────────────
# 内层循环：async generator（对应 query.ts 的 queryLoop()）
#
# 这是 Claude Code 架构的精髓：
# 整个 Agent Loop 是一个 generator，通过 yield 吐出事件。
# UI 层通过 async for 消费这些事件，实时更新显示。
#
# 对比 Promise/回调：
#   - Promise: await 只能等一次，拿到最终结果，不适合流式
#   - 回调: 每个事件注册回调，难以组合（地狱）
#   - Generator: yield 可以暂停/恢复，yield* 可以委托给子 generator
# ─────────────────────────────────────────────────────────────
async def query_loop(
    messages: list,
    abort_signal: asyncio.Event | None = None,
) -> AsyncGenerator[dict, None]:
    """
    核心 Agent Loop，以 async generator 形式实现。

    调用方用法：
        async for event in query_loop(messages):
            handle(event)

    取消用法：
        abort = asyncio.Event()
        asyncio.create_task(query_loop(messages, abort))
        abort.set()   # 任何时刻都可以取消
    """
    turn = 0

    while True:
        # 检查取消信号（对应 AbortController + AbortSignal）
        if abort_signal and abort_signal.is_set():
            yield event_error("用户取消", withheld=False)
            return

        turn += 1
        yield event_stream_start(turn)

        # 调用模型（DRY_RUN 时用脚本响应，有 Key 时真实调用）
        try:
            if DRY_RUN:
                response = await mock_api_call(messages)
            else:
                response = await client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    tools=TOOLS,
                )
        except Exception as e:
            # 某些错误会被 withheld，等待上层决定是否恢复
            # 例如 max_output_tokens 错误会触发 token 升级重试
            yield event_error(str(e), withheld="max_tokens" in str(e).lower())
            return

        reply = response.choices[0].message

        # 有文字输出 → yield 给 UI 显示
        if reply.content:
            yield event_text(reply.content)

        # 没有工具调用 → 任务完成，退出循环
        if not reply.tool_calls:
            yield event_done(reply.content or "")
            return

        # 有工具调用 → 先把模型回复追加到历史
        messages.append({
            "role": "assistant",
            "content": reply.content or "",
            "tool_calls": [tc.model_dump() for tc in reply.tool_calls],
        })

        # 执行每个工具调用
        for tc in reply.tool_calls:
            args = json.loads(tc.function.arguments)
            yield event_tool_use(tc.function.name, args, tc.id)

            result = await run_bash_async(args.get("command", ""))
            yield event_tool_result(tc.function.name, result, tc.id)

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

        # 继续循环，模型看到工具结果后决定下一步


# ─────────────────────────────────────────────────────────────
# 消费层：UI 如何处理事件流（对应 components/App.tsx + QueryEngine.ts）
# ─────────────────────────────────────────────────────────────
async def render_events(event_stream: AsyncGenerator[dict, None]):
    """
    消费 generator 吐出的事件，实时更新 UI。
    对应 QueryEngine.ts 里 for await (const event of query(...))
    """
    async for event in event_stream:
        t = event["type"]

        if t == "stream_request_start":
            print(f"\n  [第 {event['turn']} 轮] 调用模型...", flush=True)

        elif t == "text":
            print(f"\nAssistant: {event['text']}", flush=True)

        elif t == "tool_use":
            print(f"\n  ⟳ 工具调用: {event['name']}({event['args']})", flush=True)

        elif t == "tool_result":
            result_preview = event['result'][:80]
            if len(event['result']) > 80:
                result_preview += "..."
            print(f"  ✓ 工具结果: {result_preview}", flush=True)

        elif t == "done":
            print("\n  [任务完成]", flush=True)

        elif t == "error":
            withheld = "(已隐藏，等待恢复)" if event.get("withheld") else ""
            print(f"\n  [错误] {event['message']} {withheld}", flush=True)


# ─────────────────────────────────────────────────────────────
# REPL 入口
# ─────────────────────────────────────────────────────────────
async def main():
    mode = "DRY_RUN（无需 API Key）" if DRY_RUN else "真实 API"
    print(f"Layer 8 — Async Generator 流式架构演示  [{mode}]  (输入 exit 退出)\n")
    if DRY_RUN:
        print("提示：没有检测到 DEEPSEEK_API_KEY，自动进入 DRY_RUN 模式。")
        print("      输入任意内容，观察完整的事件序列：stream_request_start → text → tool_use → tool_result → done\n")
    else:
        print("提示：试试 '列出当前目录文件，然后告诉我有几个 .py 文件'\n")

    messages = []
    abort = asyncio.Event()

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            abort.set()
            break
        if user_input in ("exit", "quit"):
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        # 启动 generator，消费事件流
        stream = query_loop(messages, abort_signal=abort)
        await render_events(stream)

        # 把最终文字追加到历史（供下一轮使用）
        if messages and messages[-1]["role"] == "tool":
            pass   # 已经在循环里追加了
        print()


if __name__ == "__main__":
    asyncio.run(main())


# ═══════════════════════════════════════════════════════════
# 自检问题（跑完后回答，不要查代码）
# ═══════════════════════════════════════════════════════════
#
# 1. yield* 和 yield 有什么区别？
#    在 Claude Code 架构里，yield* 解决了什么问题？
#    提示：想想子 agent 的事件如何传递给父 agent。
#
# 2. error 事件的 withheld=True 是什么意思？
#    什么情况下错误会被"扣押"而不是立即暴露给调用方？
#
# 3. 如果用 Promise 代替 async generator 来实现 queryLoop，
#    "用户随时可以 Ctrl+C 取消" 这个特性会怎么实现？会变得更复杂还是更简单？
