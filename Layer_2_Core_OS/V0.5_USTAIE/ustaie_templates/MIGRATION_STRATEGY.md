# Template: Migration Strategy

## 1. Document Control
*   **Project Name**: [Project Name]
*   **Migration ID**: MIG-[UUID]

---

## 2. Migration Pipeline Phases
*Outline the transition strategy (e.g. database schema upgrade or microservice split).*

```
[Phase 1: Dual Write Mode] ──► [Phase 2: Historical Data Backfill] ──► [Phase 3: Deprecate Old Store]
```

---

## 3. Execution Checklist & Verification

### Phase 1: Dual Write Execution
*   [ ] Write API modifications to route writes to both PostgreSQL and DynamoDB.
*   [ ] Verify dual write latency overhead remains < 10ms.

### Phase 2: Backfill Execution
*   [ ] Run batch backfill script: `scripts/backfill_user_data.py`.
*   [ ] Execute data validation integrity checks.

### Phase 3: Cut-over
*   [ ] Toggle feature flag to route database reads to the new database.
*   [ ] Deprecate the old database configuration variables.
