"""
Layer 9 — Context Window 管理 & Auto-Compact
对应源码：claudecode_src/src/utils/context.ts
         claudecode_src/src/query.ts（auto-compact 逻辑）
         claudecode_src/src/commands/compact.ts

核心问题：Claude Code 如何在超长对话中不爆 context window？

答：三道防线——

  1. Token 预算监控
     每次 API 调用后检查：已用 token / 窗口上限。
     超过阈值（默认 90%）触发 auto-compact。

  2. Auto-Compact（自动压缩）
     调用模型对当前历史生成一段摘要，
     用摘要替换原始消息（保留关键信息，丢弃详细内容）。
     继续对话，不中断用户体验。

  3. /compact 斜杠命令
     用户手动触发，效果同 auto-compact。

  关键设计：静态/动态边界（SYSTEM_PROMPT_DYNAMIC_BOUNDARY）
    系统 Prompt 的前半部分永不变（跨 session 可缓存）。
    后半部分每轮更新（用户名、当前目录等）。
    这个分界线最大化了 Claude 的 prompt cache 命中率（节省 50~70K token）。

无需 API Key 即可运行（演示逻辑；注释掉的代码展示真实实现方式）
"""

import os
import json

# ─────────────────────────────────────────────────────────────
# Token 估算（真实代码用 tiktoken / Claude 的计数 API）
# 这里用"4 字符 = 1 token"的粗略估算做演示
# ─────────────────────────────────────────────────────────────
def estimate_tokens(messages: list) -> int:
    total = 0
    for msg in messages:
        content = msg.get("content", "")
        if isinstance(content, str):
            total += len(content) // 4
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict):
                    total += len(str(block)) // 4
    return total


# ─────────────────────────────────────────────────────────────
# Context Window 配置（对应 utils/context.ts）
#
# 真实代码的 getContextWindowForModel() 有 6 层解析优先级：
#   1. 环境变量覆盖（内部测试用）
#   2. [1m] 后缀（用户明确选择百万 token 窗口）
#   3. SDK 元数据（API 返回的能力描述）
#   4. Beta header（context_1m_beta）
#   5. 统计分配（A/B 测试）
#   6. 默认值（200K）
# ─────────────────────────────────────────────────────────────
CONTEXT_WINDOWS = {
    "claude-opus-4-6":   200_000,
    "claude-sonnet-4-6": 200_000,
    "claude-haiku-4-5":  200_000,
    "deepseek-chat":     64_000,
    "deepseek-reasoner": 128_000,
}

COMPACT_THRESHOLD = 0.85    # 使用超过 85% 时触发 auto-compact
OUTPUT_RESERVE   = 8_000    # 为模型输出预留的 token（不算在历史里）


class ContextWindowManager:
    """
    对应 utils/context.ts 里的上下文管理逻辑。
    追踪 token 用量，判断是否需要压缩。
    """

    def __init__(self, model: str = "deepseek-chat"):
        self.model = model
        self.window_size = CONTEXT_WINDOWS.get(model, 64_000)
        self.usable = self.window_size - OUTPUT_RESERVE

    def usage_ratio(self, messages: list) -> float:
        """当前历史占可用窗口的比例"""
        used = estimate_tokens(messages)
        return used / self.usable

    def should_compact(self, messages: list) -> bool:
        return self.usage_ratio(messages) >= COMPACT_THRESHOLD

    def status(self, messages: list) -> str:
        used = estimate_tokens(messages)
        ratio = self.usage_ratio(messages)
        bar_len = 30
        filled = int(bar_len * ratio)
        bar = "█" * filled + "░" * (bar_len - filled)
        color = "\033[31m" if ratio > 0.85 else "\033[33m" if ratio > 0.6 else "\033[32m"
        return (
            f"  Context: [{color}{bar}\033[0m] "
            f"{ratio:.0%}  ({used:,} / {self.usable:,} tokens)"
        )


# ─────────────────────────────────────────────────────────────
# Auto-Compact：用摘要替换历史（对应 query.ts 的 autoCompact()）
#
# 真实实现：调用 Claude API，让模型对当前历史生成摘要。
# 这里用规则摘要做演示（不需要 API Key）。
#
# 关键：compact 前后消息数量差距很大，但 context 用量大幅下降。
# ─────────────────────────────────────────────────────────────
def compact_messages(messages: list) -> tuple[list, str]:
    """
    压缩消息历史，返回（压缩后的消息列表，摘要文本）。
    对应 commands/compact.ts 和 query.ts 里的 reactiveCompact()。

    真实代码会：
      1. 调用模型生成摘要（传入 COMPACT_SYSTEM_PROMPT）
      2. 用 SDKCompactBoundaryMessage 标记压缩点（供回放/调试）
      3. 保留系统消息（system prompt 不压缩）
      4. 用 [Compact] 摘要替换所有 user/assistant/tool 消息
    """
    system_messages = [m for m in messages if m["role"] == "system"]
    conversation = [m for m in messages if m["role"] != "system"]

    if len(conversation) < 4:
        return messages, "(消息太少，无需压缩)"

    # 生成摘要（真实版本调用模型；这里用规则版）
    user_count = sum(1 for m in conversation if m["role"] == "user")
    tool_count = sum(1 for m in conversation if m["role"] == "tool")
    topics = []
    for m in conversation:
        if m["role"] == "user" and isinstance(m.get("content"), str):
            text = m["content"][:80]
            topics.append(text)

    summary = (
        f"[对话摘要]\n"
        f"共 {len(conversation)} 条消息（{user_count} 条用户输入，{tool_count} 条工具结果）\n"
        f"主要话题：\n"
        + "\n".join(f"  - {t}" for t in topics[:5])
    )

    # 压缩后的消息：系统消息 + 一条摘要消息 + 最近 2 轮（保持连贯性）
    recent = conversation[-4:] if len(conversation) > 4 else conversation
    compacted = system_messages + [
        {"role": "user", "content": summary},    # 替换全部历史
        {"role": "assistant", "content": "好的，我已经了解之前的对话内容。"},
    ] + recent

    return compacted, summary


