# Aggregate Root Schema Specification

## Document Control
| Version | Date | Author | Description | Reviewer |
| :--- | :--- | :--- | :--- | :--- |
| 1.0.0 | 2026-06-26 | Database Architect | Aggregate serialization schemas | Lead Developer |

## 1. Context & Lifecycle
This document defines schemas for validating the serialized state of aggregates when persisted in document databases or logged for transactional event sourcing.
- For domain definitions, see [DOMAIN_MODEL_SPECIFICATION.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/DOMAIN_MODEL_SPECIFICATION.md).
- Event logs are detailed in [EVENT_CATALOG_SPECIFICATION.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/EVENT_CATALOG_SPECIFICATION.md).

---

## 2. Account Aggregate Root JSON Schema
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "AccountAggregateRoot",
  "description": "JSON representation of the Account Aggregate Root state for storage and validation.",
  "type": "object",
  "properties": {
    "aggregate_id": {
      "type": "string",
      "format": "uuid"
    },
    "version": {
      "type": "integer",
      "minimum": 0
    },
    "owner_id": {
      "type": "string",
      "pattern": "^usr_[a-zA-Z0-9]+$"
    },
    "balance": {
      "type": "object",
      "properties": {
        "amount": { "type": "number" },
        "currency": { "type": "string", "pattern": "^[A-Z]{3}$" }
      },
      "required": ["amount", "currency"]
    },
    "status": {
      "type": "string",
      "enum": ["ACTIVE", "SUSPENDED", "CLOSED"]
    },
    "limits": {
      "type": "object",
      "properties": {
        "max_daily_limit": { "type": "number", "minimum": 0 },
        "overdraft_limit": { "type": "number", "minimum": 0 }
      },
      "required": ["max_daily_limit", "overdraft_limit"]
    }
  },
  "required": ["aggregate_id", "version", "owner_id", "balance", "status", "limits"]
}
```

---

## 3. Database Mapping Specification (PostgreSQL JSONB)
When storing the aggregate state in a relational system, the following table and constraints apply:

```sql
CREATE TABLE account_aggregates (
    aggregate_id UUID PRIMARY KEY,
    version INT NOT NULL,
    owner_id VARCHAR(50) NOT NULL,
    state JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_version_non_negative CHECK (version >= 0)
);

-- Optimize queries searching on deep JSON properties
CREATE INDEX idx_accounts_owner ON account_aggregates ((state->>'owner_id'));
CREATE INDEX idx_accounts_status ON account_aggregates ((state->>'status'));
```
Refer to [DATABASE_INDEXING_QUERY_PLAN.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/DATABASE_INDEXING_QUERY_PLAN.md) for more details on indexing parameters.
