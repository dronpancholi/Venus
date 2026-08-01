# Regression Test Suite Specification
**Document ID:** VENUS-STD-074
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Purpose
This specification documents the regression testing strategy designed to verify that existing platform features remain operational after software updates, refactoring, or patch configurations.

## 2. Regression Cycle Definition
*   **Execution Frequency:** Daily at 02:00 UTC (automated cron pipeline).
*   **Trigger Conditions:** Merges to the `develop` or `release/*` branches.
*   **Execution Time Limit:** The regression suite must execute and report in less than 30 minutes.

## 3. Core Regression Scenarios Matrix

| Scenario ID | Component | Action / Path | Verification | Expected Output |
| :--- | :--- | :--- | :--- | :--- |
| **REG-001** | Identity Provider | Submit token authentication payload | Verify token verification | Success (HTTP 200) + Signed JWT token |
| **REG-002** | Payment Gateway | Invoke transaction route `/v1/charge` | Verify gateway signature | Success (HTTP 200) + Tx Hash code |
| **REG-003** | Order Management | POST `/v1/orders` | Check database transaction state | Database entry created with state "Pending" |
| **REG-004** | Inventory Controller| Request SKU quantity update | Deduct stock index | Stock count falls by request amount |

## 4. Test Selection Strategy
1. **Critical Hotspots:** 100% of P0 scenarios (Authentication, Payments, Order placement) are included.
2. **Boundary Checks:** All updated service contracts must include schema checks.
3. **Historical Regressions:** Any resolved regression bug must have a test written and permanently appended to the regression test suite.

## 5. Cross-References
- [Test Plan Strategy](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/TEST_PLAN_STRATEGY.md)
- [QA Automation Suite Runbook](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/QA_AUTOMATION_SUITE_RUNBOOK.md)
