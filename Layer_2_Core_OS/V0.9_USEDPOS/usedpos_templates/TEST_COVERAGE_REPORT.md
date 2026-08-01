# Test Coverage Report Template
**Document ID:** VENUS-STD-068
**Version:** 1.0.0
**Status:** Operational
**Last Updated:** 2026-06-26

## 1. Executive Summary
This report aggregates the code coverage metrics compiled from unit, integration, and E2E testing pipelines across Project Venus application repositories.

## 2. Consolidated Coverage Target Metrics

| Repository | Statements | Branches | Functions | Lines | Status |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `venus-core-auth` | 89.2% | 85.0% | 90.1% | 88.5% | PASS |
| `venus-payment-gw` | 91.5% | 88.4% | 93.0% | 91.0% | PASS |
| `venus-order-mgmt` | 78.4% | 71.2% | 80.5% | 77.9% | FAIL |
| **System Aggregated** | **86.3%** | **81.5%** | **87.8%** | **85.8%** | **PASS** |

*Note:* `venus-order-mgmt` fails the quality gate of 80% coverage. A pull request is required to remediate coverage prior to releasing `release/v2.1.0`.

## 3. Remediation Action Plan
For repositories failing the 80% quality gate, the following steps must be taken:
1. Identify components with the lowest coverage using coverage tools (e.g. `lcov` or `cobertura` reports).
2. Prioritize writing unit tests for core domain logic paths.
3. Log target files in the development team's Sprint Backlog.

## 4. Cross-References
- [Test Plan Strategy](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/TEST_PLAN_STRATEGY.md)
- [Static Analysis SonarQube Spec](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/STATIC_ANALYSIS_SONARQUBE_SPEC.md)
