# Engine: AI Architecture

## 1. Context & Strategy

### 1.1 Purpose
The AI Architecture Engine profiles tasks to design the optimal AI system pattern, preventing over-engineering and minimizing execution cost.

### 1.2 Philosophy
Do not throw a model at every problem. We justify LLM deployments only when static heuristics fail, and multi-agent coordination only when single-agent tool loops saturate.

---

## 2. Decision Logic Matrix

| Task Characteristics | Recommendation | Selected Profile |
|---|---|---|
| Rigid schema, static inputs | **No AI / Heuristics** | Regex, SQL, static code rules |
| High text variety, single task | **Single LLM** | Prompt templates, JSON parsing |
| Multi-step research, tool loops | **Single Agent** | ReAct planning loops, tool calling |
| Diverse parallel workloads | **Multi-Agent Swarm** | Coordinator + specialized worker agents |

---

## 3. Topologies & Routing Decisions

### 3.1 LLM Routing Flow
```
                          [Inbound AI Task]
                                  │
                      [Determinism Requirement]
                        ├── High ──► [Local Model / Code Rules]
                        └── Low  ──► [Context Window Check]
                                           ├── < 4K tokens ──► [Gemini Flash]
                                           └── > 32K tokens ──► [Gemini Pro / RAG]
```

### 3.2 Fine-Tuning vs. RAG
*   **RAG**: Enforced when dynamic, updating knowledge database data is required.
*   **Fine-Tuning**: Enforced when style, specific syntax formats, or low-cost small models are target requirements.

---

## 4. AI Architecture Checklist
*   [ ] Checked target task against suitability metrics.
*   [ ] Checked context window bounds.
*   [ ] Audited token budget costs at 10x scale.
*   [ ] Configured RAG caching layers.
