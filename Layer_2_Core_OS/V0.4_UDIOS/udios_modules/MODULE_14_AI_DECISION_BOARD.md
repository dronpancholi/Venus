# Module 14 — AI Decision Board

## 1. Context & Strategy

### 1.1 Purpose
The AI Decision Board determines objectively if an AI-based system (LLMs, agents, fine-tuning) is required for a component, or if traditional heuristics and databases are more appropriate.

### 1.2 Philosophy
AI is not a default solution. It introduces non-deterministic outputs, latency spikes, and cost escalations. We justify AI deployment only when rules-based systems cannot solve the problem.

---

## 2. Ingest Parameters & Taxonomy

### 2.1 Inputs & Outputs
*   **Inputs**: DIR and target task description.
*   **Outputs**: AI Suitability Scorecard and recommended technology profiles.

### 2.2 Technology Profiles
*   **Workflow**: Temporal / Airflow orchestrations.
*   **RAG (Retrieval-Augmented Generation)**: Dynamic contextual search.
*   **MCP (Model Context Protocol)**: Model interaction tool integrations.
*   **Fine-tuning**: Domain-specific styling.
*   **Local**: Ollama / Llama.cpp self-hosted execution.
*   **Cloud**: Gemini / OpenAI vendor APIs.
*   **Hybrid**: Combined routing pipelines.

---

## 3. Operational Algorithm & Decision Tree

### 3.1 AI Suitability Matrix
The engine scores suitability across four indicators:
*   *Determinism Required (1-5)*: 1: Creative tasks (hallucination okay). 5: Exact numbers/database queries (must be 100% correct).
*   *Variety / Unstructured Data (1-5)*: 1: Clean CSV schema. 5: Raw, noisy email text.
*   *Latency Bound (1-5)*: 1: Hours to complete. 5: Web UI response (<100ms).

### 3.2 Decision Tree logic
```
                          [Evaluate Suitability]
                                    │
                     [Is Determinism Score = 5?]
                     ├── YES ──► [Select: Simple Automation / Heuristics]
                     └── NO  ──► [Check Variety / Unstructured Data Score]
                                       ├── Score >= 4 ──► [Select: LLM / RAG]
                                       └── Score < 4  ──► [Select: Traditional ML]
```

---

## 4. Reusable Templates & Checklists

### 4.1 Template: AI Suitability Record
```markdown
### 1. Suitability Profile
*   **Decision ID**: DEC-[UUID]
*   **Selected Profile**: RAG + Cloud LLM (Gemini-1.5-Pro)
*   **Justification**: Task involves parsing noisy customer emails; semantic search is required.
*   *Estimated Monthly Token Spend*: $[Cost]
```

### 4.2 Checklist
*   [ ] Checked target task for determinism limits.
*   [ ] Checked average token payload sizes.
*   [ ] Audited model latency profiles.
*   [ ] Evaluated local self-hosted models to reduce vendor costs.

---

## 5. SRE, AI-Agent, & Safety Parameters

### 5.1 AI-Agent Execution Instructions
1.  **Parse**: Read inputs to identify if task is mathematical or database routing.
2.  **Flag**: If proposer selects a cloud LLM for simple data extraction without evaluating regex or local alternatives, block intake.

### 5.2 Common Anti-patterns
*   *The LLM Calculator*: Deploying a massive LLM agent to extract dates or perform sums, increasing latency and cost.

### 5.3 Exit Criteria
*   AI Suitability Scorecard completed and **approved model type selected**.
*   Proceed to **Module 15: Economic Decision Engine**.
