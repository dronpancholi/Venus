# USPTCROS Capability Engine: Terraform Security Auditor
## Version: 0.10 | Classification: Institutional Security Standard | Status: Mandated Gateway

---

## 1. Operational Purpose & Scope
Analyzes Terraform HCL configuration files and deployment plan outputs to identify insecure infrastructure definitions before provisioning.

### 1.1 Input Interfaces & Data Sources
- **Input Source**: Terraform HCL configuration files (*.tf).
- **Input Source**: Terraform plan outputs (JSON format).
- **Input Source**: Security rule definitions mapping to CIS benchmarks.

### 1.2 Output Interfaces & Artifacts
- **Output Artifact**: Terraform Security Audit report listing infrastructure vulnerabilities.
- **Output Artifact**: Mitigation plan proposing secure HCL configuration options.
- **Output Artifact**: JSON compliance report detailing configuration violations.

### 1.3 Integration & Automation Triggers
- Runs during local plan stages and CI verification gates.
- Blocks deployment workflows if high-severity violations are found.
- Integrates with repositories to scan state records.

---

## 2. Mathematical Verification Model
### 2.1 Metric/Score Formula
$$TF_{Risk} = \sum (F_{Type} \times C_{Severity})$$

### 2.2 Variable Definitions
- $F_{Type}$: Count of violations matched in configuration files.
- $C_{Severity}$: Severity rating weight (e.g. 5.0 for open SSH, 2.0 for unencrypted buckets).

### 2.3 Calculation Steps & Evaluation Thresholds
1. Parse Terraform files into structured HCL formats.
2. Verify configuration values against security rules.
3. Inspect execution plans for unauthorized access properties.
4. Sum weighted findings to calculate the total risk score.

---

## 3. Configuration & Output JSON Validation Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "TerraformAuditConfig",
  "type": "object",
  "properties": {
    "scanPath": {
      "type": "string"
    },
    "failOnSeverity": {
      "type": "string",
      "enum": [
        "Low",
        "Medium",
        "High",
        "Critical"
      ]
    },
    "ignoredRules": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "scanPath",
    "failOnSeverity",
    "ignoredRules"
  ]
}
```

---

## 4. Operational Verification Checklist
- [ ] **Pre-Execution Checks**:
  - [ ] Verify plan files are in readable JSON formats.
  - [ ] Check that checkov or tfsec rules are updated.
- [ ] **Execution & Scan Verification**:
  - [ ] Scan HCL code blocks for hardcoded passwords.
  - [ ] Check network isolation and ingress configuration blocks.
- [ ] **Post-Execution & Mitigation Gates**:
  - [ ] Log violation summaries to pipeline dashboard.
  - [ ] Fail the pipeline if critical violations are found.
- [ ] **Exception Handling & Emergency Rollback**:
  - [ ] Revert Terraform configuration files to the last secure version.
  - [ ] Destroy unapproved resources in test environments.

---

## 5. Navigation & Reference Matrix
- **Related Engines**:
  - [ENGINE_CLOUD_CONFIGURATION_AUDITOR.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/ENGINE_CLOUD_CONFIGURATION_AUDITOR.md)
  - [ENGINE_KUBERNETES_SECURITY_AUDITOR.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/ENGINE_KUBERNETES_SECURITY_AUDITOR.md)
  - [ENGINE_NETWORK_SEGMENTATION_PLANNER.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/ENGINE_NETWORK_SEGMENTATION_PLANNER.md)
- **Output Templates**:
  - [SECURITY_ARCHITECTURE_BLUEPRINT.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/SECURITY_ARCHITECTURE_BLUEPRINT.md)
