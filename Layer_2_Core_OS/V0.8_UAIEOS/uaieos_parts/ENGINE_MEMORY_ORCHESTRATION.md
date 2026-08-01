# UAIEOS Engine: Memory Orchestration Engine

This document defines the operational architecture, synchronization engines, databases, and background pruning algorithms for the Memory Orchestration Engine. This engine manages session storage, updates semantic indexes, and compiles episodic histories.

---

## 1. Engine Overview & Core Functions

The Memory Orchestration Engine acts as the central coordinator for all memory partitions (working, session, semantic, episodic, and long-term).

```
                         [Agent Read/Write Event]
                                    │
                                    ▼
                       [Memory Orchestration Engine]
                          ├── In-Memory Cache (Redis)
                          ├── Vector Index Sync (Qdrant)
                          └── Background Consolidation
                                    │
             ┌──────────────────────┼──────────────────────┐
             ▼                      ▼                      ▼
     [Session Memory]      [Episodic Database]     [Semantic Index]
```

### 1.1 Core Functions
1.  **Partition Synchronization:** Coordinates context window variables with backing databases (Redis/Spanner) to maintain consistent state.
2.  **Episodic Memory Compilation:** Runs background tasks to group raw session chats into concise episodic vectors.
3.  **Dynamic Pruning Loop:** Computes salience scores and drops or compresses low-value memory nodes.
4.  **Semantic Index Updating:** Appends factual assertions discovered during execution to the semantic index.

---

## 2. Technical Architecture & Algorithms

### 2.1 Background Consolidation Cycle
Consolidation runs as an asynchronous cron job:
1.  The scheduler scans for completed agent sessions.
2.  A consolidation worker reads the raw session logs.
3.  The worker extracts key facts, error codes, and solutions, compiling them into a semantic schema.
4.  The schema is embedded and written to the episodic vector database.
5.  Raw session records are moved to cold archival storage.

### 2.2 Salience Decay Execution
The engine runs a nightly pruning sweep over the episodic database. For each memory node $M_i$:
1.  It retrieves the timestamp and calculates the elapsed time $t - t_0$.
2.  It reads the total access count $F_i$.
3.  It updates the salience value:

$$\text{Salience}(M_i, t) = w_r \cdot e^{-\lambda (t - t_0)} + w_f \cdot \log_{10}(F_i + 1) + w_s \cdot S_i$$

4.  If $\text{Salience} < 0.20$, the node is deleted from the active vector index.

---

## 3. Data Protocols & Schemas

### 3.1 Memory Record Entry Schema
This schema defines a single entry inside the episodic database:

```json
{
  "node_id": "mem-ep-1002",
  "session_ref": "sess-agent-99218",
  "timestamp_created": "2026-06-26T00:00:00Z",
  "timestamp_last_accessed": "2026-06-26T03:06:06Z",
  "access_frequency": 4,
  "base_importance_score": 0.80,
  "salience_score": 0.87,
  "content_summary": "Encountered a seccomp violation on syscall: fork during code compilation task. Resolved by implementing gVisor sandbox.",
  "vector_embedding_ref": "qdrant://collection/episodic/1002"
}
```

### 3.2 Memory Recall Query Payload
Agents recall context by sending query requests:

```json
{
  "session_id": "sess-agent-99218",
  "query_text": "How do I compile python code safely?",
  "top_k": 3,
  "partition_targets": ["episodic", "semantic"]
}
```

---

## 4. Integration & Commands

Administrators manage memory systems and trigger manual consolidation runs using command-line arguments.

### 4.1 Trigger Manual Memory Consolidation
```bash
python -m uaieos.engines.memory_orchestrator --action consolidate-session --session-id sess-agent-99218
```
*Expected Output:*
```json
{
  "session_id": "sess-agent-99218",
  "status": "CONSOLIDATED",
  "extracted_nodes": 1,
  "archive_status": "COMPLETED"
}
```

### 4.2 Query Memory Index Status
```bash
python -m uaieos.engines.memory_orchestrator --action status
```
*Expected Output:*
```json
{
  "redis_active_sessions": 14,
  "vector_index_dimensions": 1536,
  "total_semantic_nodes": 1280,
  "total_episodic_nodes": 14092,
  "nodes_pruned_last_24h": 412
}
```

---

## 5. System Cross-References
*   For the memory partition descriptions, salience weights, and decay rules, see [PART_06_MEMORY_SYSTEMS.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_06_MEMORY_SYSTEMS.md).
*   For details on vector search embeddings and similarity metrics, see [PART_01_AI_FOUNDATIONS.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_01_AI_FOUNDATIONS.md).
*   For retrieval pipelines, index configurations, and vector database scaling models, refer to [ENGINE_RAG_ORCHESTRATION.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/ENGINE_RAG_ORCHESTRATION.md).
