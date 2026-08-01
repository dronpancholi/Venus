# Template: Trust Boundary Analysis

## 1. Document Control
*   **Project Name**: [Project Name]
*   **Audit ID**: SEC-TRU-[UUID]

---

## 2. Trust Boundaries Registry
*List all system interfaces where data crosses from lower trust to higher trust zones.*

| Interface ID | Source Zone (Low Trust) | Destination Zone (High Trust) | Data Exchanged | Security Gate |
|---|---|---|---|---|
| **TRU-01** | Public Internet (User) | Private VPC (Gateway) | HTTP API request parameters | Zod validation + JWT verification |
| **TRU-02** | Gateway Service | DB Subnet | SQL Queries | pgBouncer authenticated sessions |
| **TRU-03** | Third-party Webhook (Stripe)| Private Subnet | Payment transaction event | Signature validation checks |

---

## 3. Data Cleansing & Boundary Rules
*   **Rule 1**: All parameters crossing TRU-01 must be typed and validated against regex sanitizers prior to SQL query parsing.
*   **Rule 2**: Cross-VPC data routes must be configured with private endpoints (e.g. AWS PrivateLink) to prevent public internet transit.
*   **Rule 3**: Webhook events must be queued; consumers verify payload signature asynchronously.
