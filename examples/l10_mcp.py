"""
Layer 10 — MCP 协议：外部工具如何进入 Claude Code
对应源码：claudecode_src/src/tools/MCPTool/ + claudecode_src/src/services/mcp/
配套深挖：
  - 中文：docs/layers/l13-mcp-hooks-plugins.md
  - English: docs/layers/l13-mcp-hooks-plugins.en.md

核心问题：Claude Code 怎样把来自外部 MCP server 的工具和内置工具统一管理？

你会看到：
  MCP（Model Context Protocol）是 Anthropic 制定的开放协议，
  允许任何外部服务以 JSON-RPC 形式暴露工具给 Claude Code 使用。

  Claude Code 作为 MCP Client：
    1. 在启动时连接配置好的 MCP server（stdio 或 http/sse）
    2. 调用 tools/list 获取工具列表
    3. 把每个 MCP 工具包装成 MCPTool 实例，注入到 getTools() 的统一列表里
    4. 模型选中 MCP 工具时，通过 tools/call 请求 MCP server 执行

  关键设计：MCPTool 实现了和 BashTool / FileReadTool 完全相同的接口（Tool.ts 的 schema + execute），
  所以主循环（queryLoop）完全不知道"这个工具是不是 MCP 的"。

无需 API Key，直接运行：
  python examples/l10_mcp.py

跑完后下一步：
  1. 读 docs/layers/l13-mcp-hooks-plugins.md
  2. 搜 MCPTool、McpClient、tools/list、tools/call
  3. 看 claudecode_src/src/tools/MCPTool/ 和 src/services/mcp/
"""

import json
import asyncio
from typing import Any

# ─────────────────────────────────────────────────────────────────
# Part 1：MCP Server（最小化实现）
#
# 真实的 MCP server 是一个独立进程，通过 stdio 或 SSE 通信。
# 这里用 in-process 的对象模拟，保留 JSON-RPC 消息结构，
# 让你看清 Claude Code MCP Client 所看到的接口形状。
# ─────────────────────────────────────────────────────────────────

class MockMCPServer:
    """
    模拟 MCP Server 暴露两个工具：
      - read_file：读取文件内容
      - list_directory：列出目录内容

    真实 MCP server 的协议参考：https://modelcontextprotocol.io/spec
    """

    def handle(self, request: dict) -> dict:
        method = request.get("method")
        params = request.get("params", {})
        req_id = request.get("id")

        if method == "initialize":
            return self._ok(req_id, {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "mock-file-server", "version": "0.1.0"},
            })

        if method == "tools/list":
            return self._ok(req_id, {"tools": self._tool_schemas()})

        if method == "tools/call":
            tool_name = params.get("name")
            args = params.get("arguments", {})
            result = self._execute(tool_name, args)
            return self._ok(req_id, {
                "content": [{"type": "text", "text": result}],
                "isError": False,
            })

        return self._error(req_id, -32601, f"Method not found: {method}")

    # ── 工具定义（对应 tools/list 响应，Claude Code MCPTool 用这个 build schema）──
    def _tool_schemas(self):
        return [
            {
                "name": "read_file",
                "description": "读取指定路径的文件内容（示例：相对路径）",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "文件路径"},
                    },
                    "required": ["path"],
                },
            },
            {
                "name": "list_directory",
                "description": "列出目录下的文件和子目录",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "目录路径，默认当前目录"},
                    },
                },
            },
        ]

    # ── 工具执行（对应 tools/call 请求，Claude Code MCPTool.execute() 会发这个）──
    def _execute(self, name: str, args: dict) -> str:
        import os
        if name == "read_file":
            path = args.get("path", "")
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read(1000)
                return content or "(空文件)"
            except FileNotFoundError:
                return f"[错误] 文件不存在: {path}"
            except Exception as e:
                return f"[错误] {e}"

        if name == "list_directory":
            path = args.get("path", ".")
            try:
                entries = os.listdir(path)
                lines = []
                for e in sorted(entries)[:20]:
                    full = os.path.join(path, e)
                    tag = "/" if os.path.isdir(full) else ""
                    lines.append(f"  {e}{tag}")
                return "\n".join(lines) or "(空目录)"
            except Exception as e:
                return f"[错误] {e}"

        return f"[错误] 未知工具: {name}"

    def _ok(self, req_id, result): return {"jsonrpc": "2.0", "id": req_id, "result": result}
    def _error(self, req_id, code, msg): return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": msg}}


