# PROJECT VENUS — INSTITUTIONAL MEMORY ARCHITECTURE

**Version**: 1.0  
**Purpose**: Persistent memory system that stores, retrieves, and evolves all institutional knowledge.

---

## 1. Memory Partitions

```
┌─────────────────────────────────────────────────────┐
│                  Memory Server                       │
│  ┌────────────┐ ┌───────────┐ ┌─────────────────┐  │
│  │  Semantic   │ │  Episodic │ │   Procedural     │  │
│  │  (concepts) │ │ (actions)  │ │  (how-to)       │  │
│  └──────┬──────┘ └─────┬─────┘ └───────┬─────────┘  │
│  ┌──────┴──────┐ ┌─────┴─────┐ ┌───────┴─────────┐  │
│  │  Decision    │ │  Research  │ │   Project       │  │
│  │  (why)      │ │ (findings) │ │  (state)        │  │
│  └─────────────┘ └───────────┘ └─────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### 1.1 Semantic Memory
- **Content**: Concepts, types, ontologies, schemas, entity definitions
- **Storage**: Vector database (embeddings for nearest-neighbor search)
- **Retrieval**: Similarity search by embedding
- **Update**: Full rebuild on ontology change; incremental on entity add

### 1.2 Episodic Memory
- **Content**: Every action, decision, plan, execution trace
- **Storage**: Time-ordered append-only log
- **Retrieval**: Timeline queries, filterable by agent/task/result
- **Update**: Each completed action appends a record

### 1.3 Procedural Memory
- **Content**: Agent workflows, validation sequences, compilation steps
- **Storage**: Structured procedure definitions (JSON/YAML)
- **Retrieval**: By procedure name or goal
- **Update**: Versioned; new versions supersede old

### 1.4 Decision Memory
- **Content**: ADRs, tradeoff analyses, rejected alternatives
- **Storage**: Canonical ADR schema (see _schemas/decision_record.json)
- **Retrieval**: By decision ID, date range, affected entity
- **Update**: Once finalized, append-only (supersede flag for reversals)

### 1.5 Research Memory
- **Content**: Research findings, analyses, external references
- **Storage**: Structured research records with source attribution
- **Retrieval**: By topic, date, source
- **Update**: New findings append; corrections supersede

### 1.6 Project Memory
- **Content**: Current project state, active goals, task status
- **Storage**: Lightweight state documents
- **Retrieval**: Fast read of current project snapshot
- **Update**: Continuous real-time updates

---

## 2. Memory Operations

| Operation | Description | Sync/Async |
|-----------|-------------|------------|
| `store(type, key, data)` | Write to memory partition | Async |
| `read(type, key)` | Direct key lookup | Sync |
| `search(type, query, n)` | Semantic similarity search | Sync |
| `query(type, filter)` | Structured query with filters | Sync |
| `transact(type, key, ttl)` | Lock-and-modify transaction | Sync |
| `evict(type, key, policy)` | Remove under LRU/age policy | Sync |
| `reindex(type)` | Rebuild vector index | Async |
| `snapshot()` | Full memory snapshot | Async |

---

## 3. Memory Schema

Defined in `memory_schema.json` — base structure shared by all memory types.

---

## 4. Vector Search Configuration

- **Embedding model**: text-embedding-ada-002 (or local equivalent)
- **Index type**: HNSW (Hierarchical Navigable Small World)
- **Dimensions**: 1536
- **Similarity metric**: Cosine distance
- **Chunking**: 512-token overlap window, 128-token stride
