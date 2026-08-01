# USPTCROS ABAC Policy Rules Schema
**Document Link:** [ABAC Policy Rules Schema](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/ABAC_POLICY_RULES_SCHEMA.md)  
**References:** [RBAC Permissions Matrix](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/RBAC_PERMISSIONS_MATRIX.md)

## 1. ABAC Policy Definition
Attribute-Based Access Control (ABAC) dynamically grants access based on subject, object, action, and environment attributes.

## 2. ABAC Rule Policy Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ABACPolicyRule",
  "type": "object",
  "properties": {
    "ruleId": { "type": "string", "pattern": "^ABAC-[0-9]{3}$" },
    "description": { "type": "string" },
    "effect": { "type": "string", "enum": ["Allow", "Deny"] },
    "subject": {
      "type": "object",
      "properties": {
        "role": { "type": "string" },
        "clearanceLevel": { "type": "integer", "minimum": 1, "maximum": 4 },
        "ipAddress": { "type": "string", "format": "ipv4" }
      },
      "required": ["role", "clearanceLevel"]
    },
    "resource": {
      "type": "object",
      "properties": {
        "type": { "type": "string" },
        "classification": { "type": "string", "enum": ["Restricted", "Confidential", "Internal", "Public"] }
      },
      "required": ["type", "classification"]
    },
    "environment": {
      "type": "object",
      "properties": {
        "timeOfDayStart": { "type": "string", "pattern": "^([0-9]{2}):([0-9]{2})$" },
        "timeOfDayEnd": { "type": "string", "pattern": "^([0-9]{2}):([0-9]{2})$" },
        "networkSegment": { "type": "string" }
      }
    }
  },
  "required": ["ruleId", "effect", "subject", "resource"]
}
```

## 3. Sample Rule Configuration
```json
{
  "ruleId": "ABAC-001",
  "description": "Permit Restricted Key Access only from internal network during office hours",
  "effect": "Allow",
  "subject": {
    "role": "SecurityAdmin",
    "clearanceLevel": 4,
    "ipAddress": "10.240.10.15"
  },
  "resource": {
    "type": "cryptographic_key",
    "classification": "Restricted"
  },
  "environment": {
    "timeOfDayStart": "08:00",
    "timeOfDayEnd": "18:00",
    "networkSegment": "SecureZone"
  }
}
```
