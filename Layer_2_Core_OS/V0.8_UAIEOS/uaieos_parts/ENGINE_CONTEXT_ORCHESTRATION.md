# UAIEOS Engine: Context Orchestration Engine

This document defines the operational architecture, compression algorithms, compiler pipelines, and cache optimizations for the Context Orchestration Engine. This engine manages token allocations and constructs prompt payloads before model inference.

---

## 1. Engine Overview & Core Functions

The Context Orchestration Engine sits ahead of the Model Intelligence routing layer, assembling and optimizing context inputs.

```
                  [Raw Prompts, Memory, Docs]
                               │
                               ▼
                 [Context Orchestration Engine]
                    ├── Token Allocator
                    ├── AST/Semantic Compactor
                    └── Prompt Cache Matcher
                               │
                               ▼
                   [Optimized Token Stream]
                               │
                               ▼
                  [Model Intelligence Engine]
```

### 1.1 Core Functions
1.  **Dynamic Context Assembly:** Combines system prompts, tools, memory context, and user history into a structured prompt layout.
2.  **Context Compaction:** Runs semantic chunking and AST extractions to compress large payloads.
3.  **Prompt Cache Optimization:** Orders prompt layers to maximize matching with the provider's active prompt cache.
4.  **Token Limit Guard:** Audits total token counts and drops low-salience chunks to prevent out-of-memory exceptions.

---

## 2. Technical Architecture & Algorithms

### 2.1 Prompt Layout Priority
To maximize prefix cache match rates, prompts must be organized in a strict top-down structure:

1.  **Static System Constitution:** Statically defined rules and system directives (must be $100\%$ identical across executions).
2.  **Tool Declarations:** JSON schemas of available tools (infrequently modified).
3.  **Grounding Context (RAG):** Retrieved background documents.
4.  **Episodic Memory Chunks:** Extracted experience logs.
5.  **Conversation/Workflow History:** Multi-turn session logs (highly dynamic).
6.  **Current User Query:** The final execution trigger.

*By placing dynamic variables at the absolute end, the upstream layers ($1, 2, 3$) can be matched in the provider's KV cache, reducing inference latency by up to $80\%$.*

### 2.2 Context Scaling Optimization Function
The engine runs a mathematical token-cost filter before dispatching queries:

$$\text{Cost}_{\text{estimate}} = (N_{\text{total}} - N_{\text{cached}}) \cdot P_{\text{input}} + N_{\text{cached}} \cdot P_{\text{cached\_discount}}$$

If $\text{Cost}_{\text{estimate}} > \text{Budget}_{\text{allocated}}$ or $N_{\text{total}} > \text{Limit}_{\text{model}}$, the compiler drops low-priority chunks from the grounding and episodic layers until:

$$N_{\text{total}} \le \min(\text{Limit}_{\text{model}}, \text{Limit}_{\text{target}})$$

---

## 3. Data Protocols & Schemas

### 3.1 Context Compiler Spec Schema
This schema configures how context elements are retrieved and compiled:

```json
{
  "compiler_profile": "agent_coder_context",
  "target_model_limit": 32768,
  "cache_optimization_enabled": true,
  "layers": [
    { "layer_index": 1, "source": "system_constitution", "importance": 1.0, "caching_anchor": true },
    { "layer_index": 2, "source": "tool_schemas", "importance": 1.0, "caching_anchor": true },
    { "layer_index": 3, "source": "rag_grounding_docs", "importance": 0.6, "caching_anchor": false },
    { "layer_index": 4, "source": "episodic_memories", "importance": 0.4, "caching_anchor": false },
    { "layer_index": 5, "source": "session_history", "importance": 0.8, "caching_anchor": false }
  ]
}
```

### 3.2 Compiled Output Telemetry Schema
The engine logs compilation results to track token efficiency:

```json
{
  "compilation_id": "comp-7716a",
  "timestamp_utc": "2026-06-26T03:06:06Z",
  "raw_input_tokens": 42092,
  "compiled_output_tokens": 12840,
  "compression_ratio": 3.27,
  "cache_match_potential_tokens": 8192,
  "discarded_chunks_count": 4
}
```

---

## 4. Integration & Commands

Administrators inspect compiled outputs and verify caching efficiency using CLI utilities.

### 4.1 Preview Compiled Context
```bash
python -m uaieos.engines.context_orchestrator --action compile-preview --profile agent_coder_context --session-id sess-agent-99218
```
*Expected Output:*
```json
{
  "compilation_status": "SUCCESS",
  "total_tokens": 12840,
  "expected_cache_hits": 8192,
  "preview_snippet": "SYSTEM: You are a senior engineer... TOOLS: ... USER: How do I compile..."
}
```

### 4.2 Query Token Statistics
```bash
python -m uaieos.engines.context_orchestrator --action stats
```
*Expected Output:*
```json
{
  "total_tokens_compiled_24h": 12049102,
  "average_compression_ratio": 2.45,
  "average_cache_hit_rate": 0.68,
  "token_cost_saved_usd": 14.82
}
```

---

## 5. System Cross-References
*   For the system constitution guidelines, token compression policies, and prompt sizing rules, see [PART_07_CONTEXT_ENGINEERING.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_07_CONTEXT_ENGINEERING.md).
*   For token pricing vector databases, caching discounts, and economic constraints, see [PART_13_AI_ECONOMICS.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_13_AI_ECONOMICS.md).
*   For the model intelligence router interface and endpoint connections, refer to [ENGINE_MODEL_INTELLIGENCE.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/ENGINE_MODEL_INTELLIGENCE.md).
