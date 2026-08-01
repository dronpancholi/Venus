# Bug Report and Triage Template
<!-- Use this template to document software defects identified during QA testing or reported from production. -->

## 1. General Defect Information
*   **Bug ID:** <!-- e.g., BUG-2026-0001 -->
*   **Reporter:** <!-- Name and Role -->
*   **Date Identified:** <!-- YYYY-MM-DD -->
*   **Component/Service:** <!-- e.g., Core Auth API -->
*   **Environment:** <!-- Staging / UAT / Production -->

## 2. Priority & Severity Classification

| Classification | Category | Definition | Action Required |
| :--- | :--- | :--- | :--- |
| **P0 / S0** | Critical Blocker | Service down, data loss, security exposure. No workaround. | Immediate engineering response. Hotfix. |
| **P1 / S1** | Major Failure | Key feature broken, but workaround exists. | Resolve within current sprint cycle. |
| **P2 / S2** | Moderate issue | Minor feature broken. UI misalignment. | Triage into backlog, schedule next sprint. |
| **P3 / S3** | Cosmetic / Low | Documentation typos, minor styling issues. | Resolve as time permits. |

*Select Category:* [ ] P0/S0  --  [ ] P1/S1  --  [ ] P2/S2  --  [ ] P3/S3

## 3. Steps to Reproduce
1. Navigate to URL: `https://staging.venus.internal/checkout`
2. Add product `prod_9091` to cart.
3. Click "Checkout" button.
4. Observe HTTP payload or UI screen behaviour.

## 4. Expected vs. Actual Behavior
*   **Expected Behavior:** System registers the order transaction, redirects to `/receipt` with HTTP 201 Created.
*   **Actual Behavior:** API server times out and logs HTTP 504 Gateway Timeout.

## 5. System Forensics (Payloads / Logs)
```json
{
  "timestamp": "2026-06-26T03:14:35Z",
  "error": "Gateway Timeout",
  "path": "/v1/orders",
  "status": 504,
  "transactionId": "tx_abc123"
}
```

```text
[2026-06-26T03:14:30Z] ERROR: Database connection pool exhausted. Active connections: 50/50.
   at pg.Pool.connect (node_modules/pg/lib/pool.js:12:4)
```

## 6. Root Cause Analysis & Mitigation Proposal
<!-- Filled out by Triage Developer -->
*   **RCA:** Database pool leaks connections in legacy auth handler handler.
*   **Mitigation:** Enforce query release statement in `finally` block of auth controller middleware.
