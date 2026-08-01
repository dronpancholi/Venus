# QA Automation Suite Runbook
**Document ID:** VENUS-STD-073
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Objectives and Scope
This runbook provides directions for QA Engineers and CI systems to run the automated test suite against staging, UAT, and production environments.

## 2. Execution Runbook

### 2.1 Local Environment Preparation
Verify node configuration and package parameters:
```bash
# Verify node and npm version
node -v
npm -v

# Fetch latest packages
npm ci
```

### 2.2 Execution Commands

```bash
# Run all unit tests
npm run test:unit

# Run database integration tests
npm run test:integration

# Run Playwright E2E tests in Headless mode
npx playwright test

# Run UI tests with interactive UI
npx playwright test --ui
```

## 3. Reporting and Artifact Collection
All E2E test runs export structured logs and execution recordings.

*   **HTML Test Report Location:** `./playwright-report/index.html`
*   **Console Log Location:** `./logs/test-execution.log`
*   **Failing Test Traces:** `./test-results/` (contains trace zip files detailing page render flows).

## 4. Failure Triage Workflow
If an automated test fails during a pipeline check:
1. Inspect the CI pipeline console to identify if the root cause is a flaky network or programmatic bug.
2. If network-related, run the job once with `retries` enabled.
3. If code-related, open a high-priority ticket using the [Bug Report Triage Template](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/BUG_REPORT_TRIAGE_TEMPLATE.md).

## 5. Cross-References
- [End-to-End Playwright Spec](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/END_TO_END_PLAYWRIGHT_SPEC.md)
- [Regression Test Suite Specification](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/REGRESSION_TEST_SUITE_SPEC.md)
