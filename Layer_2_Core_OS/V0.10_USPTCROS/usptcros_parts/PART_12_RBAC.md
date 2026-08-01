# Project Venus USPTCROS — Part 12: Role-Based Access Control (RBAC)

## 1. Executive Summary
Role-Based Access Control (RBAC) simplifies permissions by assigning authorizations to logical roles rather than individual subjects. Venus structures roles and permissions hierarchical, ensuring coarse-grained access control.

## 2. RBAC Policy Schema
The following JSON schema defines the format for Venus RBAC role configurations and user-to-role bindings.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "VenusRBACPolicy",
  "type": "object",
  "properties": {
    "roles": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "role_name": { "type": "string" },
          "permissions": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "resource": { "type": "string" },
                "actions": {
                  "type": "array",
                  "items": { "type": "string" }
                }
              },
              "required": ["resource", "actions"]
            }
          }
        },
        "required": ["role_name", "permissions"]
      }
    },
    "bindings": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "subject_id": { "type": "string" },
          "assigned_role": { "type": "string" }
        },
        "required": ["subject_id", "assigned_role"]
      }
    }
  },
  "required": ["roles", "bindings"]
}
```

---

## 3. RBAC Enforcement Middleware Example
```python
from typing import List, Dict, Set

class RBACEnforcer:
    def __init__(self, rbac_policy: Dict[str, Any]):
        self.roles = {r["role_name"]: r["permissions"] for r in rbac_policy.get("roles", [])}
        self.bindings = {b["subject_id"]: b["assigned_role"] for b in rbac_policy.get("bindings", [])}

    def check_permission(self, subject_id: str, resource: str, action: str) -> bool:
        assigned_role = self.bindings.get(subject_id)
        if not assigned_role:
            return False  # Subject has no bound roles
        
        permissions = self.roles.get(assigned_role, [])
        for perm in permissions:
            if perm["resource"] == resource or perm["resource"] == "*":
                if action in perm["actions"] or "*" in perm["actions"]:
                    return True
        return False
```

---

## 4. RBAC Audit Checklist
- [ ] Enforce Separation of Duties (SoD): A user with role "Developer" must not have the role "Deployer".
- [ ] Conduct monthly automated reconciliation audits to verify that no orphaned user accounts retain active bindings.
- [ ] Configure role bindings to inherit minimal default permissions upon initialization.

---

## 5. Absolute System Links
- **Previous Chapter**: [Part 11: Authorization](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/PART_11_AUTHORIZATION.md)
- **Next Chapter**: [Part 13: ABAC](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/PART_13_ABAC.md)