# ─────────────────────────────────────────────────────────────────
# Part 2：MCP Client（对应 claudecode_src/src/services/mcp/）
#
# 真实的 McpClient 通过 stdio / SSE 与 server 通信。
# 这里直接调用 server 对象，保留消息格式不变。
# ─────────────────────────────────────────────────────────────────

class MockMCPClient:
    """
    对应 Claude Code 里的 McpClient。
    负责：连接 server → tools/list → 提供工具列表给 Claude Code 主流程。
    """

    def __init__(self, server: MockMCPServer):
        self._server = server
        self._next_id = 1

    def _call(self, method: str, params: dict = None) -> dict:
        req = {"jsonrpc": "2.0", "id": self._next_id, "method": method}
        if params:
            req["params"] = params
        self._next_id += 1
        return self._server.handle(req)

    def initialize(self):
        resp = self._call("initialize", {"protocolVersion": "2024-11-05",
                                          "clientInfo": {"name": "mock-claude-code", "version": "1.0"}})
        return resp.get("result", {})

    def list_tools(self) -> list[dict]:
        """对应 Claude Code 启动时调用 tools/list 拿到工具列表。"""
        resp = self._call("tools/list")
        return resp.get("result", {}).get("tools", [])

    def call_tool(self, name: str, arguments: dict) -> str:
        """对应 MCPTool.execute()：把 tool_use block 转成 tools/call 请求。"""
        resp = self._call("tools/call", {"name": name, "arguments": arguments})
        result = resp.get("result", {})
        content = result.get("content", [])
        return "\n".join(c.get("text", "") for c in content if c.get("type") == "text")


# ─────────────────────────────────────────────────────────────────
# Part 3：MCPTool 包装层（对应 claudecode_src/src/tools/MCPTool/）
#
# 这是最关键的设计：MCPTool 实现和 BashTool 相同的接口。
# queryLoop 只调用 tool.execute(args)，不关心底层是 bash 还是 MCP。
# ─────────────────────────────────────────────────────────────────

