# UAIEOS Part 07: Context Engineering Manual

This manual defines the protocols for prompt construction, context window compression, dynamic context compiling, and cache optimization within the UAIEOS. Designing system prompts and managing context windows are critical to ensuring high accuracy, low latency, and optimal token economy.

---

## 1. System Prompt Constitutions

Every agent and workflow template inside UAIEOS must build system prompts using a standardized constitution. This structure guarantees alignment, safety, and operational consistency.

### 1.1 Constitutional Structure
1.  **Role & Persona Definition:** Specifies the operational identity and target domains (e.g., "You are an institutional security auditor...").
2.  **Capabilities & Rules:** List of tools the agent can call, along with strict constraints (e.g., "Do not execute bash commands directly").
3.  **Strict Output Specifications:** Format requirements (e.g., "You must output JSON conforming to the schema").
4.  **Error Handling & Guardrails:** Instructions for addressing invalid inputs or tool failures (e.g., "If validation fails, state the error and wait").

---

## 2. Context Window Compression

To handle large inputs without exceeding token limits or incurring high latency, inputs must be compressed prior to inference.

```
       ┌───────────────────[Raw Inputs: Log files, Code, Docs]──────────────────┐
       │                                                                        │
       ▼                                                                        ▼
  [Semantic Chunking]                                                   [AST Parsing]
  (Extract paragraphs, discard noise)                                   (Extract signatures, discard implementation)
       │                                                                        │
       └───────────────────────────────────┬────────────────────────────────────┘
                                           ▼
                            [Token Prioritization Filter]
                            (Retain high-salience elements)
                                           │
                                           ▼
                         [Compressed Output Payload to Model]
```

### 2.1 Chunking Strategies
*   **Semantic Chunking:** Splitting documents at paragraphs, headers, or structural markdown breaks instead of character limits. This maintains context coherence inside each block.
*   **AST Summarization:** For source code context, the engine strips method bodies and extracts class signatures, importing only the definition signatures to save up to $80\%$ of code space.

### 2.2 Token Prioritization Filter
If the total input token count exceeds the model's target threshold (e.g., $32\text{k}$ tokens on a high-speed engine), the context manager scores chunks using relative salience and drops low-priority chunks until the footprint conforms to limits.

---

## 3. Dynamic Context Construction

Dynamic context construction compiles the final payload sent to the LLM runtime at execution time, incorporating variables, user states, and cached blocks.

### 3.1 Token Cost Optimization Model
The context compiler estimates the transaction cost for a completion step using input, output, and caching pricing models:

$$\text{Cost}_{\text{transaction}} = (N_{\text{total}} - N_{\text{cached}}) \cdot P_{\text{input}} + N_{\text{cached}} \cdot P_{\text{cached\_discount}} + N_{\text{output}} \cdot P_{\text{output}}$$

Where:
*   $N_{\text{total}}$ is the total input token count.
*   $N_{\text{cached}}$ is the number of tokens matched in the provider's active prompt cache.
*   $P_{\text{input}}, P_{\text{cached\_discount}}, P_{\text{output}}$ are the per-token prices set by the provider.
*   **Optimization Rule:** Prompt layouts must place long static blocks (e.g., system instructions, database schemas) at the absolute beginning of the prompt. Dynamic variables (e.g., user inputs, conversation history) must be appended at the end to maximize the cached token footprint $N_{\text{cached}}$.

### 3.2 Dynamic Context Builder Schema
```json
{
  "system_constitution_ref": "file:///Users/dronpancholi/Developer/01_Strategic/Venus/templates/SYSTEM_PROMPT_CONSTITUTION.md",
  "static_schemas": [
    { "schema_name": "tool_database_query", "path": "file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_05_TOOL_ENGINEERING.md" }
  ],
  "dynamic_variables": {
    "current_time_utc": "2026-06-26T03:06:06Z",
    "active_user_context": "$.session.user_id",
    "retrieved_memory_chunks": "$.memory.retrieved_chunks"
  }
}
```

---

## 4. System Cross-References
*   To see the engine implementation that constructs prompts and compresses context states, see [ENGINE_CONTEXT_ORCHESTRATION.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/ENGINE_CONTEXT_ORCHESTRATION.md).
*   For token pricing optimization plans, caching guidelines, and GPU constraints, refer to [PART_13_AI_ECONOMICS.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_13_AI_ECONOMICS.md).
*   For details on querying, updating, and pruning episodic memories before injecting them into the context, refer to [PART_06_MEMORY_SYSTEMS.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_06_MEMORY_SYSTEMS.md).
