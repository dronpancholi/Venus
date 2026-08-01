# Template: Knowledge Graph Design

## 1. Document Control
*   **Project Name**: [Project Name]
*   **Graph ID**: KG-DSN-[UUID]

---

## 2. Graph Schema & Node Definition
*Define the node types, labels, and relationship edges.*

```
                 +──────────────────────────────────────────────────+
                 |  (:User) -[:OWNS]-> (:Tenant)                    |
                 |  (:Tenant) -[:EXECUTES]-> (:Campaign)            |
                 |  (:Campaign) -[:ACQUIRES]-> (:Backlink)          |
                 +──────────────────────────────────────────────────+
```

---

## 3. Node & Edge Index Mappings

| Node Type | Properties | Indexes | Primary Unique Key |
|---|---|---|---|
| **User** | email, name, role | CREATE INDEX ON :User(email) | `user_id` (UUID) |
| **Tenant** | name, tier, region | CREATE INDEX ON :Tenant(id) | `tenant_id` (UUID) |
| **Campaign**| status, budget | None | `campaign_id` (UUID) |

---

## 4. Query Performance Optimizations
*   **Database Engine**: Neo4j Enterprise.
*   **Constraint Rule**: Enforce unique node key constraints on `user_id` and `tenant_id`.
*   *Index Policy*: Create indexes on all relationship properties (e.g. status fields) to optimize path traversal.
