# Database Schema Definition
**Document ID:** VENUS-STD-033
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Table Definitions (PostgreSQL 16)
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE RESTRICT NOT NULL,
    balance DECIMAL(18, 4) DEFAULT 0.0000 NOT NULL,
    currency VARCHAR(3) NOT NULL,
    status VARCHAR(20) NOT NULL,
    CONSTRAINT check_positive_balance CHECK (balance >= 0.0000)
);

CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_account_id UUID REFERENCES accounts(id) ON DELETE RESTRICT NOT NULL,
    target_account_id UUID REFERENCES accounts(id) ON DELETE RESTRICT NOT NULL,
    amount DECIMAL(18, 4) NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
```

---

## 2. Reusable Checklist & Exit Criteria
*   [ ] Checked that DDL scripts define strict constraints (NOT NULL, CHECK).
*   [ ] Verified referencing foreign keys enforce ON DELETE RESTRICT constraints.
*   [ ] Confirmed data types match payload definitions.
