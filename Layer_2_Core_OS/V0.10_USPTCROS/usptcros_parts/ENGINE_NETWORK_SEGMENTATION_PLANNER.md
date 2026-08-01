# USPTCROS Capability Engine: Network Segmentation Planner
## Version: 0.10 | Classification: Institutional Security Standard | Status: Mandated Gateway

---

## 1. Operational Purpose & Scope
Validates network isolation configurations across VPCs, subnets, and Kubernetes namespaces to ensure compliance with micro-segmentation architectures.

### 1.1 Input Interfaces & Data Sources
- **Input Source**: VPC and routing table configuration files.
- **Input Source**: Kubernetes network policy definitions.
- **Input Source**: Target data flow maps and zone configurations.

### 1.2 Output Interfaces & Artifacts
- **Output Artifact**: Network Isolation report listing unapproved routing paths.
- **Output Artifact**: Network policy templates for firewalls and Kubernetes.
- **Output Artifact**: VPC connection map showing active zones.

### 1.3 Integration & Automation Triggers
- Runs validation checks on network changes.
- Executed before applying routing configurations.
- Scans live routing tables weekly to detect policy drift.

---

## 2. Mathematical Verification Model
### 2.1 Metric/Score Formula
$$N_{Isolation} = 1.0 - \frac{Routes_{CrossZone}}{Routes_{Total}}$$

### 2.2 Variable Definitions
- $Routes_{CrossZone}$: Count of active cross-zone connection routes that violate policies.
- $Routes_{Total}$: Total count of active routing paths.

### 2.3 Calculation Steps & Evaluation Thresholds
1. Extract active routing policies and firewall rules.
2. Build a topological graph of network connections.
3. Identify paths that connect isolated security zones.
4. Calculate isolation rating based on policy-violating routes.

---

## 3. Configuration & Output JSON Validation Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "NetworkSegmentationConfig",
  "type": "object",
  "properties": {
    "vpcId": {
      "type": "string"
    },
    "isolatedSubnets": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "allowedPeeringPairs": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "fromZone": {
            "type": "string"
          },
          "toZone": {
            "type": "string"
          }
        },
        "required": [
          "fromZone",
          "toZone"
        ]
      }
    }
  },
  "required": [
    "vpcId",
    "isolatedSubnets",
    "allowedPeeringPairs"
  ]
}
```

---

## 4. Operational Verification Checklist
- [ ] **Pre-Execution Checks**:
  - [ ] Verify configuration parameters of targeted subnets.
  - [ ] Load the approved network connection maps.
- [ ] **Execution & Scan Verification**:
  - [ ] Audit routing table configurations and settings.
  - [ ] Test access controls between isolated subnet boundaries.
- [ ] **Post-Execution & Mitigation Gates**:
  - [ ] Block unapproved cross-zone connection routes.
  - [ ] Update routing databases with verified settings.
- [ ] **Exception Handling & Emergency Rollback**:
  - [ ] Revert routing modifications to the last stable configurations.
  - [ ] Enable temporary bypasses for critical service traffic if approved.

---

## 5. Navigation & Reference Matrix
- **Related Engines**:
  - [ENGINE_ZERO_TRUST_VALIDATOR.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/ENGINE_ZERO_TRUST_VALIDATOR.md)
  - [ENGINE_POLICY_GENERATOR.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/ENGINE_POLICY_GENERATOR.md)
  - [ENGINE_CLOUD_CONFIGURATION_AUDITOR.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/ENGINE_CLOUD_CONFIGURATION_AUDITOR.md)
- **Output Templates**:
  - [TRUST_BOUNDARY_MAP.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/TRUST_BOUNDARY_MAP.md)
