# Database Indexing & Query Plan
**Document ID:** VENUS-STD-034
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Indexing Strategy
To optimize query performance under high load, tables must compile indexes for search parameters.

```sql
-- Indexes for accounts retrieval
CREATE INDEX idx_accounts_user_id ON accounts(user_id);

-- Partial index for active transactions query
CREATE INDEX idx_transactions_active ON transactions(created_at) WHERE status = 'PENDING';
```

## 2. Query Plan Validation
Developers must analyze query plans using `EXPLAIN ANALYZE`:
```sql
EXPLAIN ANALYZE
SELECT * FROM transactions
WHERE source_account_id = 'c3b2a1-0000-1111-2222-333344445555'
ORDER BY created_at DESC;
```
*   *Exit Gate*: Query execution paths must utilize Index Scan instead of Seq Scan.

---

## 3. Reusable Checklist & Exit Criteria
*   [ ] Checked that foreign keys contain active indexing tags.
*   [ ] Verified `EXPLAIN ANALYZE` reports show zero Sequential Scans on large tables.
*   [ ] Confirmed partial indexes are generated for state flags where appropriate.
