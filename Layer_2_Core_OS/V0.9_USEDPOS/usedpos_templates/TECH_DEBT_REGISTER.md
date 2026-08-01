# Technical Debt Register
**Document ID:** VENUS-STD-059
**Version:** 1.0.0
**Status:** Operational
**Last Updated:** 2026-06-26

## 1. Overview
The Technical Debt Register tracks architectural shortcomings, outdated dependencies, lacking test coverage, and code maintenance issues. Tech debt is reviewed during sprint planning to allocate development effort for refactoring.

## 2. Technical Debt Schema
Each entry in the technical debt register must be logged with the following schema details:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "TechDebtItem",
  "type": "object",
  "properties": {
    "id": { "type": "string", "pattern": "^TD-[0-9]{4}$" },
    "title": { "type": "string" },
    "description": { "type": "string" },
    "classification": { "type": "string", "enum": ["Architecture", "Code Quality", "Test Coverage", "Infrastructure"] },
    "remediationCostDays": { "type": "number" },
    "impactScore": { "type": "integer", "minimum": 1, "maximum": 5 },
    "status": { "type": "string", "enum": ["Backlog", "Scheduled", "InProgress", "Resolved"] },
    "owner": { "type": "string" },
    "targetResolutionDate": { "type": "string", "format": "date" }
  },
  "required": ["id", "title", "description", "classification", "remediationCostDays", "impactScore", "status"]
}
```

## 3. Register Entries

| ID | Title | Description | Classification | Remediation Cost (Days) | Impact Score (1-5) | Status | Owner | Target Date |
| :--- | :--- | :--- | :--- | :---: | :---: | :--- | :--- | :--- |
| **TD-0001** | Refactor Legacy Auth Handler | Migrate from token-based authentication to fully stateless JWT validator. | Architecture | 5.0 | 4 | Scheduled | Jane Doe | 2026-07-15 |
| **TD-0002** | Add E2E Playwright Coverage | Playwright coverage of checkout page is missing ($0\%$ UI coverage). | Test Coverage | 4.0 | 3 | Backlog | John Smith | 2026-08-01 |
| **TD-0003** | Terraform State Clean Up | Consolidate duplicate VPC resources and upgrade modules to TF v1.5+. | Infrastructure | 3.0 | 2 | InProgress | Alan Turing | 2026-07-05 |

## 4. Cross-References
- [Refactoring Proposal](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/REFACTORING_PROPOSAL.md)
- [Static Analysis SonarQube Spec](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/STATIC_ANALYSIS_SONARQUBE_SPEC.md)
