"""
Layer 1 — 启动与入口
对应源码：claudecode_src/src/main.tsx + entrypoints/ + setup.ts
配套深挖：
  - 中文：docs/layers/l1-startup.md
  - English: docs/layers/l1-startup.en.md

核心问题：`claude` 命令敲下去之后，真正发生了什么？

你会看到：
  1. headlessProfilerCheckpoint() 打时间戳，追踪每个启动阶段耗时
  2. setup.ts 检测工作目录、API Key、权限模式，建立 session_id
  3. entrypoints/ 根据命令行参数分流到不同模式

这个文件是简化版演示，无需 API Key 即可运行。

运行后请回答：
  - 启动路径和 query 路径是在什么地方接起来的？
  - 为什么模式分流要发生在真正进入 Agent Loop 之前？
"""

import sys
import os
import json
import uuid
import time
from pathlib import Path

# ─────────────────────────────────────────────
# 1. 性能检查点（对应 headlessProfiler.ts）
#    Claude Code 在每个启动阶段都打一个时间戳，
#    方便分析"首次渲染"到底卡在哪一步。
# ─────────────────────────────────────────────
_t0 = time.monotonic()

def checkpoint(name: str):
    elapsed = (time.monotonic() - _t0) * 1000
    print(f"  [checkpoint] {name:30s} +{elapsed:.1f}ms")


# ─────────────────────────────────────────────
# 2. 配置加载（对应 setup.ts + getGlobalConfig()）
#    读取 ~/.myagent/config.json，获取工作目录、权限模式等。
#    文件不存在时使用默认值——Claude Code 同样如此。
# ─────────────────────────────────────────────
def load_config() -> dict:
    config_path = Path.home() / ".myagent" / "config.json"
    if config_path.exists():
        return json.loads(config_path.read_text())
    # 默认配置，对应 Claude Code 首次运行时的初始状态
    return {
        "permission_mode": "default",   # default | acceptEdits | bypassPermissions
        "cwd": str(Path.cwd()),
        "model": "deepseek-chat",
    }


# ─────────────────────────────────────────────
# 3. 环境初始化（对应 setup.ts 的 setup() 函数）
#    验证工作目录存在，生成 session_id，注入环境变量。
# ─────────────────────────────────────────────
def setup(config: dict) -> str:
    checkpoint("setup_start")

    cwd = Path(config["cwd"])
    assert cwd.exists(), f"工作目录不存在: {cwd}"

    # 每次启动生成唯一 session_id，用于日志追踪和费用统计
    session_id = str(uuid.uuid4())[:8]
    os.environ["AGENT_SESSION_ID"] = session_id
    os.environ["AGENT_CWD"] = str(cwd)

    api_key = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("  [警告] 未检测到 API Key，请设置 DEEPSEEK_API_KEY 或 ANTHROPIC_API_KEY")

    checkpoint("setup_done")
    return session_id


# ─────────────────────────────────────────────
# 4. 入口分流（对应 main.tsx 的 CLI 解析 + entrypoints/ 目录）
#    根据命令行参数决定以哪种模式运行。
#    Claude Code 的真实分流逻辑在 entrypoints/ 下：
#      - interactive.tsx   → 交互式 REPL
#      - nonInteractive.ts → --print 模式
#      - apiServer.ts      → serve 模式
# ─────────────────────────────────────────────
def run_interactive_repl(initial_prompt: str | None = None):
    """交互式模式：用户持续输入，直到 /exit"""
    print("\n[模式] 交互式 REPL — 输入 /exit 退出")
    if initial_prompt:
        print(f"[初始提示] {initial_prompt}")
    while True:
        try:
            text = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            break
        if text in ("/exit", "exit", "quit"):
            break
        if text.startswith("/"):
            print(f"Assistant: (处理斜杠命令 '{text}' — 见 Layer 5 示例)")
        else:
            print(f"Assistant: (调用 Agent Loop 处理 '{text}' — 见 Layer 2 示例)")


def run_non_interactive(prompt: str):
    """非交互模式：执行一个任务后退出，对应 claude --print '...' """
    print(f"\n[模式] 非交互 — 执行: {prompt}")
    print("Assistant: (处理完毕，退出)")
    sys.exit(0)


def run_server_mode(port: int = 8080):
    """服务器模式：监听 HTTP，对应 claude serve"""
    print(f"\n[模式] HTTP 服务器 — 监听 :{port}")
    print("(真实实现在 claudecode_src/src/server/ 目录下)")


def main():
    checkpoint("main_entry")     # 对应 profileCheckpoint('main_tsx_entry')

    config = load_config()
    session_id = setup(config)

    checkpoint("ready")
    print(f"\n会话 {session_id} 已在 {config['cwd']} 启动")
    print(f"权限模式: {config['permission_mode']}  模型: {config['model']}\n")

    # ── 根据参数分流（对应 main.tsx 的 commander 解析）──
    args = sys.argv[1:]

    if "--print" in args:
        idx = args.index("--print")
        prompt = args[idx + 1] if idx + 1 < len(args) else ""
        run_non_interactive(prompt)

    elif "serve" in args:
        run_server_mode()

    else:
        initial = " ".join(args) if args else None
        run_interactive_repl(initial)


if __name__ == "__main__":
    main()
