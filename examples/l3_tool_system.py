"""
Layer 3 — 工具系统
对应源码：claudecode_src/src/Tool.ts + tools.ts + tools/*/
配套深挖：
  - 中文：docs/layers/l3-tool-system.md
  - English: docs/layers/l3-tool-system.en.md

核心问题：Claude Code 怎么定义、注册、调用工具？

你会看到：每个工具 = JSON Schema（给模型看）+ Python 函数（在本地执行）。
  Tool.ts 定义接口，tools/ 下每个目录是一个工具的完整实现，
  tools.ts 是注册表，把所有工具汇总成模型可以调用的列表。

这个文件无需 API Key 即可运行，直接演示工具的定义和分发逻辑。

运行后请回答：
  - 为什么 schema 和 execute 必须分开？
  - 工具注册表在 Agent 系统里承担了什么角色？
"""

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

# ─────────────────────────────────────────────
# 工具接口（对应 Tool.ts 的 ToolDef / buildTool()）
#
# 真实 Tool.ts 里的关键字段：
#   name: string
#   description: string          ← 模型理解"这个工具是干什么的"
#   inputSchema: ToolInputJSONSchema  ← 模型知道传什么参数
#   call(input, context): Promise<ToolResult>  ← 实际执行
# ─────────────────────────────────────────────
@dataclass
class ToolDef:
    name: str
    description: str
    schema: dict          # JSON Schema —— 这一份发给模型
    execute: Callable     # Python 函数 —— 这一份在本地跑
    needs_permission: bool = False   # 对应 BashTool 的 bashToolHasPermission


# ─────────────────────────────────────────────
# 安全层（对应 bashPermissions.ts + bashSecurity.ts）
# BashTool 有完整的权限检查和危险命令检测，这里做简化版
# ─────────────────────────────────────────────
DANGEROUS = {"rm", "sudo", "chmod", "chown", "mkfs", "dd", ":(){:", "fork"}

def is_dangerous(command: str) -> bool:
    first_token = command.strip().split()[0] if command.strip() else ""
    return first_token in DANGEROUS

def ask_permission(tool_name: str, args: dict) -> bool:
    """对应 canUseTool()：在执行高危操作前询问用户"""
    cmd = args.get("command", "")
    if is_dangerous(cmd):
        print(f"\n  [权限] 高危命令: {cmd}")
        answer = input("  是否允许执行？[y/N] ").strip().lower()
        return answer == "y"
    return True    # 非危险命令默认放行


# ─────────────────────────────────────────────
# 工具实现（对应 tools/BashTool、FileReadTool、FileEditTool、FileWriteTool）
# ─────────────────────────────────────────────
def _bash(args: dict) -> str:
    result = subprocess.run(
        args["command"], shell=True, capture_output=True, text=True, timeout=30
    )
    out = (result.stdout + result.stderr).strip()
    return out[:3000] if len(out) > 3000 else out or "(无输出)"

def _read_file(args: dict) -> str:
    path = Path(args["path"])
    if not path.exists():
        return f"Error: 文件不存在 {path}"
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    limit = args.get("limit", 200)
    result = "\n".join(lines[:limit])
    if len(lines) > limit:
        result += f"\n... (省略 {len(lines) - limit} 行)"
    return result

def _write_file(args: dict) -> str:
    path = Path(args["path"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(args["content"], encoding="utf-8")
    return f"已写入 {path} ({len(args['content'])} 字节)"

def _edit_file(args: dict) -> str:
    path = Path(args["path"])
    if not path.exists():
        return f"Error: 文件不存在 {path}"
    text = path.read_text(encoding="utf-8")
    if args["old_str"] not in text:
        return f"Error: 未找到要替换的文本"
    new_text = text.replace(args["old_str"], args["new_str"], 1)
    path.write_text(new_text, encoding="utf-8")
    return "编辑成功"


# ─────────────────────────────────────────────
# 工具注册表（对应 tools.ts 的 getTools()）
#
# 真实 tools.ts 里：
#   export function getTools(context: ToolUseContext): Tools {
#     return [BashTool, FileReadTool, FileEditTool, ...]
#   }
# ─────────────────────────────────────────────
TOOL_REGISTRY: dict[str, ToolDef] = {
    t.name: t for t in [
        ToolDef(
            name="bash",
            description="执行 shell 命令，返回 stdout+stderr",
            schema={
                "type": "object",
                "properties": {"command": {"type": "string", "description": "要执行的命令"}},
                "required": ["command"],
            },
            execute=_bash,
            needs_permission=True,
        ),
        ToolDef(
            name="read_file",
            description="读取文件内容",
            schema={
                "type": "object",
                "properties": {
                    "path":  {"type": "string", "description": "文件路径"},
                    "limit": {"type": "integer", "description": "最多读取行数"},
                },
                "required": ["path"],
            },
            execute=_read_file,
            needs_permission=False,   # 只读，无需确认
        ),
        ToolDef(
            name="write_file",
            description="写入文件（覆盖）",
            schema={
                "type": "object",
                "properties": {
                    "path":    {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
            execute=_write_file,
            needs_permission=True,
        ),
        ToolDef(
            name="edit_file",
            description="精确替换文件中的一段文本",
            schema={
                "type": "object",
                "properties": {
                    "path":    {"type": "string"},
                    "old_str": {"type": "string", "description": "要被替换的原始文本"},
                    "new_str": {"type": "string", "description": "替换后的新文本"},
                },
                "required": ["path", "old_str", "new_str"],
            },
            execute=_edit_file,
            needs_permission=True,
        ),
    ]
}


def get_openai_schemas() -> list[dict]:
    """
    把注册表转换成 OpenAI 工具格式——这才是发给模型的内容。
    对应 tools.ts 里把 ToolDef 转换成 API 请求格式的逻辑。
    """
    return [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description,
                "parameters": t.schema,
            },
        }
        for t in TOOL_REGISTRY.values()
    ]


def dispatch(name: str, args: dict) -> str:
    """
    工具分发（对应 Tool.ts 的 call() 方法）。
    根据工具名找到实现，做权限检查，执行，返回结果字符串。
    """
    tool = TOOL_REGISTRY.get(name)
    if not tool:
        return f"Error: 未知工具 '{name}'"
    if tool.needs_permission and not ask_permission(name, args):
        return "Error: 用户拒绝了权限请求"
    try:
        return tool.execute(args)
    except Exception as e:
        return f"Error: {e}"


# ─────────────────────────────────────────────
# 演示：打印注册表 + 手动调用几个工具
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("═══ 已注册的工具（这是模型看到的 JSON Schema）═══\n")
    for schema in get_openai_schemas():
        f = schema["function"]
        print(f"  [{f['name']}]  {f['description']}")
        props = f["parameters"].get("properties", {})
        for p, v in props.items():
            req = "必填" if p in f["parameters"].get("required", []) else "可选"
            print(f"    - {p} ({v['type']}, {req}): {v.get('description', '')}")
        print()

    print("═══ 手动分发工具调用 ═══\n")

    # 模拟模型发出的工具调用
    print("bash: ls -la .")
    print(dispatch("bash", {"command": "ls -la ."}))
    print()

    print("read_file: README.MD (前 5 行)")
    print(dispatch("read_file", {"path": "README.MD", "limit": 5}))
    print()

    print("未知工具: fly_to_moon")
    print(dispatch("fly_to_moon", {}))
