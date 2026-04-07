"""
Layer 2 — Agent 核心循环
对应源码：claudecode_src/src/query.ts + QueryEngine.ts
配套深挖：
  - 中文：docs/layers/l2-agent-loop.md
  - English: docs/layers/l2-agent-loop.en.md

核心问题：Claude Code 怎么一直循环调用工具直到任务完成？

你会看到：query.ts 里有一个 async generator function*，内部是 while (true)。
  每轮循环：调用模型 → 如果返回工具调用就执行 → 把结果追回历史 → 继续。
  模型说"我做完了"（stop_reason = end_turn）时 return，循环结束。

这就是整个 Claude Code 的心脏。其他一切都是围绕它的脚手架。

运行方式：
  无需 API Key（DRY_RUN 模式，看到完整 loop 节奏）：
    python examples/l2_agent_loop.py

  有 API Key（真实模型调用）：
    export DEEPSEEK_API_KEY=你的key
    python examples/l2_agent_loop.py

跑完后下一步：
  1. 读 docs/paths/p2-core-loop.md
  2. 看 docs/source-map.md 的"单轮查询主链路"
  3. 搜 `query`、`queryLoop`、`tool_result`
  4. 先开 `query.ts` 和 `QueryEngine.ts`
"""

import os
import json
import subprocess
from openai import OpenAI

# ─────────────────────────────────────────────
# DRY_RUN 模式：没有 API Key 时自动启用
# 用预设的"假模型响应"走完完整的 loop 节奏，
# 让你不依赖真实 API 也能看到 while(true) 的每一步。
# ─────────────────────────────────────────────
DRY_RUN = not os.environ.get("DEEPSEEK_API_KEY", "").strip()

# ─────────────────────────────────────────────
# 配置（支持 DeepSeek 或任意 OpenAI 兼容接口）
# ─────────────────────────────────────────────
client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY", "no-key"),
    base_url="https://api.deepseek.com/v1",
)
MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

# ─────────────────────────────────────────────
# Mock 响应序列（DRY_RUN 时使用）
# 模拟一次完整的 2 轮 loop：
#   轮 1 → 模型发起 bash 工具调用
#   轮 2 → 模型看到工具结果，给出最终回答（end_turn）
# ─────────────────────────────────────────────
_MOCK_TOOL_CALL_ID = "mock_call_001"
_MOCK_SCRIPT = [
    # 第 1 轮：返回工具调用（对应 stop_reason = "tool_calls"）
    {
        "content": None,
        "tool_calls": [{
            "id": _MOCK_TOOL_CALL_ID,
            "type": "function",
            "function": {
                "name": "bash",
                "arguments": json.dumps({"command": "echo '[mock] hello from bash tool'"})
            }
        }]
    },
    # 第 2 轮：看到工具结果后给出最终回答（对应 stop_reason = "end_turn"）
    {
        "content": "[DRY_RUN] 工具执行完了！这就是 while(true) 的完整节奏：\n"
                   "  轮 1 → 模型选工具 → 执行 → 结果追回历史\n"
                   "  轮 2 → 模型读到结果 → end_turn → loop 退出\n"
                   "现在去读 query.ts 第 241 行的 queryLoop()，找到这个 while(true)。",
        "tool_calls": None
    },
]
_mock_turn = 0


def mock_chat_completion(messages):
    """返回预设的假响应，模拟真实 API 的 response 结构。"""
    global _mock_turn
    script = _MOCK_SCRIPT[min(_mock_turn, len(_MOCK_SCRIPT) - 1)]
    _mock_turn += 1

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

# ─────────────────────────────────────────────
# 工具定义（完整的工具系统见 Layer 3）
# ─────────────────────────────────────────────
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "bash",
            "description": "执行 shell 命令，返回输出",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"],
            },
        },
    }
]

def run_bash(command: str) -> str:
    """执行命令，截断超长输出（防止 context 爆满）"""
    result = subprocess.run(
        command, shell=True, capture_output=True, text=True, timeout=30
    )
    output = (result.stdout + result.stderr).strip()
    return output[:2000] if len(output) > 2000 else output or "(无输出)"


# ─────────────────────────────────────────────
# 核心循环（对应 query.ts 的 async function* queryLoop()）
#
# 真实源码（query.ts line 241~）：
#   async function* queryLoop(...) {
#     while (true) {                          ← 无限循环
#       const stream = await callAPI(...)
#       yield* processStream(stream)
#       if (stop_reason === 'end_turn') return ← 退出条件
#       const results = await runTools(...)
#       messages.push(results)               ← 结果追回历史
#     }
#   }
# ─────────────────────────────────────────────
def query_loop(messages: list) -> str:
    """
    Agent Loop 的最小实现。
    接收消息历史，在内部循环直到任务完成，返回最终文字响应。
    """
    while True:                              # ← 这就是那个 while (true)

        # Step 1：调用模型（DRY_RUN 时用脚本响应，有 Key 时真实调用）
        if DRY_RUN:
            response = mock_chat_completion(messages)
        else:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=TOOLS,
            )
        reply = response.choices[0].message

        # Step 2：没有工具调用 → 模型说"我做完了"，退出循环
        if not reply.tool_calls:
            return reply.content or "(空响应)"

        # Step 3：有工具调用 → 把模型的回复先追加到历史
        messages.append({
            "role": "assistant",
            "content": reply.content or "",
            "tool_calls": [tc.model_dump() for tc in reply.tool_calls],
        })

        # Step 4：逐个执行工具，把每个结果追加到历史
        for tc in reply.tool_calls:
            args = json.loads(tc.function.arguments)
            print(f"  → 工具调用: {tc.function.name}({args})")

            result = run_bash(args["command"])
            print(f"  ← 工具结果: {result[:100]}{'...' if len(result) > 100 else ''}")

            # 工具结果以 tool 角色追加——模型下一轮能看到
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

        # Step 5：历史已更新，回到循环顶部继续调用模型
        # 模型会看到工具结果并决定：继续调用工具 or 给出最终答案


# ─────────────────────────────────────────────
# REPL 入口
# ─────────────────────────────────────────────
def main():
    mode = "DRY_RUN（无需 API Key）" if DRY_RUN else "真实 API"
    print(f"Layer 2 — Agent Loop 演示  [{mode}]  (输入 exit 退出)\n")
    if DRY_RUN:
        print("提示：没有检测到 DEEPSEEK_API_KEY，自动进入 DRY_RUN 模式。")
        print("      输入任意内容，观察 while(true) 的完整 2 轮节奏。\n")
    messages = []   # 消息历史：每轮都追加，从不删除（这是多轮记忆的全部秘密）

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            break
        if user_input in ("exit", "quit"):
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        print("Assistant: ", end="", flush=True)
        final = query_loop(messages)
        print(final)

        # 把最终回答也追加到历史，保持多轮连贯性
        messages.append({"role": "assistant", "content": final})
        print()


if __name__ == "__main__":
    main()


# ═══════════════════════════════════════════════════════════
# 自检问题（跑完后回答，不要查代码）
# ═══════════════════════════════════════════════════════════
#
# 1. while(true) 在 query() 里还是在 queryLoop() 里？
#    这两个函数各自负责什么？
#
# 2. 工具结果为什么必须追回 messages 列表，
#    而不是临时存一个变量用完就扔？
#
# 3. 模型什么条件下会让 loop 退出？在代码里退出信号叫什么？
#    提示：看 stop_reason / tool_calls 的判断逻辑。
