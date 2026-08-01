# Template: Database Blueprint

## 1. Document Control
*   **Project Name**: [Project Name]
*   **DB Blueprint ID**: DB-[UUID]
*   **Date**: [Date]

---

## 2. Entity Relationship Diagram (ERD Schema)
*Provide the database DDL schema outline.*

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transactions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    amount NUMERIC(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL
);
```

---

## 3. Storage Configuration & Scaling
*   **Database Engine**: PostgreSQL 15.
*   **Connection Limits**: Enforced PgBouncer pool ceiling at 100 concurrent connections.
*   **Partition Key**: Hashed user_id partition strategy.

---

## 4. Query Index optimization
*   [ ] Index created on `users(email)`.
*   [ ] Foreign key index created on `transactions(user_id)`.
*   [ ] Checked database read replication topology.
