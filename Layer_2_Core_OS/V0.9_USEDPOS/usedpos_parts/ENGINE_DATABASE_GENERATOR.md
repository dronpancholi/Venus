# ENGINE — Database Generator
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## Purpose
Generates complete database schemas, migration files, seed data, repository implementations, and performance validation for any service's persistence layer. Applies all database engineering standards from Part 12.

---

## Input Requirements
```
Required:
  - Domain entities and their attributes
  - Relationships between entities
  - Expected query patterns (what queries will run most frequently)
  - Expected data volume and growth rate
  - Consistency requirements (ACID / eventual)

Optional:
  - Performance targets (p95 query time)
  - Compliance requirements (GDPR, HIPAA — affects encryption/retention)
  - Multi-tenant requirements
  - Historical data requirements
```

---

## Generation Process

### Step 1: Entity-Relationship Analysis
- Parse domain entities from DDD model
- Identify cardinality of relationships
- Normalize to 3NF
- Identify denormalization candidates from query patterns

### Step 2: Schema Generation (PostgreSQL Default)
For each entity:
```sql
-- Generated schema includes:
CREATE TABLE {table_name} (
  id          UUID        PRIMARY KEY DEFAULT uuid_generate_v7(),
  -- domain columns
  tenant_id   UUID        NOT NULL REFERENCES tenants(id),  -- if multi-tenant
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at  TIMESTAMPTZ  -- soft delete
);
```

Apply naming conventions from Part 12 standards.

### Step 3: Index Generation
Analyze query patterns and generate indexes:
- Foreign key indexes (always)
- Frequently filtered columns (WHERE clause analysis)
- Sort columns (ORDER BY analysis)
- Full-text search (GIN indexes)
- Partial indexes (WHERE deleted_at IS NULL)

### Step 4: Migration Generation
Generate numbered migration files in expand-contract format:
- Up migration
- Down migration (where safe)
- Rollback risk assessment
- Execution time estimate for large tables

### Step 5: Repository Implementation Generation
For each aggregate:
- Repository interface (domain layer)
- PostgreSQL implementation (infrastructure layer)
- Optimistic locking (version column)
- Soft delete support
- Pagination support (cursor and offset)

### Step 6: Performance Validation Queries
Generate EXPLAIN ANALYZE queries for all critical paths.
Target: All OLTP queries < 10ms p95.

---

## Row-Level Security (Multi-Tenant)
When multi-tenant flag set:
- RLS policies generated per table
- Tenant context injection in middleware
- Test suite validates tenant isolation

---

## Seed Data Generation
- Development seed with realistic fake data (Faker.js)
- Test fixtures per entity type
- Performance test data set (1M rows per major table)
