# USPTCROS Attack Tree Node Schema
**Document Link:** [Attack Tree Node Schema](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/ATTACK_TREE_NODE_SCHEMA.md)

JSON validation schema for programmatically defining attack tree topologies and calculations.

## 1. Schema Validation Definition
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "AttackTreeNode",
  "type": "object",
  "properties": {
    "nodeId": { "type": "string", "pattern": "^AT-[0-9]{3}$" },
    "label": { "type": "string", "maxLength": 128 },
    "gateType": { "type": "string", "enum": ["AND", "OR", "LEAF"] },
    "probability": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
    "attackerCost": { "type": "integer", "minimum": 0 },
    "difficulty": { "type": "string", "enum": ["Trivial", "Medium", "High", "Extreme"] },
    "mitigatedBy": {
      "type": "array",
      "items": { "type": "string" }
    },
    "children": {
      "type": "array",
      "items": { "$ref": "#" }
    }
  },
  "required": ["nodeId", "label", "gateType", "probability", "attackerCost", "difficulty"]
}
```

## 2. Valid JSON Data Block
```json
{
  "nodeId": "AT-001",
  "label": "Bypass Web Application Firewall",
  "gateType": "OR",
  "probability": 0.15,
  "attackerCost": 25000,
  "difficulty": "High",
  "mitigatedBy": ["WAF-RULE-404", "IP-RATE-LIMIT"],
  "children": [
    {
      "nodeId": "AT-002",
      "label": "Execute Zero-Day Vulnerability",
      "gateType": "LEAF",
      "probability": 0.05,
      "attackerCost": 150000,
      "difficulty": "Extreme"
    },
    {
      "nodeId": "AT-003",
      "label": "Exploit CORS Misconfiguration",
      "gateType": "LEAF",
      "probability": 0.40,
      "attackerCost": 5000,
      "difficulty": "Medium"
    }
  ]
}
```
