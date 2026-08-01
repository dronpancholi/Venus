# Stage 6 — AI Research Framework

## 1. Governance & Rationale

### 1.1 Why It Exists
Integrating AI is expensive, introduces non-deterministic outputs, and can lead to security vulnerabilities. Stage 6 provides a structured framework to evaluate LLMs, RAG configurations, agent frameworks, and memory architectures. It ensures AI is deployed only when it is objectively superior to deterministic rules.

### 1.2 What Questions It Answers
*   Should this task be executed by deterministic code or an AI model?
*   Which LLM (frontier vs. open-weight) offers the optimal balance of latency, cost, and accuracy?
*   What memory, RAG, or Model Context Protocol (MCP) architectures are required?
*   How do we evaluate model output drift, safety boundaries, and alignment targets?

### 1.3 What Decisions Depend on It
*   **Model Selection**: Primary and fallback LLM endpoints (e.g., Anthropic Claude vs. Local Llama-3).
*   **Orchestration Architecture**: Decision to use LangChain vs. native SDKs vs. durable Temporal activities for agent coordination.
*   **Inference Compute Model**: Third-party API (SaaS) vs. private dedicated cloud hosting (NVIDIA NIM).

### 1.4 What Happens if It Is Skipped
Skipping Stage 6 results in **AI Over-engineering and Cost Bloat**. The team might use a high-cost frontier model for simple data extraction tasks that could be handled via Regex or Pydantic parsers. Alternatively, they may deploy unvalidated prompts that generate toxic, incorrect, or insecure outputs in production.

### 1.5 What Evidence Is Required Before Proceeding
*   Prompt validation matrix showing accuracy and latency benchmarks under simulated load.
*   Documented fallback mechanism for model downtime or inference rate limits.
*   Safety validation report confirming prompt injection defenses.

---

## 2. Operational Methodology

### 2.1 AI vs. Deterministic Code Decision Tree
Before routing any feature to an AI agent, the team must run it through the following query path:

```
                  Does the task require semantic understanding
                        or natural language output?
                                 │
                     ┌───────────┴───────────┐
                     ▼                       ▼
                    [No]                   [Yes]
                     │                       │
                     ▼                       ▼
            [Deterministic Code]    Can it be solved via Regex,
                                    templates, or SQL filters?
                                             │
                                 ┌───────────┴───────────┐
                                 ▼                       ▼
                                [Yes]                   [No]
                                 │                       │
                                 ▼                       ▼
                        [Deterministic Code]      [AI Model Route]
```

### 2.2 Framework & Architecture Evaluation

#### 2.2.1 Model Selection Criteria
*   *Inference Latency*: Response times under maximum concurrent user requests.
*   *Output Format Enforcement*: Ability to parse structured outputs (JSON/Pydantic) reliably.
*   *Compliance*: Data residency restrictions of the API provider (e.g., zero retention agreements).

#### 2.2.2 Retrieval-Augmented Generation (RAG) & Vector Database Strategy
*   *Embedding model selection*: Latency vs. dimensional size.
*   *Grounding verification*: Anti-hallucination layers verifying LLM outputs against source contexts.

---

## 3. Inputs & Outputs

### 3.1 Inputs
*   Feature Specifications (from Stage 3).
*   API integration parameters.
*   Evaluation test prompts.

### 3.2 Outputs
*   **AI Suitability Blueprint**: Categorized list of features routed to AI vs. deterministic code.
*   **Model Performance Dossier**: Latency, cost, and accuracy benchmarks.
*   **Prompt Security Policy**: Hardened prompts with built-in injection protection.

---

## 4. Reusable Checklists & Templates

### 4.1 AI Integration Checklist
*   [ ] Evaluated and rejected deterministic alternatives for all AI features.
*   [ ] Tested a minimum of 3 candidate models (frontier and open-weights).
*   [ ] Structured and locked all prompt templates in version control.
*   [ ] Configured JSON schema enforcement for all LLM calls.
*   [ ] Set up rate limit handles and fallback endpoints.
*   [ ] Verified data privacy policies (zero data storage/training agreements).

### 4.2 Template: AI Capability Assessment Matrix
```markdown
### 1. Feature: [e.g., Personalized Outreach Generation]
*   **deterministic Alternative**: [e.g., Template system with merge variables]
*   **Why rejected**: [e.g., Templates lack semantic personalization and fail to capture website content relevance]

### 2. Model Benchmarking

| Candidate Model | Cost / 1K Tokens | Latency (P95) | structured JSON Match % |
|---|---|---|---|
| Claude 3.5 Sonnet | $0.0030 | 1.8s | 99.8% |
| GPT-4o-mini | $0.00015 | 0.8s | 98.5% |
| Llama-3-70b (Local) | $0.00080 | 1.2s | 94.2% |

### 3. Safety & Grounding Blueprint
*   *Grounding Method*: [e.g., Cross-check generated text against source HTML keywords using Regex]
*   *Safety Guardrail*: [e.g., If prompt injection string detected, throw 403 error]
```

---

## 5. Scoring & Decision Gates

### 5.1 Scorecard: AI Integrity Index (AII)
Evaluate the AI solution on a 1-5 scale:

| Vector | Scoring Criteria | Score (1-5) |
|---|---|---|
| **Determinism Need** | 1: Critical for system logic. 5: Semantic variation acceptable. | |
| **Output Security** | 1: High prompt injection risk. 5: Zero exposure to critical paths. | |
| **Cost Efficiency** | 1: Prohibitive inference costs. 5: Cost-effective at high scale. | |
| **Inference Speed** | 1: >5s latency (unusable). 5: Sub-second response times. | |

### 5.2 Decision Gate
*   **Exit Criteria**: AII score **≥ 15 / 20**, with no single vector scoring below 3.
*   **Pass**: Proceed to **Stage 7: Economic Research**.
*   **Fail**: Reject AI route and build a deterministic solution.
