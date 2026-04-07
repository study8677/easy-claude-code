"""
Layer 6 — 高级机制：技能 / 多 Agent 协调 / 费用追踪
对应源码：claudecode_src/src/skills/ + coordinator/ + cost-tracker.ts
配套深挖：
  - 中文：docs/layers/l6-advanced.md
  - English: docs/layers/l6-advanced.en.md

核心问题：Claude Code 如何复用提示词？如何并行调度多个 Agent？怎么算钱？

你会看到：三个相互独立的系统：

  1. 技能系统（skills/）
     技能 = 带 frontmatter 的 Markdown 文件，在启动时编译成斜杠命令。
     用户可以在 ~/.claude/skills/ 放自己的 .md 文件来添加技能。
     真实代码：loadSkillsDir.ts + bundledSkills.ts

  2. 多 Agent 协调（coordinator/ + AgentTool/）
     一个 coordinator Claude 实例通过 AgentTool 生成子 Agent，
     每个子 Agent 拥有受限的工具集，完成子任务后用 SyntheticOutputTool 返回结果。
     真实代码：coordinatorMode.ts + tools/AgentTool/

  3. 费用追踪（cost-tracker.ts）
     每次 API 调用后累加 token 数，乘以单价得到 USD 费用。
     真实代码：cost-tracker.ts + bootstrap/state.js (全局累加器)

无需 API Key 即可运行。

运行后请回答：
  - 技能、工具、命令分别在解决什么问题？
  - 为什么 coordinator 和 worker 之间要有 structured output 边界？

跑完后下一步：
  1. 读 docs/layers/l6-advanced.md
  2. 看 docs/source-map.md 的“多 Agent / Structured Output 路径”
  3. 搜 `SYNTHETIC_OUTPUT_TOOL_NAME`、`createSyntheticOutputTool`、`ASYNC_AGENT_ALLOWED_TOOLS`
  4. 先开 `tools/SyntheticOutputTool/*` 和 `coordinator/coordinatorMode.ts`
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ═══════════════════════════════════════════════════════
# Part 1 — 技能系统（对应 skills/loadSkillsDir.ts）
# ═══════════════════════════════════════════════════════

SKILL_EXAMPLE = """\
---
name: run-tests
description: 运行测试套件并展示失败的用例
allowed_tools:
  - bash
