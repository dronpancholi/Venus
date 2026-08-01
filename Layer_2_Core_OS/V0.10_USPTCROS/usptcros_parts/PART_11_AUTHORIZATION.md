# Project Venus USPTCROS — Part 11: Authorization

## 1. Executive Summary
Authorization enforces what authenticated subjects are allowed to do. Venus leverages the Policy Enforcement Point (PEP) and Policy Decision Point (PDP) architecture to ensure consistent, auditable, and decoupled authorization decisions.

## 2. PEP/PDP Architecture Model
```
 [Client Request] ──► [Policy Enforcement Point (PEP)] ──► [Policy Decision Point (PDP)]
                             │                                  │
                             ▼                                  ▼
                     [Execute Action]                   [Consult Policies]
                             ▲                                  │
                             │                                  ▼
                             +------------------------ [Policy Information Point (PIP)]
```

---

## 3. Policy Decision Point Execution Loop (Implementation Example)
The following Python script defines an abstract PEP/PDP mechanism that verifies user privileges using external policies.

```python
from typing import Dict, Any, List

class PolicyDecisionPoint:
    def __init__(self, policies: List[Dict[str, Any]]):
        self.policies = policies

    def evaluate_request(self, subject: Dict[str, Any], resource: Dict[str, Any], action: str) -> bool:
        # Loop through registered policies
        for policy in self.policies:
            if self._matches_policy(policy, subject, resource, action):
                if policy.get("effect") == "DENY":
                    return False  # Explicit deny overrides all permits
                if policy.get("effect") == "ALLOW":
                    return True
        return False  # Default Deny if no policy matches

    def _matches_policy(self, policy: Dict[str, Any], subject: Dict[str, Any], resource: Dict[str, Any], action: str) -> bool:
        # Check target context
        target = policy.get("target", {})
        if target.get("role") and target.get("role") not in subject.get("roles", []):
            return False
        if target.get("resource_type") != resource.get("type"):
            return False
        if action not in target.get("actions", []):
            return False
        return True
```

---

## 4. Authorization Audit Checklist
- [ ] Ensure that authorization checks are performed on the server side, not in client-side applications.
- [ ] Validate that authorization logs contain the matching policy ID and final decision.
- [ ] Verify that policies are stored in Git repositories with peer-review protection.
- [ ] Confirm that "Deny" policies always override "Allow" policies in evaluation logic.

---

## 5. Absolute System Links
- **Previous Chapter**: [Part 10: Authentication](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/PART_10_AUTHENTICATION.md)
- **Next Chapter**: [Part 12: RBAC](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/PART_12_RBAC.md)
