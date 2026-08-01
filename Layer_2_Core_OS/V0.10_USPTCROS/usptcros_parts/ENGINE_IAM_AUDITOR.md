# USPTCROS Capability Engine: IAM Auditor
## Version: 0.10 | Classification: Institutional Security Standard | Status: Mandated Gateway

---

## 1. Operational Purpose & Scope
Audits IAM user groups, service accounts, roles, and privileges, detecting over-privileged roles and access policy drift.

### 1.1 Input Interfaces & Data Sources
- **Input Source**: Cloud IAM policy definitions and JSON mappings.
- **Input Source**: Identity provider user privilege records.
- **Input Source**: Service account role assignment registries.

### 1.2 Output Interfaces & Artifacts
- **Output Artifact**: Over-privileged Account report detailing excessive roles.
- **Output Artifact**: Remediation policy recommending minimal privileges.
- **Output Artifact**: Drift report highlighting differences between target state and configuration.

### 1.3 Integration & Automation Triggers
- Integrates into cloud configuration audit pipelines.
- Runs scheduled daily reviews of identity setups.
- Integrates with central compliance tracking dashboards.

---

## 2. Mathematical Verification Model
### 2.1 Metric/Score Formula
$$IAM_{OverPrivilege} = \frac{U_{Assigned} - U_{Used}}{U_{Assigned}}$$

### 2.2 Variable Definitions
- $U_{Assigned}$: Number of distinct permissions assigned to the identity.
- $U_{Used}$: Number of permissions utilized by the identity in the past 90 days.

### 2.3 Calculation Steps & Evaluation Thresholds
1. Query IAM role profiles from the identity configurations.
2. Analyze audit logs to measure actual permission usage.
3. Identify unused permissions and flag identities with excess access rights.
4. Generate policies targeting minimal privileges.

---

## 3. Configuration & Output JSON Validation Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "IamAuditConfig",
  "type": "object",
  "properties": {
    "scope": {
      "type": "string"
    },
    "auditPeriodDays": {
      "type": "integer"
    },
    "enforceLeastPrivilege": {
      "type": "boolean"
    }
  },
  "required": [
    "scope",
    "auditPeriodDays",
    "enforceLeastPrivilege"
  ]
}
```

---

## 4. Operational Verification Checklist
- [ ] **Pre-Execution Checks**:
  - [ ] Verify admin credentials for reading IAM configurations.
  - [ ] Confirm that access history logs are updated and readable.
- [ ] **Execution & Scan Verification**:
  - [ ] Audit role definitions for wildcard ('*') permissions.
  - [ ] Identify accounts that have been inactive for over 90 days.
- [ ] **Post-Execution & Mitigation Gates**:
  - [ ] Revoke inactive accounts and remove excessive permissions.
  - [ ] Generate policy updates matching minimal permission requirements.
- [ ] **Exception Handling & Emergency Rollback**:
  - [ ] Restore original permissions if critical service calls fail.
  - [ ] Document override approvals for temporary privilege elevations.

---

## 5. Navigation & Reference Matrix
- **Related Engines**:
  - [ENGINE_ZERO_TRUST_VALIDATOR.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/ENGINE_ZERO_TRUST_VALIDATOR.md)
  - [ENGINE_POLICY_GENERATOR.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/ENGINE_POLICY_GENERATOR.md)
  - [ENGINE_CLOUD_CONFIGURATION_AUDITOR.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/ENGINE_CLOUD_CONFIGURATION_AUDITOR.md)
- **Output Templates**:
  - [RBAC_PERMISSIONS_MATRIX.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/RBAC_PERMISSIONS_MATRIX.md)
