"""
Tests for MCP Platform (Mission 37).
"""

import json
import pytest
from genesis.mcp import MCPServer, MCPTool, MCPRequest, MCPResponse


class TestMCPServer:
    def test_create_server(self):
        s = MCPServer("genesis", "1.0.0")
        assert s.name == "genesis"
        assert s.version == "1.0.0"

    def test_list_tools_includes_builtins(self):
        s = MCPServer()
        tools = s.list_tools()
        names = [t["name"] for t in tools]
        assert "list_tools" in names
        assert "server_info" in names

    def test_register_tool(self):
        s = MCPServer()
        s.register_tool(MCPTool("my_tool", "My tool", {"type": "object"}), lambda x: x)
        tools = s.list_tools()
        assert any(t["name"] == "my_tool" for t in tools)

    def test_handle_known_tool(self):
        s = MCPServer()
        s.register_tool(MCPTool("echo", "Echo", {"type": "object", "properties": {"msg": {"type": "string"}}}),
                        lambda msg: {"echo": msg})
        req = MCPRequest("echo", {"msg": "hello"})
        resp = s.handle_request(req)
        assert resp.content["echo"] == "hello"
        assert not resp.is_error

    def test_handle_unknown_tool(self):
        s = MCPServer()
        req = MCPRequest("unknown", {})
        resp = s.handle_request(req)
        assert resp.is_error
        assert "Unknown" in resp.content["error"]

    def test_handle_tool_error(self):
        s = MCPServer()
        s.register_tool(MCPTool("crash", "Crashes", {}),
                        lambda: (_ for _ in ()).throw(RuntimeError("boom")))
        req = MCPRequest("crash", {})
        resp = s.handle_request(req)
        assert resp.is_error
        assert "boom" in resp.content["error"]

    def test_server_info_tool(self):
        s = MCPServer("my_server", "2.0")
        req = MCPRequest("server_info", {})
        resp = s.handle_request(req)
        assert resp.content["name"] == "my_server"
        assert resp.content["version"] == "2.0"

    def test_mcp_response_to_dict(self):
        resp = MCPResponse({"result": "ok"})
        d = resp.to_dict()
        assert "content" in d
        assert d["isError"] is False

    def test_mcp_error_response_to_dict(self):
        resp = MCPResponse({"error": "fail"}, is_error=True)
        d = resp.to_dict()
        assert d["isError"] is True


class TestMCPServerStdio:
    def test_ping_pong(self, capsys):
        s = MCPServer()
        import io
        import sys
        test_input = json.dumps({"type": "ping", "id": "1"}) + "\n"
        old_stdin = sys.stdin
        sys.stdin = io.StringIO(test_input)
        try:
            s.run_stdio()
        except SystemExit:
            pass
        finally:
            sys.stdin = old_stdin
        captured = capsys.readouterr()
        output = json.loads(captured.out.strip())
        assert output["type"] == "pong"
        assert output["id"] == "1"

    def test_list_tools_via_stdio(self, capsys):
        s = MCPServer()
        import io
        import sys
        test_input = json.dumps({"type": "list_tools", "id": "2"}) + "\n"
        old_stdin = sys.stdin
        sys.stdin = io.StringIO(test_input)
        try:
            s.run_stdio()
        except SystemExit:
            pass
        finally:
            sys.stdin = old_stdin
        captured = capsys.readouterr()
        output = json.loads(captured.out.strip())
        assert output["type"] == "tools"
        assert len(output["tools"]) >= 2

    def test_call_tool_via_stdio(self, capsys):
        s = MCPServer()
        import io
        import sys
        test_input = json.dumps({"type": "call_tool", "id": "3", "tool": "server_info", "arguments": {}}) + "\n"
        old_stdin = sys.stdin
        sys.stdin = io.StringIO(test_input)
        try:
            s.run_stdio()
        except SystemExit:
            pass
        finally:
            sys.stdin = old_stdin
        captured = capsys.readouterr()
        output = json.loads(captured.out.strip())
        assert output["type"] == "result"
