# Token Optimization & Caching Plan
**Document ID:** Venus-UAIEOS-TEMP-31  
**Version:** V0.8  
**Classification:** Institutional-Grade Operations Template  
**Target Directory:** `file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_templates/`  

---

## 1. Executive Summary & Objectives

To scale LLM-based agent networks cost-effectively, applications must optimize their token utilization. Context windows represent the largest driver of system cost and latency.

This document outlines the **Token Optimization & Caching Plan** to:
1. Define the multi-tier caching architecture (Semantic Cache vs Provider Context Cache).
2. Formulate optimization metrics (Cache Hit Ratio, Effective Latency).
3. Establish prompt structuring guidelines that maximize prefix cache matching.
4. Define cache TTL (Time to Live) and eviction rules.

---

## 2. Multi-Tier Caching Architecture

Our caching strategy is divided into two primary execution layers:
1.  **Semantic Cache Layer (Local):** Intercepts queries before sending them to the model by performing similarity searches against historical prompts.
2.  **Context Prefix Cache Layer (Provider):** Structuring API requests to ensure that static, repetitive context resides at the beginning of the prompt.

```mermaid
graph TD
    User[User Prompt / Agent Request] --> B[Semantic Cache Interceptor]
    B -->|Query Vector Store| C{Semantic Hit? Cos > 0.95}
    C -->|Yes| D[Return Cached Response]
    C -->|No| E[Provider Prefix Cache Structuring]
    E --> F[API Request to LLM Provider]
    F --> G{Provider Cache Match?}
    G -->|Yes (Fast / Cheap)| H[Generate Output / Update Semantic Cache]
    G -->|No (Full Price / Slow)| I[Compile Context / Update Semantic Cache]
    H & I --> UserOutput[Final Output]
```

---

## 3. Metrics & Mathematical Formulations

### 3.1 Cache Hit Ratio (CHR)
The performance efficiency of the caching framework is measured by:

$$\text{CHR} = \frac{H}{H + M}$$

Where $H$ is the number of cache hits and $M$ is the number of cache misses over a given time interval.

### 3.2 Semantic Similarity Matching
For the local semantic cache, input prompts $\mathbf{u}_1$ and $\mathbf{u}_2$ are evaluated for similarity:

$$\text{Cos}(\mathbf{u}_1, \mathbf{u}_2) = \frac{\mathbf{u}_1 \cdot \mathbf{u}_2}{\|\mathbf{u}_1\| \|\mathbf{u}_2\|}$$

If $\text{Cos}(\mathbf{u}_1, \mathbf{u}_2) \ge \theta_{\text{threshold}}$ (default $\theta = 0.95$), the cached response is served.

### 3.3 Effective Latency ($L_{\text{eff}}$)
The overall latency footprint of the request pipeline is defined as:

$$L_{\text{eff}} = \text{CHR} \cdot L_{\text{cache}} + (1 - \text{CHR}) \cdot L_{\text{miss}}$$

Where $L_{\text{cache}}$ is the local cache lookup latency (~5-15ms) and $L_{\text{miss}}$ is the full LLM execution latency (~800-4000ms).

---

## 4. Prompt Structuring Guidelines for Prefix Caching

Providers (such as Anthropic and Google Gemini) cache segments of prompts if they are identical in prefix. To maximize hit rates, structure prompts using the **Stable-to-Dynamic Ordering Standard**:

```markdown
┌──────────────────────────────────────────────────────────┐
│ STABLE PREFIX: System Prompt & Safety Guidelines         │
│ (Changes rarely - Always placed first)                   │
├──────────────────────────────────────────────────────────┤
│ SEMI-STABLE CONTEXT: System Schema & Function Specs      │
│ (Changes only during API updates)                        │
├──────────────────────────────────────────────────────────┤
│ FEW-SHOT EXAMPLES: Curated static Input/Output pairs     │
│ (Identical across all runs of this agent)                │
├──────────────────────────────────────────────────────────┤
│ DYNAMIC RETRIEVED CONTEXT: RAG Documents                 │
│ (Changes per query, but should be clustered if possible) │
├──────────────────────────────────────────────────────────┤
│ DYNAMIC PROMPT: User Query / Iterative Agent Instruction │
│ (Changes constantly - Always placed last)                │
└──────────────────────────────────────────────────────────┘
```

> [!IMPORTANT]
> Any mutation in the stable prefix (even a trailing space or altered punctuation) invalidates the entire downstream cache block. System prompts must be trimmed and formatted deterministically.

---

## 5. Cache Eviction & Invalidation Policy

| Cache Pool | Target Memory Type | Default TTL | Eviction Policy | Invalidation Trigger |
|---|---|---|---|---|
| **Semantic Cache** | Redis Vector DB | 24 Hours | LRU (Least Recently Used) | Data update on source reference DB |
| **Embedding Cache**| Local Memcached | 72 Hours | LFU (Least Frequently Used)| Model endpoint migration / update |
| **Context Prefix** | Model Provider | 300 Seconds | Provider-Managed | Prompt structure change |

---

## 6. Implementation Reference (Semantic Cache Setup)

```python
"""
Venus Semantic Cache Engine
"""
from typing import Optional, Tuple
import numpy as np

class SemanticCache:
    def __init__(self, vector_db_client, embedding_model, threshold: float = 0.95):
        self.db = vector_db_client
        self.embed = embedding_model
        self.threshold = threshold
        
    def get(self, query: str) -> Tuple[Optional[str], float]:
        """
        Queries vector store for semantic matches.
        """
        query_vector = self.embed.get_embedding(query)
        match = self.db.search_nearest(query_vector, limit=1)
        
        if match:
            similarity = match[0].score # Cosine similarity
            if similarity >= self.threshold:
                return match[0].response_text, similarity
            return None, similarity
        return None, 0.0

    def set(self, query: str, response: str) -> None:
        """
        Saves query, its embedding, and response to semantic database.
        """
        query_vector = self.embed.get_embedding(query)
        self.db.insert(query, query_vector, response)
```

---
*For systems engineering and cache scale tuning, contact the caching infrastructure lead at [Venus Systems](file:///Users/dronpancholi/Developer/01_Strategic/Venus/).*
