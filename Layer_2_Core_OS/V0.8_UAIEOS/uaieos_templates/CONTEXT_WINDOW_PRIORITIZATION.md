# Context Window Prioritization Specification (Project Venus V0.8)

## 1. Context Window Budget Allocation
This specification defines how the host runtime segments, prioritzes, and limits token allocations within a model's context window. Proper budgeting prevents context truncation errors, control-instruction dilution, and excessive token usage costs.

```
┌────────────────────────────────────────────────────────┐
│ Total Context Window (e.g., 32,768 Tokens)            │
├───────────┬─────────────┬──────────────┬───────────────┤
│ System    │ RAG Docs    │ Session Chat │ Output Buffer │
│ Prompt    │ (Semantic)  │ History      │ (Generation)  │
│ (10%)     │ (40%)       │ (30%)        │ (20%)         │
└───────────┴─────────────┴──────────────┴───────────────┘
```

---

## 2. Dynamic Token Budgeting Model
Token allocations are scaled dynamically using a resource reservation script.

| Context Segment | Reservation % | Token Budget (32k Window) | Truncation / Eviction Priority |
| :--- | :--- | :--- | :--- |
| **System Prompt** | $10\%$ | $3,276$ tokens | **Priority 0 (Never Evict)** |
| **Tool Definition Schema** | $15\%$ | $4,915$ tokens | **Priority 1 (Never Evict)** |
| **Retrieved Context (RAG)** | $35\%$ | $11,468$ tokens | **Priority 4 (Evict Lowest Similarity)** |
| **Chat History / Conversational Turns**| $25\%$ | $8,192$ tokens | **Priority 3 (Apply Sliding Window/Summary)**|
| **Generation Buffer (Output)** | $15\%$ | $4,915$ tokens | **Priority 2 (Fixed Allocation)** |

---

## 3. Eviction & Summarization Algorithms

### 3.1 Chat History Sliding Window & Summarization
When the token count of active chat history $T_{\text{history}}$ exceeds its allocation ($25\%$):

1.  **Token Counter Check:** Count tokens in the conversation queue using a fast tokenizer library (e.g., TikToken).
2.  **Compression Trigger:** If $T_{\text{history}} > T_{\text{max\_allocation}}$:
    *   Extract the oldest $N$ turns (excluding system setups).
    *   Route the turns to a fast model (`Model-B-Utility`) with a summarization prompt.
    *   Append the compiled summary string to the top of the chat logs.
    *   Evict the raw text of the summarized turns.

```python
# Pseudo-implementation of Chat History Compression
def balance_history_context(chat_history, max_tokens, tokenizer):
    if tokenizer.count(chat_history) <= max_tokens:
        return chat_history
        
    # Segment: Keep last 3 turns, compress the older ones
    preserve_turns = chat_history[-3:]
    compress_turns = chat_history[:-3]
    
    summary = model.summarize(compress_turns)
    
    new_history = [
        {"role": "system", "content": f"Previous conversation summary: {summary}"}
    ] + preserve_turns
    
    return new_history
```

### 3.2 RAG Context Scoring & Truncation
When the retrieved document chunks exceed the $35\%$ RAG budget, chunks are discarded in ascending order of their semantic similarity scores:

$$\text{Evict Chunk } c \text{ if } S_{\text{relevance}}(c) < \theta \text{ until } T_{\text{rag\_docs}} \le T_{\text{max\_rag}}$$

---

## 4. Cross-References
*   The system prompt rules governing prompt size are defined in [SYSTEM_PROMPT_CONSTITUTION.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_templates/SYSTEM_PROMPT_CONSTITUTION.md).
*   Retrieval similarity functions for RAG are defined in [RAG_INDEXING_RETRIEVAL_SPEC.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_templates/RAG_INDEXING_RETRIEVAL_SPEC.md).
*   Memory pruning rules for long-term storage are located in [MEMORY_PRUNING_RETRIEVAL_SPEC.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_templates/MEMORY_PRUNING_RETRIEVAL_SPEC.md).
