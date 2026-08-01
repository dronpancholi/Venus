# PART 12 — Database Engineering
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## 1. Purpose

Database Engineering defines the selection criteria, schema design standards, migration lifecycle, performance tuning philosophy, indexing strategy, replication architecture, backup requirements, and operational governance for all persistence layers within VENUS systems.

---

## 2. Database Selection Framework

| Database Type | When to Choose | Technology Options |
|---|---|---|
| **Relational (OLTP)** | ACID transactions, complex joins, normalized data | PostgreSQL (primary), MySQL |
| **Document** | Flexible schema, JSON-native data, nested structures | MongoDB, Firestore |
| **Key-Value** | Caching, sessions, ephemeral data | Redis, DynamoDB |
| **Wide-Column** | High write throughput, time series, analytics | Cassandra, ScyllaDB |
| **Time-Series** | Metrics, monitoring, IoT data | TimescaleDB, InfluxDB |
| **Vector** | Semantic search, embeddings, AI similarity | pgvector, Pinecone, Weaviate |
| **Graph** | Relationship-heavy data (social, permissions, supply chain) | Neo4j, Amazon Neptune |
| **Search** | Full-text search, faceted filtering | Elasticsearch, OpenSearch |
| **OLAP / Analytics** | Complex aggregations, large datasets, BI | BigQuery, ClickHouse, Redshift |

**VENUS Default**: PostgreSQL for primary application data. Introduce additional databases only when there is a justified, documented technical requirement.

---

## 3. Schema Design Standards

### 3.1 Naming Conventions (PostgreSQL)
```sql
Tables:       snake_case, plural nouns    — orders, order_items, user_accounts
Columns:      snake_case                  — created_at, user_id, total_amount
Primary Keys: uuid (UUID v7 preferred)   — id UUID DEFAULT uuid_generate_v7()
Foreign Keys: {table_singular}_id        — order_id, user_id
Indexes:      idx_{table}_{column(s)}    — idx_orders_user_id
Constraints:  chk_{table}_{description} — chk_orders_positive_amount
Sequences:    {table}_{column}_seq       — orders_id_seq
```

### 3.2 Mandatory Columns
Every table must include:
```sql
id          UUID        PRIMARY KEY DEFAULT uuid_generate_v7(),
created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
deleted_at  TIMESTAMPTZ           -- Soft delete (nullable)
```

### 3.3 Normalization Standard
- Minimum 3NF for all transactional data
- Selective denormalization only when justified by performance profiling
- Never store computed values that can be derived from stored data
- JSON columns only for genuinely schemaless or highly variable data

---

## 4. Migration Engineering

### 4.1 Migration Principles
- All schema changes managed through migration files (never manual SQL)
- Migrations are numbered, sequenced, and immutable once merged
- Every migration must be: **backward-compatible** (dual-write, expand/contract pattern)
- Zero-downtime migrations required for production

### 4.2 Expand-Contract Pattern
```
Phase 1 (Expand):   Add new column (nullable, no constraint)
Phase 2 (Migrate):  Backfill data; application writes to both columns
Phase 3 (Contract): Remove old column after 100% data backfill verified
```

### 4.3 Migration File Structure
```
migrations/
  V001__create_users_table.sql
  V002__add_email_to_users.sql
  V003__create_orders_table.sql
  V004__add_index_orders_user_id.sql

Each file contains:
  -- Migration: V004
  -- Description: Add index for user_id lookup on orders
  -- Author: engineer@example.com
  -- Date: 2024-01-15
  -- Rollback: DROP INDEX idx_orders_user_id;

  CREATE INDEX CONCURRENTLY idx_orders_user_id ON orders(user_id);
```

---

## 5. Indexing Strategy

### 5.1 Index Requirements
| Query Pattern | Index Type |
|---|---|
| Equality lookup on foreign key | B-tree index |
| Range queries (dates, amounts) | B-tree index with range clause |
| Full-text search | GIN index with tsvector |
| JSON field lookup | GIN index with jsonb_path_ops |
| Partial filter | Partial index with WHERE clause |
| Multi-column lookup | Composite index (column order matters) |
| Vector similarity | IVFFlat or HNSW (pgvector) |

### 5.2 Index Anti-Patterns
- Never index a column with < 10 distinct values (low cardinality)
- Never index every column "just in case"
- Monitor index bloat and rebuild periodically
- Use `CONCURRENTLY` for all production index creation

---

## 6. Performance Standards

| Metric | Target | Alert Threshold |
|---|---|---|
| OLTP query p95 response time | < 10ms | > 50ms |
| OLTP query p99 response time | < 50ms | > 200ms |
| Connection pool utilization | < 70% | > 85% |
| Cache hit rate (Redis) | > 90% | < 80% |
| Slow query count (> 100ms) | 0 per hour | > 5 per hour |
| Replication lag | < 100ms | > 1000ms |

---

## 7. Replication & High Availability

### 7.1 PostgreSQL HA Architecture
```
Primary (Read/Write)
    ├── Synchronous Replica 1 (Hot Standby)
    └── Asynchronous Replica 2 (Read Replica — analytics queries)

Failover: Automated via Patroni or RDS Multi-AZ
RPO: < 1 minute
RTO: < 30 seconds
```

### 7.2 Backup Policy
| Backup Type | Frequency | Retention | Storage |
|---|---|---|---|
| Continuous WAL | Real-time | 7 days | Encrypted S3 |
| Daily snapshot | Daily 02:00 UTC | 30 days | Encrypted S3 |
| Weekly snapshot | Sunday 04:00 UTC | 1 year | Encrypted S3 Glacier |
| Annual snapshot | January 1st | 7 years | Encrypted S3 Deep Archive |

**Restore testing**: Quarterly full restore drill is mandatory.

---

## 8. Database Security Standards

- Separate database users per service (principle of least privilege)
- No application connects as `root` or superuser
- All connections use SSL/TLS
- Credentials managed through secrets manager (never hardcoded)
- Audit logging enabled for all DDL operations
- Row-Level Security (RLS) for multi-tenant schemas
- Encryption at rest enabled for all production databases