---
1. 执行 `pytest -x --tb=short` 运行测试
2. 如果有失败，展示完整的错误信息
3. 给出简洁的修复建议
"""

@dataclass
class Skill:
    name: str
    description: str
    prompt_template: str
    allowed_tools: list[str] = field(default_factory=list)

def parse_skill(markdown: str) -> Skill | None:
    """
    解析技能文件（对应 loadSkillsDir.ts 的解析逻辑）。

    技能文件格式：
      ---
      name: skill-name
      description: "描述"
      allowed_tools: [bash, read_file]
      ---
      (提示词正文)
    """
    if not markdown.strip().startswith("---"):
        return None

    parts = markdown.split("---", 2)
    if len(parts) < 3:
        return None

    # 极简 YAML 解析（真实代码用 js-yaml）
    meta: dict[str, Any] = {}
    for line in parts[1].strip().splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip().strip('"')

    # allowed_tools 是列表格式
    tools_raw = meta.get("allowed_tools", "")
    if isinstance(tools_raw, str):
        tools = re.findall(r"[\w_]+", tools_raw)
    else:
        tools = list(tools_raw)

    return Skill(
        name=meta.get("name", "unnamed"),
        description=meta.get("description", ""),
        prompt_template=parts[2].strip(),
        allowed_tools=tools,
    )

def load_skills_dir(directory: Path) -> dict[str, Skill]:
    """
    扫描目录里的所有 .md 文件，编译成技能字典。
    对应 loadSkillsDir.ts 的 loadSkillsFromDir()。
    """
    skills = {}
    if not directory.exists():
        return skills
    for md_file in directory.glob("*.md"):
        skill = parse_skill(md_file.read_text(encoding="utf-8"))
        if skill:
            skills[skill.name] = skill
    return skills


# ═══════════════════════════════════════════════════════
# Part 2 — 多 Agent 协调（对应 coordinator/coordinatorMode.ts）
# ═══════════════════════════════════════════════════════

@dataclass
class AgentTask:
    task_id: str
    description: str
    allowed_tools: list[str]
    status: str = "pending"        # pending | running | done | error
    result: str | None = None

class CoordinatorAgent:
    """
    简化版 Coordinator（对应 coordinatorMode.ts）。

    真实 Claude Code 的协调模式：
      - coordinator 是一个普通的 Claude 实例，但拥有 AgentTool
      - 它通过调用 AgentTool 生成 worker Claude 实例
      - 每个 worker 只有受限工具集（ASYNC_AGENT_ALLOWED_TOOLS）
      - worker 完成后调用 SyntheticOutputTool 返回结果给 coordinator
      - coordinator 汇总所有结果，给出最终答案

    这个模式让 Claude Code 可以并行处理独立的子任务，
    比如同时读取多个文件、同时运行多个命令。
    """

    def __init__(self):
        self.tasks: list[AgentTask] = []
        self._task_counter = 0

    def spawn_worker(self, description: str, tools: list[str]) -> AgentTask:
        """
        生成一个 worker agent（对应 AgentTool 的 call()）。
        每个 worker 的工具集受限，防止子任务越权。
        """
        self._task_counter += 1
        task = AgentTask(
            task_id=f"worker-{self._task_counter}",
            description=description,
            allowed_tools=tools,
        )
        self.tasks.append(task)
        print(f"  [coordinator] 生成 Worker {task.task_id}: {description}")
        print(f"               允许工具: {', '.join(tools)}")
        return task

    def run_worker(self, task: AgentTask, mock_result: str):
        """模拟 worker 执行（真实版本会启动完整的 Agent Loop）"""
        task.status = "running"
        print(f"  [worker {task.task_id}] 执行中...")
        task.result = mock_result      # SyntheticOutputTool 的返回值
        task.status = "done"
        print(f"  [worker {task.task_id}] 完成: {mock_result[:60]}")

    def collect_results(self) -> str:
        """汇总所有 worker 结果（对应 coordinator 读取 SyntheticOutput）"""
        done = [t for t in self.tasks if t.status == "done"]
        return "\n".join(f"[{t.task_id}] {t.result}" for t in done)


# ═══════════════════════════════════════════════════════
# Part 3 — 费用追踪（对应 cost-tracker.ts）
# ═══════════════════════════════════════════════════════

# 每百万 token 价格（USD）
# 真实价格表在 claudecode_src/src/utils/modelCost.ts
MODEL_PRICES: dict[str, dict[str, float]] = {
    "claude-opus-4-6":     {"input": 15.0,  "output": 75.0},
    "claude-sonnet-4-6":   {"input":  3.0,  "output": 15.0},
    "claude-haiku-4-5":    {"input":  0.8,  "output":  4.0},
    "deepseek-chat":       {"input":  0.14, "output": 0.28},
    "deepseek-reasoner":   {"input":  0.55, "output": 2.19},
}

@dataclass
class CostTracker:
    """
    对应 cost-tracker.ts 的 addToTotalCostState() 和 getTotalCost()。
    每次 API 调用后记录 token 用量，实时计算累计费用。
    """
    model: str = "deepseek-chat"
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    call_count: int = 0

    def record(self, input_tokens: int, output_tokens: int):
        """每次 API 响应后调用一次"""
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.call_count += 1

    def total_cost_usd(self) -> float:
        prices = MODEL_PRICES.get(self.model, {"input": 0.0, "output": 0.0})
        return (
            self.total_input_tokens  * prices["input"] +
            self.total_output_tokens * prices["output"]
        ) / 1_000_000

    def summary(self) -> str:
        return (
            f"模型: {self.model}\n"
            f"API 调用次数: {self.call_count}\n"
            f"输入 token:   {self.total_input_tokens:,}\n"
            f"输出 token:   {self.total_output_tokens:,}\n"
            f"累计费用:     ${self.total_cost_usd():.6f} USD"
        )


# ═══════════════════════════════════════════════════════
# 演示
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":

    # ── Part 1：技能解析 ──────────────────────────
    print("═══ Part 1：技能系统 ═══\n")
    skill = parse_skill(SKILL_EXAMPLE)
    print(f"技能名称: {skill.name}")
    print(f"描述:     {skill.description}")
    print(f"允许工具: {skill.allowed_tools}")
    print(f"提示词:\n  {skill.prompt_template.replace(chr(10), chr(10) + '  ')}")
    print()

    # ── Part 2：多 Agent 协调 ─────────────────────
    print("═══ Part 2：多 Agent 协调 ═══\n")
    coordinator = CoordinatorAgent()

    # coordinator 把大任务拆成独立的子任务分发给 worker
    w1 = coordinator.spawn_worker("读取 README.MD 并提取关键信息", tools=["read_file"])
    w2 = coordinator.spawn_worker("检查 Python 文件语法", tools=["bash"])
    w3 = coordinator.spawn_worker("列出 examples/ 目录结构", tools=["bash", "read_file"])

    # 并行执行（真实版用 asyncio）
    coordinator.run_worker(w1, "README 以 9 个可运行示例为主线，配套 paths/layers/source-map 学习材料")
    coordinator.run_worker(w2, "所有 Python 文件语法检查通过")
    coordinator.run_worker(w3, "examples/ 包含 l1~l9 共 9 个示例文件")

    print(f"\n[coordinator] 汇总结果:\n{coordinator.collect_results()}")
    print()

    # ── Part 3：费用追踪 ──────────────────────────
    print("═══ Part 3：费用追踪 ═══\n")
    tracker = CostTracker(model="claude-sonnet-4-6")

    # 模拟 3 次 API 调用
    tracker.record(input_tokens=1200, output_tokens=300)   # 第 1 轮：用户消息
    tracker.record(input_tokens=1800, output_tokens=150)   # 第 2 轮：工具调用结果
    tracker.record(input_tokens=2100, output_tokens=450)   # 第 3 轮：最终回答

    print(tracker.summary())
    print()
    print("对比不同模型的费用（相同 token 量）:")
    for model in MODEL_PRICES:
        t = CostTracker(model=model)
        t.record(2100, 450)
        print(f"  {model:30s} ${t.total_cost_usd():.6f}")


# ═══════════════════════════════════════════════════════════
# 自检问题（跑完后回答，不要查代码）
# ═══════════════════════════════════════════════════════════
#
# 1. 技能（Skill）和斜杠命令（/model、/cost）的本质区别是什么？
#    技能的 prompt 是在哪一步被注入主循环的？
#
# 2. 费用追踪器在主线中处于哪一层？
#    它是从哪里拿到 input_tokens / output_tokens 数值的？
#
# 3. 协调者（Coordinator）为什么只能看到 SyntheticOutput，
#    而不能直接观察子 agent 的中间消息历史？
