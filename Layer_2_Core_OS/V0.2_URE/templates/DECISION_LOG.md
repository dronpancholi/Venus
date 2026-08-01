# Template: Decision Log

## 1. Document Context
*   **Project Name**: [Project Name]
*   **Target Scope**: Architecture & Operations
*   **Date Compiled**: [Date]

---

## 2. Decision Audit Trail

Every major architectural, product, or infrastructural decision made is logged below to preserve institutional memory:

| Decision ID | Target Subject | Selected Option | Rejected Options | Decisive Rationale | Approver |
|---|---|---|---|---|---|
| **DEC-01** | background Queue | Temporal.io | Celery, BullMQ | Durable stateful workflows, retry logic, signal handling | [Name] |
| **DEC-02** | Multi-Tenancy | Postgres RLS | DB-per-tenant | Shared cost structure with absolute security isolation | [Name] |
| **DEC-03** | Frontend Client | Next.js Console | SPA React App | Fast initial load, SEO routing, unified app folder | [Name] |

---

## 3. Decision Status
*All logged decisions are marked as **PROPOSED**, **APPROVED**, or **SUPERSEDED** (with links to replacement entries).*
