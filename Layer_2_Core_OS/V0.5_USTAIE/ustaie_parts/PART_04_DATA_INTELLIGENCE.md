# Part 04 — Data Intelligence

## 1. Polyglot Persistence & Data Design
Data Intelligence models the flow, storage format, and ownership boundaries of all system datasets. We map storage requirements to database engines: OLTP, OLAP, Vector, Document, Columnar, or Graph.

---

## 2. Persistence Selection Matrix

| Database Type | Target Workload | Schema Profile | Example |
|---|---|---|---|
| **OLTP (Relational)** | ACID transactions, queries | Rigid, normalized schemas | PostgreSQL |
| **OLAP (Warehouse)** | Analytical scans, aggregations | Star / Snowflake schemas | BigQuery |
| **Vector DB** | Semantic search, embeddings | High-dimension float indices | pgvector / Pinecone |
| **Knowledge Graph** | Relationship tracing, loops | Node & Edge schema structures | Neo4j |
| **Document Store** | Semi-structured data, logs | Dynamic JSON fields | MongoDB |

---

## 3. Data Lakehouse Architecture
Data Lakehouse architectures decouple storage (e.g. GCS, S3) from compute using open table formats (e.g. Apache Iceberg, Delta):

```
[Raw App Data] ──► [S3 Object Storage (Parquet files)] ──► [Iceberg Catalog Metadata]
                                                            ▲
                                                            │
                                              [BigQuery / Spark Query Engine]
```

### 3.1 Schema Evolution Rules
*   *Backward Compatibility*: New schema additions must support default values; column deletions must be deprecated in code before database drops.

---

## 4. Data Intelligence Checklist
*   [ ] Selected storage engine matching workload profile (OLTP vs OLAP).
*   [ ] Defined primary data schemas with migration paths.
*   [ ] Checked database isolation indices.
*   [ ] Configured schema validation bounds at data boundaries.
