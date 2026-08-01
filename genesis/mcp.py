from __future__ import annotations

import json
import sys
from typing import Any


class MCPTool:
    name: str
    description: str
    parameters: dict[str, Any]

    def __init__(self, name: str, description: str, parameters: dict[str, Any]):
        self.name = name
        self.description = description
        self.parameters = parameters

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.parameters,
        }


class MCPRequest:
    def __init__(self, tool: str, arguments: dict[str, Any]):
        self.tool = tool
        self.arguments = arguments


class MCPResponse:
    def __init__(self, content: Any, is_error: bool = False):
        self.content = content
        self.is_error = is_error

    def to_dict(self) -> dict[str, Any]:
        return {
            "content": [{"type": "text", "text": json.dumps(self.content, indent=2, default=str)}],
            "isError": self.is_error,
        }


class MCPServer:
    def __init__(self, name: str = "genesis", version: str = "1.0.0"):
        self.name = name
        self.version = version
        self._tools: dict[str, MCPTool] = {}
        self._handlers: dict[str, callable] = {}
        self._register_core_tools()

    def register_tool(self, tool: MCPTool, handler: callable):
        self._tools[tool.name] = tool
        self._handlers[tool.name] = handler

    def list_tools(self) -> list[dict[str, Any]]:
        return [t.to_dict() for t in self._tools.values()]

    def handle_request(self, request: MCPRequest) -> MCPResponse:
        handler = self._handlers.get(request.tool)
        if not handler:
            return MCPResponse({"error": f"Unknown tool: {request.tool}"}, is_error=True)
        try:
            result = handler(**request.arguments)
            return MCPResponse(result)
        except Exception as e:
            return MCPResponse({"error": str(e)}, is_error=True)

    def _register_core_tools(self):
        self.register_tool(
            MCPTool("list_tools", "List all available MCP tools", {}),
            lambda: self.list_tools(),
        )
        self.register_tool(
            MCPTool("server_info", "Get server information", {}),
            lambda: {"name": self.name, "version": self.version},
        )

    def run_stdio(self):
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue

            msg_type = msg.get("type", "")
            msg_id = msg.get("id", "")

            if msg_type == "ping":
                self._send({"type": "pong", "id": msg_id})
            elif msg_type == "list_tools":
                self._send({"type": "tools", "id": msg_id, "tools": self.list_tools()})
            elif msg_type == "call_tool":
                request = MCPRequest(tool=msg["tool"], arguments=msg.get("arguments", {}))
                response = self.handle_request(request)
                self._send({
                    "type": "result" if not response.is_error else "error",
                    "id": msg_id,
                    **response.to_dict(),
                })
            else:
                self._send({"type": "error", "id": msg_id, "error": f"Unknown type: {msg_type}"})

    def _send(self, msg: dict[str, Any]):
        sys.stdout.write(json.dumps(msg) + "\n")
        sys.stdout.flush()
