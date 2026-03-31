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

运行前需要设置：
  export DEEPSEEK_API_KEY=你的key
  pip install openai

如果你暂时没有 API Key：
  先读 docs/layers/l2-agent-loop.md，再配合 docs/source-map.md 搜 `queryLoop`。
"""

import os
import json
import subprocess
from openai import OpenAI

# ─────────────────────────────────────────────
# 配置（支持 DeepSeek 或任意 OpenAI 兼容接口）
# ─────────────────────────────────────────────
client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY", ""),
    base_url="https://api.deepseek.com/v1",
)
MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

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

        # Step 1：调用模型
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
    print("Layer 2 — Agent Loop 演示  (输入 exit 退出)\n")
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
