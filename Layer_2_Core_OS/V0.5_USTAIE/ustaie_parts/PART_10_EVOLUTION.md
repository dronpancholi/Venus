# Part 10 — Evolution

## 1. Zero-Downtime System Upgrades
Evolution models backward compatibility checks, API versioning pathways, database schema migrations, and feature flag lifecycles.

---

## 2. API Versioning Patterns
*   **Path-Based**: `/api/v1/users` (Standard, simple deprecation).
*   **Header-Based**: `Accept: application/vnd.venus.v1+json` (Modular, clean URLs).
*   **Query-Based**: `/api/users?version=1` (Flexible, ad-hoc calls).

---

## 3. Database Schema Evolution (Two-Phase Upgrades)
To perform zero-downtime database upgrades, migrations must use the two-phase approach:

```
[Phase 1: Write to Old & New] ──► [Phase 2: Migrate Old Data] ──► [Phase 3: Drop Old Columns]
```

### 3.1 Migration Rules
1.  *Never rename columns directly*: Create new column first, mirror writes in code, execute backfill script, then drop old column.
2.  *Backward Compatibility*: Database schemas must remain compatible with the currently running application build.

---

## 4. Evolution Checklist
*   [ ] Selected API versioning strategy.
*   [ ] Verified database migrations use the two-phase writing protocol.
*   [ ] Defined deprecation dates for legacy endpoints.
*   [ ] Verified feature flag toggle checks in code paths.
