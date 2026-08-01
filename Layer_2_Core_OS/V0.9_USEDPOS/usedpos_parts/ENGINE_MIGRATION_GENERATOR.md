# ENGINE — Migration Generator
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## Purpose
Generates safe, zero-downtime database migration plans and execution scripts for any schema change. Applies expand-contract pattern, batch processing, rollback plans, and verification queries automatically.

---

## Input
```
Required:
  - Current schema state (DDL or introspection)
  - Target schema state (desired DDL)
  - Estimated table row counts
  - Production traffic pattern (peak hours, quiet windows)

Optional:
  - Lock timeout requirements
  - Maximum acceptable migration duration
  - Rollback requirements
```

---

## Generation Process

### Step 1: Change Analysis
Diff current vs target schema:
```
Detect:
  - New tables (safe)
  - New nullable columns (safe)
  - New non-null columns (requires default/backfill)
  - Column renames (requires dual-write period)
  - Column type changes (requires backfill + validation)
  - Index additions (CONCURRENTLY)
  - Index removals (safe)
  - Table removals (dangerous — require observation period)
  - Foreign key additions (requires backfill validation)
  - Constraint additions (requires validation pass first)
```

### Step 2: Risk Classification
| Change | Risk | Approach |
|---|---|---|
| Add nullable column | Low | Single migration |
| Add index | Low-Medium | CONCURRENTLY |
| Add non-null column | Medium | Expand-contract (3 phases) |
| Rename column | High | Dual-write (4 phases) |
| Change column type | High | Expand-contract with backfill |
| Drop column | Critical | 30-day observation after removal from code |
| Drop table | Critical | Archive first; drop after 90 days |

### Step 3: Migration Script Generation
For each change, generate:
```sql
-- Migration: V{number}__{description}
-- Risk: {LOW | MEDIUM | HIGH | CRITICAL}
-- Duration estimate: {X} minutes for {N} rows
-- Rollback: {rollback_sql or "manual process required"}
-- Author: {auto-detected from git config}
-- Date: {today}

BEGIN;
  {migration_sql}
COMMIT;
```

### Step 4: Backfill Script Generation (if required)
For large tables requiring data backfill:
```sql
-- Batched backfill with progress tracking
DO $$
DECLARE
  batch_size INT := 5000;
  processed  INT := 0;
  total      INT;
BEGIN
  SELECT COUNT(*) INTO total FROM {table} WHERE {condition};
  WHILE processed < total LOOP
    UPDATE {table} SET {new_column} = {expression}
    WHERE {condition} AND id IN (
      SELECT id FROM {table} WHERE {condition}
      ORDER BY id LIMIT batch_size
    );
    GET DIAGNOSTICS processed = processed + ROW_COUNT;
    PERFORM pg_sleep(0.05);  -- Rate limiting
  END LOOP;
END $$;
```

### Step 5: Verification Queries
Generated post-migration validation:
- Row counts (before vs after)
- Null check for new required columns
- Constraint validation
- Index usage validation
- Sample data integrity checks

### Step 6: Rollback Plan
Every migration ships with explicit rollback SQL and decision criteria.

---

## Output Artifacts
- `V{N}__{description}.up.sql` — Forward migration
- `V{N}__{description}.down.sql` — Rollback migration
- `V{N}__{description}.verify.sql` — Verification queries
- `V{N}__{description}.backfill.sql` — Backfill script (if applicable)
- `V{N}__{description}.plan.md` — Human-readable migration plan
