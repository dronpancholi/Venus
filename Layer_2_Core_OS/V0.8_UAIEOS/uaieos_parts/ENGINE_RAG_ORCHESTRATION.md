# UAIEOS Engine: RAG Orchestration Engine

This document defines the operational architecture, search execution pipelines, rank merging algorithms, and grounding gates for the Retrieval-Augmented Generation (RAG) Orchestration Engine. This engine manages document indexes, executes hybrid searches, and validates response groundedness.

---

## 1. Engine Overview & Core Functions

The RAG Orchestration Engine executes search requests, combining keyword and semantic databases before passing results to the context compiler.

```
                         [User Query Input]
                                 │
                                 ▼
                     [RAG Orchestration Engine]
                        ├── Dense Vector Search (Qdrant)
                        ├── Lexical Keyword Search (BM25)
                        ├── RRF Rank Merger
                        └── Cross-Encoder Re-ranker
                                 │
                                 ▼
                    [Grounded Reference Chunks]
```

### 1.1 Core Functions
1.  **Hybrid Search Execution:** Runs parallel queries against dense vector and lexical text indexes.
2.  **Rank Fusion (RRF):** Blends dense and lexical rankings into a single sorted list.
3.  **Cross-Encoder Re-ranking:** Computes precise semantic relevance scores to select the top-k chunks.
4.  **Grounding Verification:** Audits output statements against source document contents.

---

## 2. Technical Architecture & Algorithms

### 2.1 The Retrieval-Rank-Filter Pipeline
When a query is received:
1.  **Parallel Search:** The engine dispatches the query embedding to the vector database and the keyword query to the lexical index.
2.  **RRF Blending:** The engine merges the result lists. The RRF score for document $d$ is:

$$\text{RRF\_Score}(d \in D) = \sum_{m \in \mathcal{M}} \frac{1}{60 + r_m(d)}$$

3.  **Re-ranking:** The top $N = 25$ documents are sent to a Cross-Encoder. Chunks are sorted descending by the Cross-Encoder score.
4.  **Chunk Selection:** The top $K = 5$ chunks are selected for context compilation.

### 2.2 Groundedness Auditing
Before delivering generated text, the engine checks for hallucinations:
1.  The text is split into assertions.
2.  Each assertion is compared to the source document chunks using an NLI classifier.
3.  If any assertion fails validation, the output is blocked.

---

## 3. Data Protocols & Schemas

### 3.1 Search Specification Configuration Schema
This schema defines retriever parameters:

```json
{
  "search_profile": "customer_support_kb",
  "vector_index": "kb_embeddings_prod",
  "lexical_index": "kb_text_prod",
  "retrieval_params": {
    "dense_weight": 0.5,
    "lexical_weight": 0.5,
    "rrf_k": 60,
    "top_n_to_rerank": 25,
    "top_k_final": 5
  },
  "reranker": {
    "model_name": "bge-reranker-large",
    "score_threshold": 0.40
  }
}
```

### 3.2 Grounding Evaluation Record Schema
The results of the grounding validation are logged for monitoring:

```json
{
  "evaluation_id": "eval-rag-1002",
  "query": "What is the return policy for hardware?",
  "generated_response": "Hardware returns are accepted within 30 days of purchase, provided items are in original packaging.",
  "grounding_results": {
    "assertions": [
      {
        "text": "Hardware returns are accepted within 30 days of purchase.",
        "verified": true,
        "source_chunk_ref": "kb_embeddings_prod:chunk-228",
        "nli_entailment_score": 0.992
      },
      {
        "text": "Items must be in original packaging.",
        "verified": true,
        "source_chunk_ref": "kb_embeddings_prod:chunk-229",
        "nli_entailment_score": 0.978
      }
    ],
    "faithfulness_score": 1.0,
    "status": "APPROVED"
  }
}
```

---

## 4. Integration & Commands

Administrators manage vector indexes and test query pipelines using CLI utilities.

### 4.1 Execute Test Search
```bash
python -m uaieos.engines.rag_orchestrator --action query --profile customer_support_kb --query "hardware return window"
```
*Expected Output:*
```json
{
  "query": "hardware return window",
  "results_returned": 2,
  "chunks": [
    { "id": "chunk-228", "rrf_score": 0.033, "rerank_score": 0.892, "text": "Hardware returns must be completed within 30 days..." },
    { "id": "chunk-229", "rrf_score": 0.028, "rerank_score": 0.814, "text": "All returned devices must be in original packaging..." }
  ]
}
```

### 4.2 Query Index Metrics
```bash
python -m uaieos.engines.rag_orchestrator --action status
```
*Expected Output:*
```json
{
  "active_indexes": ["kb_embeddings_prod", "kb_text_prod"],
  "total_documents": 14209,
  "total_chunks": 71045,
  "vector_search_p99_latency_ms": 32,
  "rerank_p99_latency_ms": 115
}
```

---

## 5. System Cross-References
*   For advanced RAG architectural patterns, chunking guidelines, and the RAG Triad framework, see [PART_08_RAG_ENGINEERING.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_08_RAG_ENGINEERING.md).
*   For details on vector models, dimension structures, and distance calculations, see [PART_01_AI_FOUNDATIONS.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_01_AI_FOUNDATIONS.md).
*   For memory index structures and vector synchronization routines, refer to [ENGINE_MEMORY_ORCHESTRATION.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/ENGINE_MEMORY_ORCHESTRATION.md).