class MCPTool:
    """
    对应 claudecode_src/src/tools/MCPTool/MCPTool.ts。

    Claude Code 里 MCPTool 实现了 Tool 接口：
      - schema: 提供给模型的 JSON schema（来自 MCP server 的 inputSchema）
      - execute: 执行时调用 McpClient.callTool()

    这让 queryLoop 对所有工具一视同仁——
    "是不是 MCP 工具"只在工具注册阶段知道，主循环不感知。
    """

    def __init__(self, mcp_client: MockMCPClient, tool_def: dict):
        self._client = mcp_client
        self._def = tool_def
        self.name = tool_def["name"]

    def schema(self) -> dict:
        """提供给模型的 JSON schema（这就是模型"看到"的工具形状）。"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self._def.get("description", ""),
                "parameters": self._def.get("inputSchema", {"type": "object", "properties": {}}),
            }
        }

    def execute(self, arguments: dict) -> str:
        """执行工具：转发给 MCP server 的 tools/call。"""
        return self._client.call_tool(self.name, arguments)


# ─────────────────────────────────────────────────────────────────
# Part 4：工具注册（对应 getTools() + buildTool()）
#
# Claude Code 的 getTools() 把内置工具和 MCP 工具合并成一个列表，
# 一起传给模型。模型不需要知道哪些是 MCP 的。
# ─────────────────────────────────────────────────────────────────

def build_tool_registry(mcp_client: MockMCPClient) -> dict[str, MCPTool]:
    """
    对应 getTools() 里为每个 MCP server 调用 tools/list，
    然后把结果合并进全局工具表。
    """
    tools = {}
    raw_tools = mcp_client.list_tools()
    for raw in raw_tools:
        tool = MCPTool(mcp_client, raw)
        tools[tool.name] = tool
    return tools


# ─────────────────────────────────────────────────────────────────
# Part 5：演示主流程
# ─────────────────────────────────────────────────────────────────

def demo():
    print("=" * 60)
    print("Layer 10 — MCP 协议演示")
    print("=" * 60)

    # 1. 启动 MCP server + client（真实场景是 stdio 子进程或 SSE）
    print("\n[Step 1] 初始化 MCP server 和 client")
    server = MockMCPServer()
    client = MockMCPClient(server)
    init_result = client.initialize()
    print(f"  server 名称: {init_result.get('serverInfo', {}).get('name')}")
    print(f"  协议版本: {init_result.get('protocolVersion')}")

    # 2. 拉取工具列表（对应 Claude Code 启动时的 tools/list）
    print("\n[Step 2] 拉取 MCP 工具列表（tools/list）")
    tool_registry = build_tool_registry(client)
    for name, tool in tool_registry.items():
        schema = tool.schema()
        desc = schema["function"]["description"]
        print(f"  工具注册: {name!r:20s} — {desc}")

    # 3. 展示模型看到的 schema（这是传给模型的 tools 参数）
    print("\n[Step 3] 模型看到的工具 schema（等同于内置工具）")
    for name, tool in tool_registry.items():
        schema_json = json.dumps(tool.schema(), ensure_ascii=False, indent=4)
        print(f"\n  [{name}]")
        for line in schema_json.splitlines():
            print(f"    {line}")

    # 4. 模拟 queryLoop 执行 MCP 工具（对应 MCPTool.execute()）
    print("\n[Step 4] 模拟 queryLoop 执行 MCP 工具（tools/call）")
    calls = [
        ("list_directory", {"path": "."}),
        ("read_file", {"path": "README.MD"}),
        ("read_file", {"path": "不存在的文件.txt"}),
    ]
    for tool_name, args in calls:
        tool = tool_registry.get(tool_name)
        if not tool:
            print(f"  [未找到工具] {tool_name}")
            continue
        print(f"\n  → 执行工具: {tool_name}({args})")
        result = tool.execute(args)
        preview = result[:200].replace("\n", "\n    ")
        print(f"  ← 工具结果:\n    {preview}")
        if len(result) > 200:
            print(f"    ...(截断，共 {len(result)} 字符)")

    # 5. 架构对比总结
    print("\n" + "=" * 60)
    print("架构总结")
    print("=" * 60)
    print("""
  内置工具（BashTool）                MCP 工具（MCPTool）
  ──────────────────────────────────────────────────────
  schema()  → 硬编码在 TypeScript     schema()  → 来自 tools/list 动态拉取
  execute() → 本地 subprocess         execute() → 通过 tools/call 转发给 server
  ──────────────────────────────────────────────────────
  queryLoop 对两者调用方式完全相同：
    result = await tool.execute(args)

  关键设计：MCPTool 实现了 Tool 接口，
  所以主循环（queryLoop）不需要知道"这是不是 MCP 工具"。
  工具来源的多样性被封装在注册层，主线保持简洁。
""")

    print("下一步：")
    print("  搜 MCPTool、McpClient、ASYNC_AGENT_ALLOWED_TOOLS")
    print("  看 claudecode_src/src/tools/MCPTool/ 和 src/services/mcp/")


# ─────────────────────────────────────────────────────────────────
# 自检问题（跑完后回答）
# ─────────────────────────────────────────────────────────────────
CHECKPOINT_QUESTIONS = """
跑完后回答以下问题（不查源码，只靠刚才的演示）：

  1. MCP server 用什么方法告诉 Claude Code "我有哪些工具"？
     提示：回顾 Part 2 的 list_tools()。

  2. MCPTool.execute() 和 BashTool.execute() 对 queryLoop 来说有什么不同？
     提示：queryLoop 根本不知道 ___________。

  3. 如果 MCP server 新增了一个工具，Claude Code 什么时候会感知到？
     提示：工具列表在 _________ 阶段拉取。
"""

if __name__ == "__main__":
    demo()
    print(CHECKPOINT_QUESTIONS)
