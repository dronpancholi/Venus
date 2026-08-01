# MCP Tool Registry Schema (Project Venus V0.8)

## 1. Executive Summary
This document defines the schema and metadata registry structure for cataloging and exposing MCP tools across the Venus Enterprise Architecture. The registry serves as the single source of truth for tool availability, execution bounds, and dependency mapping.

---

## 2. Tool Registry JSON Schema
All registry entry files (`mcp-registry.json`) must strictly validate against the JSON Schema defined below:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "VenusMcpToolRegistry",
  "type": "object",
  "properties": {
    "registry_name": { "type": "string" },
    "version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },
    "last_updated": { "type": "string", "format": "date-time" },
    "servers": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "server_id": { "type": "string" },
          "description": { "type": "string" },
          "transport": { "type": "string", "enum": ["stdio", "sse"] },
          "connection_config": {
            "type": "object",
            "properties": {
              "command": { "type": "string" },
              "args": { "type": "array", "items": { "type": "string" } },
              "env": { "type": "object" },
              "url": { "type": "string", "format": "uri" }
            },
            "required": []
          },
          "tools": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "name": { "type": "string", "pattern": "^[a-zA-Z0-9_-]+$" },
                "description": { "type": "string" },
                "input_schema": { "type": "object" },
                "security_profile": {
                  "type": "object",
                  "properties": {
                    "isolation_level": { "type": "string", "enum": ["system", "sandbox", "restricted"] },
                    "required_clearance": { "type": "string", "enum": ["L1", "L2", "L3"] }
                  },
                  "required": ["isolation_level", "required_clearance"]
                },
                "deprecation_status": {
                  "type": "object",
                  "properties": {
                    "is_deprecated": { "type": "boolean" },
                    "deprecation_date": { "type": "string", "format": "date" },
                    "replacement_tool": { "type": "string" }
                  },
                  "required": ["is_deprecated"]
                }
              },
              "required": ["name", "description", "input_schema", "security_profile"]
            }
          }
        },
        "required": ["server_id", "transport", "tools"]
      }
    }
  },
  "required": ["registry_name", "version", "last_updated", "servers"]
}
```

---

## 3. Example Registry Configuration Payload

```json
{
  "registry_name": "Venus Global Tool Registry",
  "version": "0.8.0",
  "last_updated": "2026-06-26T03:00:00Z",
  "servers": {
    "data-utility-server": {
      "server_id": "data-utility-server-v1",
      "description": "Standard database querying and analytics server",
      "transport": "stdio",
      "connection_config": {
        "command": "node",
        "args": ["/opt/venus/mcp/db-server.js"],
        "env": {
          "DB_READONLY": "true"
        }
      },
      "tools": [
        {
          "name": "run_read_query",
          "description": "Executes standard read-only SELECT statements.",
          "input_schema": {
            "type": "object",
            "properties": {
              "sql_query": { "type": "string" }
            },
            "required": ["sql_query"]
          },
          "security_profile": {
            "isolation_level": "sandbox",
            "required_clearance": "L2"
          },
          "deprecation_status": {
            "is_deprecated": false
          }
        }
      ]
    }
  }
}
```

---

## 4. Deprecation & Lifecycle Strategy
To prevent unexpected agent failures, tools flagged with `is_deprecated: true` execute a phased wind-down:
1.  **Phase 1 (Warning):** Executions succeed, but warnings are injected into the agent log stream.
2.  **Phase 2 (Throttling):** Deprecated tools introduce artificial latency delays ($1,000\text{ ms}$ increase) to disincentivize runtime dependency.
3.  **Phase 3 (Removal):** Tool is deleted from registry; attempts to execute return a JSON-RPC error.

---

## 5. Cross-References
*   Protocol definitions for the hosting servers are configured in [MCP_SERVER_SPECIFICATION.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_templates/MCP_SERVER_SPECIFICATION.md).
*   Security restrictions on tool invocation are detailed in [MCP_SECURITY_POLICY.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_templates/MCP_SECURITY_POLICY.md).
*   Individual schema validation specifications are structured in [TOOL_SCHEMA_DEFINITION.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_templates/TOOL_SCHEMA_DEFINITION.md).
