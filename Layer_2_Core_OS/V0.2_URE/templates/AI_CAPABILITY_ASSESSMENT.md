# Template: AI Capability Assessment

## 1. Document Context
*   **Project Name**: [Project Name]
*   **Target Feature**: [e.g., Email Subject Personalization]
*   **Date Compiled**: [Date]

---

## 2. Model Benchmarking Logs

### 2.1 Performance Matrix

| Model | Cost per 1M tokens | Latency (P90) | Output Schema Accuracy |
|---|---|---|---|
| [Model A] | $[Cost] | [Latency] | [Percentage]% |
| [Model B] | $[Cost] | [Latency] | [Percentage]% |
| [Model C] | $[Cost] | [Latency] | [Percentage]% |

### 2.2 Orchestration & RAG Pattern
*   *Grounding Layer*: [e.g., Vector cosine similarity check on Qdrant]
*   *Orchestration framework*: [e.g., Native Python SDK call wrapped inside a Temporal activity]

---

## 3. Security & Safety Evaluation
*   *Prompt Injection Defense*: [Describe the input sanitization filters]
*   *Data Policy Vetting*: [Verify that customer prompts are not saved or used for base model training]

---

## 4. Final Routing Recommendation
*   **Primary Model Route**: [e.g., Claude 3.5 Sonnet]
*   **Fallback Model Route**: [e.g., GPT-4o-mini]
*   **Trigger Condition**: [e.g., If latency > 3.0s or rate limit code 429 received, route to fallback]
