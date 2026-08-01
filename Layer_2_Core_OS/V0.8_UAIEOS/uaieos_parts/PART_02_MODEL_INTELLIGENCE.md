# UAIEOS Part 02: Model Intelligence Manual

This manual establishes the protocols for evaluating foundation models, executing dynamic, multi-factor model routing, comparing self-hosted deployments against API providers, and managing context window constraints. The goal is to maximize performance while minimizing latency and token costs across all enterprise tasks.

---

## 1. Foundation Model Evaluation

UAIEOS mandates a standardized evaluation process for all candidate models prior to production deployment. Models are assessed across multiple dimensions using structured benchmarks and regression suites.

### 1.1 Core Benchmark Suite
*   **MMLU (Massive Multitask Language Understanding):** Evaluates academic and professional-level general knowledge.
*   **HumanEval:** Evaluates coding capabilities and Python code generation accuracy.
*   **MATH:** Assesses multi-step mathematical reasoning and chain-of-thought correctness.
*   **GSM8K:** Measures grade-school word problem-solving.

### 1.2 Quantitative Capability Mapping
The system normalizes benchmark scores into a task competency vector $\vec{C} = [c_{\text{code}}, c_{\text{reason}}, c_{\text{general}}, c_{\text{math}}]$ where each $c_i \in [0, 1]$. This vector is updated continuously using evaluation runs against custom golden datasets.

### 1.3 Latency-Throughput and Calibration Metrics
A model is not evaluated solely on accuracy; it must meet operational SLA bounds:
*   **Time to First Token (TTFT):** Must be $< 200\text{ ms}$ for interactive interfaces.
*   **Inter-Token Latency (ITL):** Throughput must exceed $50\text{ tokens/sec}$ for high-capacity models and $150\text{ tokens/sec}$ for agent routing models.
*   **Expected Calibration Error (ECE):** Assesses if the model's self-reported confidence matches its true accuracy:

$$\text{ECE} = \sum_{m=1}^{M} \frac{|B_m|}{N} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|$$

---

## 2. Dynamic Model Routing

Dynamic routing optimizes execution by matching incoming tasks to the most cost-effective model that satisfies capability and latency constraints.

```
                              [Incoming Payload]
                                       │
                                       ▼
                         [Context Router Classifier]
                                       │
            ┌──────────────────────────┼──────────────────────────┐
            ▼                          ▼                          ▼
      [Lightweight Code]      [Complex Logical Reasoning] [Generic Summarization]
      (ITL > 120 tok/sec,       (TTFT < 800 ms,           (Token Cost < $0.10/M,
       HumanEval > 0.85)         MATH > 0.70)              MMLU > 0.75)
            │                          │                          │
            ▼                          ▼                          ▼
       [Small Model]             [High-Cap Model]           [Medium Model]
```

### 2.1 Router Utility Optimization Function
The router calculates the utility score $U(M, T)$ of model $M$ for task $T$:

$$U(M, T) = w_a \cdot A(M, T) - w_c \cdot \log_{10}(C_{\text{million}}(M)) - w_l \cdot \text{TTFT}(M)$$

Where:
*   $A(M, T) \in [0, 1]$ is the accuracy score of model $M$ on task category $T$.
*   $C_{\text{million}}(M)$ is the cost in USD per million tokens (input + output blended).
*   $\text{TTFT}(M)$ is the Time to First Token in seconds.
*   $w_a, w_c, w_l$ are weights that prioritize quality, cost, or speed respectively.

### 2.2 Fallback Cascades
If the selected model fails (due to timeout, rate limits, or safety blocks), the execution cascades along a pre-configured fallback path:

$$\text{Primary Model} \xrightarrow{\text{500ms Timeout / Rate Limit}} \text{Fallback Model} \xrightarrow{\text{Fail}} \text{High-Capacity API} \xrightarrow{\text{Fail}} \text{Deterministic Error Code}$$

---

## 3. Self-Hosted vs. Managed APIs

UAIEOS maintains a hybrid infrastructure topology. Selecting the deployment model for a task depends on the following characteristics:

| Feature / Metric | Self-Hosted Models (e.g., Llama-3-70B on vLLM/TRT-LLM) | Managed APIs (e.g., Gemini Flash/Pro, Claude Sonnet) |
| :--- | :--- | :--- |
| **Data Sovereignty** | Absolute. Data never leaves the VPC. | High-risk. Dependent on provider data handling agreements. |
| **Latency Profile** | Highly predictable. Bounded by cluster queue capacity. | Variable. Subject to network traffic and provider load. |
| **Scaling Dynamics** | Static scaling based on physical GPU provisioning. | Elastic auto-scaling to meet massive parallel demand. |
| **Cost Profile** | High fixed infrastructure costs; zero marginal cost per token. | Zero fixed costs; variable linear pricing per token. |
| **Customization** | Full weight adjustment, fine-tuning, LoRA adapters. | Prompt engineering and system prompt constitutions only. |

### 3.1 Routing Split Policy
*   **Privacy-Restricted Tasks:** Must route to Self-Hosted Models.
*   **Elastic Workloads (Massive Parallel Processing):** Route to Managed APIs.
*   **Fine-tuned Specific Tasks:** Route to Self-Hosted LoRA deployments.

---

## 4. Context Window Optimization

As context windows extend (e.g., $128\text{k}$ to $2\text{M}$ tokens), management of token utilization is critical to prevent cost overruns and context retrieval degradation (the "Lost in the Middle" phenomenon).

### 4.1 Context Density Metrics
We define Context Density ($\rho_C$) as the ratio of retrieval accuracy inside the context window to the length of the window:

$$\rho_C(L) = \frac{\text{Recall}(L, i)}{L}$$

Where $\text{Recall}(L, i)$ represents the probability of retrieving a key piece of information located at relative index $i$ inside a context of total length $L$.
*   **Lost in the Middle Mitigation:** If $\rho_C(L)$ falls below a threshold ($0.80$), UAIEOS splits the context using Hierarchical Chunking or forces a Map-Reduce compilation phase.

### 4.2 Prefix Caching and Sizing
To minimize latency and cost, prompts are structured to maximize prefix caching. System prompts and schemas must remain static at the beginning of the context window. Changing system parameters on a per-query basis invalidates the KV cache, increasing latency by up to $10\text{x}$.

---

## 5. System Cross-References
*   For the operational code that executes the model routing, see [ENGINE_MODEL_INTELLIGENCE.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/ENGINE_MODEL_INTELLIGENCE.md).
*   For token cost optimization strategies and caching models, refer to [PART_13_AI_ECONOMICS.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_13_AI_ECONOMICS.md).
*   For prompt architecture and system prompt design, refer to [PART_07_CONTEXT_ENGINEERING.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_07_CONTEXT_ENGINEERING.md).
