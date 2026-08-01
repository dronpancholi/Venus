# UAIEOS Part 04: Model Context Protocol (MCP) Engineering Manual

This manual establishes the architecture, capability protocols, connection lifecycles, and security guidelines for implementing the Model Context Protocol (MCP) in the UAIEOS framework. MCP provides a standardized interface for connecting foundation models to external data sources, filesystems, and tool environments.

---

## 1. Model Context Protocol Architecture

The Model Context Protocol decouples client interfaces (which orchestrate LLM reasoning loops) from server interfaces (which expose resources, tools, and prompts).

```
 +─────────────────────────+                   +─────────────────────────+
 │       MCP Client        │                   │       MCP Server        │
 │  (Agent Engine / LLM)   │                   │  (Filesystem/Database)  │
 +────────────┬────────────+                   +────────────▲────────────+
              │                                             │
              │  JSON-RPC 2.0 over Stdio / SSE Transport    │
              └─────────────────────────────────────────────┘
```

### 1.1 Architectural Tiers
*   **Clients:** Orchestrate model contexts, manage user prompts, and map tool execution tokens to local execution flows.
*   **Servers:** Independent runtime processes that expose specific capability endpoints:
    *   **Resources:** Read-only data sources (e.g., database tables, log streams).
    *   **Tools:** Executable endpoints (e.g., shell compilers, web scrapers).
    *   **Prompts:** Pre-configured system templates and task architectures.

---

## 2. Capability Discovery & Handshake

When a client connects to an MCP server, it must execute a protocol handshake to discover capability boundaries, protocol versions, and specific schemas.

### 2.1 The Handshake Exchange
```
Client                                                         Server
  │                                                              │
  ├─ initialize Request (Client Capabilities) ──────────────────►│
  │                                                              │
  │◄─ initialize Response (Server Capabilities) ─────────────────┤
  │                                                              │
  ├─ initialized Notification ──────────────────────────────────►│
```

### 2.2 Protocol Version Negotiation
Clients and servers must negotiate the highest mutually supported protocol version. During `initialize`, the client proposes its version range, and the server returns the selected version. If the server does not support the client's minimum version, the connection is terminated.

### 2.3 Handshake Initialization Schema
The handshake utilizes JSON-RPC 2.0 payloads:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "roots": { "listChanged": true },
      "sampling": {}
    },
    "clientInfo": {
      "name": "uaieos-agent-core",
      "version": "0.8.0"
    }
  }
}
```

The server response details its capabilities, including lists of resources, tools, and custom prompts:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "resources": { "subscribe": true, "listChanged": true },
      "tools": { "listChanged": true },
      "prompts": { "listChanged": true }
    },
    "serverInfo": {
      "name": "enterprise-filesystem-broker",
      "version": "1.2.4"
    }
  }
}
```

---

## 3. Transport Layer & Connection Management

MCP supports multiple transport layer configurations. Connections are supervised by a host runtime wrapper to guarantee error handling and packet delivery.

### 3.1 Supported Transport Channels
1.  **Stdio Transport:** Standard input/output channels. Used primarily for locally spawned processes (e.g., node scripts, python runtimes). Highly secure as there is no network interface exposed.
2.  **Server-Sent Events (SSE):** HTTP-based unidirectional streaming combined with a client-to-server POST endpoint. Used for remote or containerized services.

### 3.2 Connection Lifecycle Management
*   **Startup:** Servers must be spawned with isolated environment variables.
*   **Heartbeat Monitor:** Active connections are pinged every $30\text{ seconds}$. If a server fails to respond to 3 consecutive pings, it is flagged as unhealthy and scheduled for auto-restart.
*   **Teardown:** Connections must be closed gracefully using the JSON-RPC `shutdown` method. If the process does not terminate within $5\text{ seconds}$, the supervisor issues a `SIGKILL`.

---

## 4. Security & Access Control

MCP servers execute code and access private repositories; strict security boundaries are mandatory.

### 4.1 Bounded Capability Access (ACLs)
MCP clients must maintain a Access Control List (ACL) configuration for every registered server:

```json
{
  "server_id": "filesystem-broker-prod",
  "allowed_directories": [
    "/Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/"
  ],
  "blocked_extensions": [".env", ".key", ".pem"],
  "allow_write": false
}
```

### 4.2 Sandboxing Rules
*   Any server executing external tools or code compilation must run in a containerized environment (e.g., Docker, firecracker microVM) with networking disabled unless explicitly whitelisted.
*   Environment variables passed to the MCP server must be stripped of system credentials and runtime secret configurations.

---

## 5. System Cross-References
*   To see the broker code that runs MCP connection routing, see [ENGINE_MCP_ORCHESTRATION.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/ENGINE_MCP_ORCHESTRATION.md).
*   For tool validation protocols, sandbox executions, and fallback rules, refer to [PART_05_TOOL_ENGINEERING.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_05_TOOL_ENGINEERING.md).
*   For security auditing and safety policies, refer to [PART_10_AI_SAFETY_GOVERNANCE.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_10_AI_SAFETY_GOVERNANCE.md).
