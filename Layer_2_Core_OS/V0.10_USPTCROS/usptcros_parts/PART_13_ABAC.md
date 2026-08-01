# Project Venus USPTCROS — Part 13: Attribute-Based Access Control (ABAC)

## 1. Executive Summary
Attribute-Based Access Control (ABAC) defines permission rules using metadata attributes belonging to the subject, resource, action, and environment. This allows Venus to enforce fine-grained, context-aware authorization decisions.

## 2. ABAC Context Policy in OPA Rego
Project Venus uses Open Policy Agent (OPA) to evaluate ABAC rules. The following Rego policy restricts resource modifications based on owner attributes, classification, and environment variables.

```rego
package venus.abac

default allow = false

# Allow access if all conditions are met
allow {
    # Subject must have verified clearance
    input.subject.clearance_level == "HIGH"
    
    # Resource classification matches clearance
    input.resource.classification == "CONFIDENTIAL"
    
    # Enforce Owner check
    input.resource.owner == input.subject.id
    
    # Action matches allowed methods
    allowed_methods[input.action.method]
    
    # Environment criteria: requests must occur within business hours
    input.environment.hour >= 8
    input.environment.hour <= 18
}

allowed_methods = {"GET", "POST", "PUT"}
```

---

## 3. ABAC Verification Steps
1. **Attribute Extraction**: Resolve subject metadata, resource tags, IP address, and time metrics.
2. **Policy Evaluation**: Forward attributes to OPA engine.
3. **Decisive Verdict**: PEP blocks request unless OPA outputs `allow = true`.

---

## 4. ABAC Operational Checklist
- [ ] Verify that resource classification tags (e.g., "CONFIDENTIAL", "PUBLIC") are protected from manual client edits.
- [ ] Ensure that system clocks are synchronized via NTP to prevent environment time-based bypasses.
- [ ] Validate that local caching of ABAC attributes does not exceed a TTL of 60 seconds.

---

## 5. Absolute System Links
- **Previous Chapter**: [Part 12: RBAC](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/PART_12_RBAC.md)
- **Next Chapter**: [Part 14: Zero Trust](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/PART_14_ZERO_TRUST.md)
