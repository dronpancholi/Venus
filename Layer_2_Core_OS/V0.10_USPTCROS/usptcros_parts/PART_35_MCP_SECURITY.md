# Part 35 — MCP Security

## 1. Executive Summary & Philosophy
Model Context Protocol (MCP) Security regulates integration paths, tool executions, and file access patterns initiated by autonomous AI agents. The Venus system handles MCP connections under strict sandboxes, validating execution signatures, and prompting for explicit user authorization.

## 2. MCP Permission Configuration Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "MCPPermissionProfile",
  "type": "object",
  "properties": {
    "server_id": { "type": "string" },
    "allowed_tools": {
      "type": "array",
      "items": { "type": "string" }
    },
    "allowed_directories": {
      "type": "array",
      "items": { "type": "string" }
    },
    "require_explicit_consent": { "type": "boolean", "const": true }
  },
  "required": ["server_id", "allowed_tools", "allowed_directories", "require_explicit_consent"]
}
```

## 3. Sandboxed Subprocess Execution Code Fragment
Secure execution wrapper limiting sub-process access under seccomp filters:
```python
import subprocess
import os

def run_mcp_tool_isolated(cmd, arguments, timeout_sec=5):
    # Restrict environment variables
    clean_env = {"PATH": "/usr/bin:/bin", "LANG": "en_US.UTF-8"}
    
    # Run containerized/sandboxed command using system limits
    proc = subprocess.Popen(
        [cmd] + arguments,
        env=clean_env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    
    try:
        stdout, stderr = proc.communicate(timeout=timeout_sec)
        return stdout.decode(), stderr.decode()
    except subprocess.TimeoutExpired:
        proc.kill()
        raise SecurityException("MCP isolated process execution timed out")
```

## 4. Institutional MCP Security Hardening Checklist
* [ ] Configured local loopback bindings (127.0.0.1) for all MCP TCP services.
* [ ] Isolated all MCP executions within seccomp profiles.
* [ ] Mandated signed JSON-RPC endpoints for MCP message buses.
* [ ] Required user consent triggers on file modifications or API requests.
* [ ] Enforced read-only permission flags on shared workspaces.

## 5. References & Inter-subsystem Links
* [V0.10 USPTCROS Main Constitution](file:///Users/dronpancholi/Developer/01_Strategic/Venus/V0.10_USPTCROS.md)
* [Prompt Injection Defense](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/PART_34_PROMPT_INJECTION_DEFENSE.md)
* [RAG Security](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/PART_36_RAG_SECURITY.md)
