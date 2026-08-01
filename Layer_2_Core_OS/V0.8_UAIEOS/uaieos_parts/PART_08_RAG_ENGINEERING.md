# UAIEOS Part 08: Retrieval-Augmented Generation (RAG) Engineering Manual

This manual defines the retrieval architectures, indexing schemes, ranking algorithms, and grounding methodologies for Retrieval-Augmented Generation (RAG) systems inside the UAIEOS. These standards ensure that foundation models are supplied with semantically relevant, factual, and structurally complete background data.

---

## 1. Retrieval Architectures

UAIEOS implements a tiered RAG architecture to support basic document search as well as agentic query resolution.

```
                   [Incoming User Query]
                             │
                             ▼
                 [Query Expansion & HyDE]
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
      [Dense Retrieval]               [Lexical Retrieval]
      (Vector search on HNSW)          (BM25 match on text index)
            │                                 │
            └────────────────┬────────────────┘
                             ▼
                 [Reciprocal Rank Fusion]
                             │
                             ▼
                   [Cross-Encoder Re-rank]
                             │
                             ▼
                  [Top-k Document Selection]
                             │
                             ▼
                 [Grounding & Faithfulness]
```

### 1.1 Standard RAG
Matches the raw query vector against document chunk vectors and appends the top-k matches to the prompt context.

### 1.2 Advanced RAG
*   **Query Expansion:** Uses an LLM to generate multiple search variations of the input query.
*   **HyDE (Hypothetical Document Embeddings):** Generates a draft answer to the query, and embeds the draft to search for similar documents, bypassing mismatching vocabulary.
*   **Hierarchical Retrieval:** Retrieves parent document blocks when a child chunk matches.

### 1.3 Agentic RAG
Enables agents to query indexes dynamically using tools, determining search parameters and processing output chunks iteratively.

---

## 2. Indexing & Storage

Efficient document search requires organizing raw text documents into optimized vector databases.

### 2.1 Chunking Policies
*   **Length:** Standard chunk size is $512\text{ tokens}$ with a $10\%$ ($51\text{ tokens}$) sliding overlap.
*   **Metadata Tagging:** Every chunk must be tagged with document ID, version, timestamp, access permissions, and a hash of the content to prevent duplicate indexing.

### 2.2 Vector Indexes
1.  **HNSW (Hierarchical Navigable Small World):** Used for low-latency queries. Standard construction parameters: $M = 16$ (bidirectional links per node), $ef\_construction = 200$.
2.  **IVF-PQ (Inverted File with Product Quantization):** Used for large datasets. Compresses vector representations to optimize memory footprint.

---

## 3. Hybrid Search & Re-ranking

Dense vector search is excellent for capturing semantic themes, but can miss exact keywords (e.g., serial numbers, names, code functions). Lexical search (BM25) is paired with dense search to resolve this.

### 3.1 Reciprocal Rank Fusion (RRF)
To combine dense vector matches and lexical BM25 results, the system calculates the Reciprocal Rank Fusion (RRF) score for each document $d$ in the union set $D$:

$$\text{RRF\_Score}(d \in D) = \sum_{m \in \mathcal{M}} \frac{1}{k + r_m(d)}$$

Where:
*   $\mathcal{M}$ is the set of retrievers (Dense Vector and Lexical BM25).
*   $r_m(d)$ is the position rank of document $d$ in retriever $m$'s result list (starting at $1$).
*   $k$ is a constant smoothing parameter (standardized to $60$ inside UAIEOS).
*   **Execution:** Documents are sorted descending by their $\text{RRF\_Score}$, and the top $N$ documents are sent to the re-ranking layer.

### 3.2 Cross-Encoder Re-ranking
The top $N$ documents are evaluated using a Cross-Encoder (e.g., Cohere or BGE re-ranker). Unlike dual-encoders (which compare pre-computed embeddings), the Cross-Encoder processes the query and document chunk simultaneously, calculating a high-precision relevance score. The top $K$ documents (where $K < N$) are then formatted into the LLM context.

---

## 4. Grounding & Hallucination Mitigation

To ensure facts inside LLM completions are sourced from retrieved documents, the system validates generations against the RAG Triad.

```
       ┌──────────────────────────────[Query]──────────────────────────────┐
       │                                                                   │
       ▼ (Answer Relevance)                                                ▼ (Context Relevance)
  [Response] ◄────────────────────── (Groundedness) ──────────────────► [Context]
```

### 4.1 The RAG Triad
1.  **Context Relevance:** Evaluates if the retrieved chunks are relevant to the query. Chunks with cosine similarity scores below $\theta_{\text{context}} = 0.60$ are dropped.
2.  **Groundedness (Faithfulness):** Validates if the generated response is supported *solely* by the retrieved context. The engine parses the response into discrete statements, and uses an NLI (Natural Language Inference) classifier or LLM validator to verify that each statement is logically entailed by the context:

$$\text{Groundedness\_Score} = \frac{\text{Number of Entailed Statements}}{\text{Total Statements in Response}}$$

*   **Policy Gate:** The system blocks delivery if the Groundedness Score is $< 1.00$.
3.  **Answer Relevance:** Assesses if the generated response directly answers the user's query.

### 4.2 Citation Attribution
Every fact in the response must append a explicit markdown link pointing to the source chunk identifier: `[Source Text](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_08_RAG_ENGINEERING.md#L123)`. Responses lacking explicit citation tags are rejected at the output boundary.

---

## 5. System Cross-References
*   To see the engine implementation executing search pipelines, RRF, and re-ranking, see [ENGINE_RAG_ORCHESTRATION.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/ENGINE_RAG_ORCHESTRATION.md).
*   For details on vector spaces and embedding algorithms, refer to [PART_01_AI_FOUNDATIONS.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_01_AI_FOUNDATIONS.md).
*   For protocols relating to semantic and episodic memory retrieval, refer to [PART_06_MEMORY_SYSTEMS.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_06_MEMORY_SYSTEMS.md).