# ─────────────────────────────────────────────────────────────
# 系统 Prompt 的静态/动态边界（对应 systemPromptSections.ts）
#
# Claude Code 把系统 Prompt 分成两部分：
#   静态部分（所有 session 共享，可被 Claude 跨用户缓存）
#   ↓ SYSTEM_PROMPT_DYNAMIC_BOUNDARY ↓
#   动态部分（每个 session 不同：用户名、cwd、当前时间等）
#
# 这个设计让 50~70K token 的系统 Prompt 有极高的缓存命中率，
# 极大降低了每次 API 调用的成本。
# ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT_STATIC = """
你是 Claude Code，Anthropic 官方的 AI 编程助手。

[核心行为准则]
- 只做被要求的事，不添加没有要求的功能
- 高危操作（删除、覆写、推送）前先确认
- 如果不确定，问清楚再做

[工具使用规范]
- 读文件用 FileReadTool，不要用 cat/head
- 编辑文件用 FileEditTool，不要用 sed/awk
- 搜索用 GlobTool/GrepTool，不要用 find/grep

[输出格式]
- 简洁直接，不废话
- 引用具体文件时用 path:行号 格式
""".strip()

# ── 这是边界 ── 边界以上可以跨用户缓存，以下每次都不同 ──

def build_dynamic_prompt(username: str, cwd: str, date: str) -> str:
    """
    每次会话都不同的动态部分（对应 DANGEROUS_uncachedSystemPromptSection）。
    因为有用户名/cwd/日期，无法跨用户缓存。
    """
    return f"""
[当前环境]
用户: {username}
工作目录: {cwd}
当前日期: {date}
""".strip()

def build_full_system_prompt(username: str = "user", cwd: str = ".", date: str = "today") -> str:
    """
    组合静态 + 动态部分。
    静态部分在 Anthropic 侧有缓存，动态部分每次重算。
    """
    return SYSTEM_PROMPT_STATIC + "\n\n" + build_dynamic_prompt(username, cwd, date)


# ─────────────────────────────────────────────────────────────
# 演示
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import datetime

    print("═══ Layer 9：Context Window 管理演示 ═══\n")

    mgr = ContextWindowManager(model="deepseek-chat")
    messages = []

    print(f"模型: {mgr.model}  窗口: {mgr.window_size:,} tokens\n")

    # ── Part 1：模拟消息增长 ──────────────────────────────────
    print("── 模拟消息增长 ──\n")

    def add_exchange(user: str, assistant: str):
        messages.append({"role": "user", "content": user})
        messages.append({"role": "assistant", "content": assistant})

    for i in range(1, 12):
        add_exchange(
            f"任务 {i}: 请帮我分析这个函数的性能瓶颈，" + "x" * (400 * i),
            f"分析结果 {i}: 该函数的主要瓶颈在于..." + "y" * (300 * i),
        )
        print(mgr.status(messages))
        if mgr.should_compact(messages):
            print(f"\n  ⚡ 触发 Auto-Compact！（使用率 {mgr.usage_ratio(messages):.0%}）")
            before_count = len(messages)
            messages, summary = compact_messages(messages)
            print(f"  压缩：{before_count} 条 → {len(messages)} 条消息")
            print(f"  摘要预览：{summary[:100]}...")
            print(mgr.status(messages))
            print()
            break

    print()

    # ── Part 2：系统 Prompt 的静态/动态边界 ─────────────────
    print("── 系统 Prompt 缓存优化 ──\n")

    static_tokens = estimate_tokens([{"role": "system", "content": SYSTEM_PROMPT_STATIC}])
    print(f"静态部分（可跨用户缓存）: ~{static_tokens} tokens")

    today = datetime.date.today().strftime("%Y-%m-%d")
    dynamic = build_dynamic_prompt(username="alice", cwd="/Users/alice/project", date=today)
    dynamic_tokens = estimate_tokens([{"role": "system", "content": dynamic}])
    print(f"动态部分（每次重算）    : ~{dynamic_tokens} tokens")

    total_tokens = static_tokens + dynamic_tokens
    savings = static_tokens
    print(f"\n完整系统 Prompt: ~{total_tokens} tokens")
    print(f"缓存命中时节省: ~{savings} tokens  "
          f"({savings / total_tokens:.0%} 的系统 Prompt 无需重新计算)")
    print()
    print("这就是为什么 Claude Code 的响应速度比你预期的快——")
    print("那几万 token 的系统 Prompt 大多数情况下直接走缓存。")
