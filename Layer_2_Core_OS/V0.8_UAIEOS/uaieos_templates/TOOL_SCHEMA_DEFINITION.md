# Tool Schema Definition (Project Venus V0.8)

## 1. Goal & Architecture
This document specifies the validation schema conventions, input/output structures, and runtime parameter checking standards for all tools accessible via the Venus Host agent system.

---

## 2. Standard Schema Template Definition
Every tool interface must declare its capabilities in an OpenAPI-compatible format using Draft-07 JSON Schema. Below is the structural schema definition template:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "VenusToolDefinition",
  "type": "object",
  "properties": {
    "name": { 
      "type": "string",
      "pattern": "^[a-z0-9_]{3,64}$",
      "description": "Unique, lowercase identifier containing alphanumeric and underscore characters."
    },
    "description": { 
      "type": "string",
      "minLength": 20,
      "description": "Detailed explanation of tool behavior. Crucial for agent model zero-shot selection."
    },
    "parameters": {
      "type": "object",
      "properties": {
        "type": { "type": "string", "const": "object" },
        "properties": { "type": "object" },
        "required": { "type": "array", "items": { "type": "string" } }
      },
      "required": ["type", "properties"]
    },
    "returns": {
      "type": "object",
      "properties": {
        "type": { "type": "string" },
        "properties": { "type": "object" }
      },
      "required": ["type"]
    }
  },
  "required": ["name", "description", "parameters", "returns"]
}
```

---

## 3. Tool Declaration Example: `fetch_api_data`

```json
{
  "name": "fetch_api_data",
  "description": "Retrieves external API content securely using a validated endpoint name.",
  "parameters": {
    "type": "object",
    "properties": {
      "endpoint_key": {
        "type": "string",
        "enum": ["billing_service", "inventory_service", "user_management"]
      },
      "query_parameters": {
        "type": "object",
        "additionalProperties": { "type": "string" }
      }
    },
    "required": ["endpoint_key"]
  },
  "returns": {
    "type": "object",
    "properties": {
      "status_code": { "type": "integer" },
      "payload": { "type": "object" }
    }
  }
}
```

---

## 4. Parameter Validation Algorithm
Before serializing the tool call parameter block to the target execution environment:

1.  **Draft-07 Check:** Run a fast standard AJV (Another JSON Validator) step against the declared `parameters` schema block.
2.  **Strict Type Casting:** Cast numeric types to double-precision values and enforce string length clamp checks.
3.  **Enum Check:** Assert value bounds for properties defining explicit `enum` arrays.
4.  **Security Sanitization:** Execute string checks for script execution strings (e.g. `eval(`, `exec(`) to prevent direct payload takeover.

---

## 5. Cross-References
*   Registry-level validation rules for all tools are maintained in [MCP_TOOL_REGISTRY_SCHEMA.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_templates/MCP_TOOL_REGISTRY_SCHEMA.md).
*   Data sanitization and access clearances are detailed in [MCP_SECURITY_POLICY.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_templates/MCP_SECURITY_POLICY.md).
*   Execution isolation specifications are outlined in [TOOL_SANDBOXING_POLICY.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_templates/TOOL_SANDBOXING_POLICY.md).
