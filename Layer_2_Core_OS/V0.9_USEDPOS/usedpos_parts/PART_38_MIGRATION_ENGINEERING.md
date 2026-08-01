# Part 38: Migration Engineering

## 1. Context & Strategy
Migration Engineering under Project Venus governs database schema and data migration processes. We mandate zero-downtime database migrations using the Expand-and-Contract (Parallel Run) pattern. Direct modifications that lock tables or break backward-compatibility are prohibited. Schema changes must be split into distinct, backward-compatible stages.

---

## 2. Migration Mathematics & Lifecycle Stages

### 2.1 The Expand-and-Contract Cycle
The migration cycle splits a single modification into four operational phases:

```
[Phase 1: Expand] ────► Add new column/table (Code supports old and new schemas)
         │
         ▼
[Phase 2: Sync]   ────► Copy legacy data (Dual writes active in application)
         │
         ▼
[Phase 3: Switch] ────► Divert reads/writes (Code redirects all operations to new schema)
         │
         ▼
[Phase 4: Contract] ──► Remove legacy elements (Drop old columns/tables safely)
```

### 2.2 Dual Write Synchronization Progress Metric
For data backfills during migration, progress ($P_{sync}$) is monitored continuously:

$$P_{sync} = \frac{N_{backfilled}}{N_{total\_records}} \times 100$$

*   *Threshold*: Phase 3 (Switch) cannot be executed until $P_{sync} = 100\%$ and data verification checksums match.

---

## 3. Migration Integration Standards

### 3.1 Expand-and-Contract SQL Specification
Example SQL steps for safely renaming a column from `user_phone` to `phone_number` in a PostgreSQL database without downtime:

```sql
-- Phase 1: Expand
ALTER TABLE users ADD COLUMN phone_number VARCHAR(32);

-- Phase 2: Sync (Application writes to both fields; backfill old records)
UPDATE users 
SET phone_number = user_phone 
WHERE phone_number IS NULL AND user_phone IS NOT NULL;

-- (Create constraint after sync is complete to prevent locking during index build)
ALTER TABLE users ADD CONSTRAINT check_phone_number_not_null CHECK (phone_number IS NOT NULL) NOT VALID;
ALTER TABLE users VALIDATE CONSTRAINT check_phone_number_not_null;

-- Phase 4: Contract (Executed in a subsequent release after confirming Phase 3 read/write success)
ALTER TABLE users DROP COLUMN user_phone;
```

### 3.2 Migration Task Configuration Schema
Migration deployments must register metadata according to this JSON structure:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "MigrationSpecification",
  "type": "object",
  "properties": {
    "migrationId": { "type": "string" },
    "targetDatabase": { "type": "string" },
    "expandSql": { "type": "string" },
    "contractSql": { "type": "string" },
    "rollbackSql": { "type": "string" }
  },
  "required": ["migrationId", "targetDatabase", "expandSql", "contractSql", "rollbackSql"]
}
```

---

## 4. Reusable Checklist & Exit Criteria
*   [ ] Checked that no `ALTER TABLE` statement triggers a full table lock on tables with $>10,000$ rows.
*   [ ] Verified that dual-write code logic is thoroughly tested on staging environments.
*   [ ] Confirmed that rollback SQL statements are validated for every migration script.
*   [ ] Checked that indexes created on large tables use the `CONCURRENTLY` modifier.
*   [ ] Verified that data migration scripts include throttle mechanisms to prevent CPU spikes.
