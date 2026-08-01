# Template: Alternative Analysis Report

## 1. Document Control
*   **Project Name**: [Project Name]
*   **Decision ID**: DEC-[UUID]
*   **Analysis Date**: [Date]
*   **Lead Analyst**: [Name]

---

## 2. Option Index & Rationale
*Detail the generated options, outlining why each was considered.*

*   **Option 1: PostgreSQL (Proposed)**
    *   *Category*: Relational Database.
    *   *Description*: Standard SQL transactional store.
    *   *Why it exists*: Outlines standard relational query joins with strict ACID safety.
*   **Option 2: MongoDB**
    *   *Category*: Document Store NoSQL.
    *   *Why it exists*: Designed for semi-structured document payloads where schemas are highly variable.
*   **Option 3: SQLite**
    *   *Category*: Embedded SQL.
    *   *Why it exists*: Eliminates network connection cost by running in-memory or on local files.

---

## 3. Option Evaluation Matrix

| Alternative Option | Key Advantage | Key Disadvantage | License Type |
|---|---|---|---|
| PostgreSQL | ACID compliance, JSONB support | Scalability requires sharding | PostgreSQL License (Permissive)|
| MongoDB | Dynamic schemas | Lacks complex multi-table joins | SSPL (Restrictive SaaS terms) |
| SQLite | Zero config, zero network latency | File locking limits concurrent writes| Public Domain (Permissive) |

---

## 4. Rejection Explanations
*Provide clear rationales explaining why non-recommended options were rejected.*

*   **MongoDB Rejection Rationale**: Rejected because SSPL license terms introduce compliance risks for our commercial cloud hosting framework.
*   **SQLite Rejection Rationale**: Rejected because concurrent write limits violate our Tier 4 scaling constraint (100,000 users).
