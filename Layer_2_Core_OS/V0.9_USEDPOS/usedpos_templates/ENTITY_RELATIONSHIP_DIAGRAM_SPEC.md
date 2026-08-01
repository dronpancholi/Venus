# Entity Relationship Diagram (ERD) Specification
**Document ID:** VENUS-STD-032
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Core Models Relationships
```mermaid
erDiagram
    USERS ||--o{ ACCOUNTS : owns
    ACCOUNTS ||--o{ TRANSACTIONS : "source of"
    ACCOUNTS ||--o{ TRANSACTIONS : "destination of"
    TRANSACTIONS ||--|| AUDIT_LOGS : generates

    USERS {
        uuid id PK
        string email
        string password_hash
        timestamp created_at
    }
    ACCOUNTS {
        uuid id PK
        uuid user_id FK
        decimal balance
        string currency
        string status
    }
    TRANSACTIONS {
        uuid id PK
        uuid source_account_id FK
        uuid target_account_id FK
        decimal amount
        string status
        timestamp timestamp
    }
    AUDIT_LOGS {
        uuid id PK
        uuid transaction_id FK
        jsonb payload
        timestamp created_at
    }
```

---

## 2. Reusable Checklist & Exit Criteria
*   [ ] Checked that foreign keys have explicit indexes to avoid full table scans.
*   [ ] Verified database schemas mirror ERD keys and relationships.
*   [ ] Confirmed field constraint definitions prevent orphan database states.
