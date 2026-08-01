# Database Migration Plan
**Document ID:** VENUS-STD-036
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Zero-Downtime Rollout Steps
Migrations must execute in four distinct phases (Expand-Contract model):

```
[Phase 1: Expand DDL] ────► [Phase 2: Data Backfill] ────► [Phase 3: Code Switch] ────► [Phase 4: Contract DDL]
```

- **Phase 1 (Expand)**: Run non-blocking DDL (e.g., add new nullable column).
- **Phase 2 (Backfill)**: Copy historical data in throttled batches to prevent locking.
- **Phase 3 (Switch)**: Deploy application code writing to both and reading from new.
- **Phase 4 (Contract)**: Drop old column in next release cycle.

---

## 2. Reusable Checklist & Exit Criteria
*   [ ] Checked that DDL scripts contain zero column rename or drop operations in Phase 1.
*   [ ] Verified that rollback scripts are generated and verified on staging database copies.
*   [ ] Confirmed data backfills include checkpoint limits.
