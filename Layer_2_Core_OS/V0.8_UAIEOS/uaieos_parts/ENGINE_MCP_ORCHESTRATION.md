# UAIEOS Engine: MCP Orchestration Engine

This document defines the operational architecture, connection management systems, message brokerage, and validation protocols for the Model Context Protocol (MCP) Orchestration Engine. This engine manages runtime server subprocesses, routes JSON-RPC packets, and enforces security policies.

---

## 1. Engine Overview & Core Functions

The MCP Orchestration Engine runs as a background broker inside the host workspace, supervising communication channels between clients and external servers.

```
                  [MCP Client (Agent Engine)]
                               │
                               ▼
                   [MCP Orchestration Engine]
                      ├── JSON-RPC Message Broker
                      ├── Connection Supervisor
                      └── Security ACL Gatekeeper
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
    [Stdio Subprocesses]                 [Remote SSE Services]
```

### 1.1 Core Functions
1.  **Server Process Supervision:** Spawns and manages Stdio subprocesses, monitoring memory utilization and exit codes.
2.  **JSON-RPC Brokerage:** Routes requests, responses, and notifications across Stdio pipelines and SSE endpoints.
3.  **Security Policy Enforcement:** Filters tool calls and resource URI queries against configured ACL boundaries.
4.  **Protocol Handshake Management:** Coordinates the initial capability handshake and version checks.

---

## 2. Technical Architecture & Protocols

### 2.1 Transport Lifecycle Management
The broker operates as an asynchronous event loop. Standard message traffic must follow the JSON-RPC 2.0 specifications.

### 2.2 Version Negotiation Logic
During initialization, the client sends proposed versions. The broker runs a checks sequence:
1.  Checks if the proposed version is in the supported version range.
2.  If yes, responds with the version match.
3.  If no, evaluates if backwards compatibility is possible.
4.  If not, terminates connection and raises a `ProtocolVersionMismatch` error.

---

## 3. Data Protocols & JSON-RPC Schemas

### 3.1 JSON-RPC Request Envelope
Any request sent from the agent client to a server must conform to this schema:

```json
{
  "jsonrpc": "2.0",
  "id": 104,
  "method": "tools/call",
  "params": {
    "name": "filesystem-read",
    "arguments": {
      "path": "/Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_01_AI_FOUNDATIONS.md"
    }
  }
}
```

### 3.2 JSON-RPC Response Envelope
The corresponding response envelope must match the structured result schema:

```json
{
  "jsonrpc": "2.0",
  "id": 104,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "# UAIEOS Part 01: Foundations of AI Engineering..."
      }
    ],
    "isError": false
  }
}
```

### 3.3 Active Server Schema
Active server configurations are tracked inside the registry:

```json
{
  "server_id": "fs-server",
  "connection_type": "stdio",
  "command": "node",
  "args": ["/Users/dronpancholi/.bin/mcp-fs-server.js"],
  "env": {
    "ALLOWED_PATHS": "/Users/dronpancholi/Developer/01_Strategic/Venus/"
  },
  "status": "RUNNING",
  "uptime_seconds": 1420,
  "capabilities": {
    "tools": ["filesystem-read", "filesystem-write"],
    "resources": []
  }
}
```

---

## 4. Integration & Commands

Administrators interact with the connection supervisor using command-line variables.

### 4.1 Initialize and Check Connection
```bash
python -m uaieos.engines.mcp_orchestrator --action verify-server --server-id fs-server
```
*Expected Output:*
```json
{
  "server_id": "fs-server",
  "status": "CONNECTED",
  "protocol_version": "2024-11-05",
  "capabilities_discovered": {
    "tools": ["filesystem-read", "filesystem-write"],
    "resources": []
  }
}
```

### 4.2 List Active Sessions
```bash
python -m uaieos.engines.mcp_orchestrator --action list-servers
```
*Expected Output:*
```json
{
  "active_servers": [
    {
      "server_id": "fs-server",
      "status": "RUNNING",
      "pid": 98172,
      "message_count": 1409
    }
  ]
}
```

---

## 5. System Cross-References
*   For the architecture guidelines, capability definitions, and security requirements, see [PART_04_MCP_ENGINEERING.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_04_MCP_ENGINEERING.md).
*   For details on sandboxing tools, seccomp validation filters, and error handlers, refer to [PART_05_TOOL_ENGINEERING.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_05_TOOL_ENGINEERING.md).
*   For security scoring, threat modeling, and injection mitigations, refer to [PART_10_AI_SAFETY_GOVERNANCE.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_10_AI_SAFETY_GOVERNANCE.md).
