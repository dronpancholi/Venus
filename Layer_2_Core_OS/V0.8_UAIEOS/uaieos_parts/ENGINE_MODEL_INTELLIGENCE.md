# UAIEOS Engine: Model Intelligence Engine

This document defines the operational architecture, state models, execution schemas, and dynamic routing algorithms for the Model Intelligence Engine. The engine coordinates foundation model routing and audits execution metrics to satisfy cost, latency, and capability SLAs.

---

## 1. Engine Overview & Core Functions

The Model Intelligence Engine sits between the Core Runtime and the physical model endpoints (both self-hosted clusters and cloud APIs).

```
                      [Inbound Inference Request]
                                   │
                                   ▼
                    [Model Intelligence Engine]
                       ├── Audit & Health Check
                       ├── Dynamic Routing Logic
                       └── KV Cache Matcher
                                   │
            ┌──────────────────────┼──────────────────────┐
            ▼                      ▼                      ▼
    [Self-Hosted Cluster]    [Managed Cloud API]    [Local Small LLM]
```

### 1.1 Core Functions
1.  **Dynamic Routing Decision:** Resolves the optimal endpoint based on current query parameters and token pricing vectors.
2.  **Telemetry Auditing:** Records TTFT, ITL, token counts, and error occurrences per model.
3.  **Active Cache Checking:** Coordinates matching requests to prompt prefix caches to minimize compute redundancy.
4.  **Health Supervision:** Runs continuous health checks on self-hosted instances to handle failovers.

---

## 2. Technical Architecture & Routing Logic

The routing decision represents a multi-variable optimization problem.

### 2.1 The Routing Weight Update Algorithm
The engine maintains a routing matrix representing the selection probability $P(M | T)$ for model $M$ given task type $T$. When performance metrics are updated via evaluation runs, the selection probability is adjusted using a Boltzmann distribution:

$$P(M_i | T) = \frac{\exp(U(M_i, T) / \tau)}{\sum_{j=1}^{M_{\text{total}}} \exp(U(M_j, T) / \tau)}$$

Where:
*   $U(M_i, T)$ is the computed utility score (from [PART_02_MODEL_INTELLIGENCE.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_02_MODEL_INTELLIGENCE.md#L80-L98)).
*   $\tau$ is the routing temperature (parameter regulating exploration vs. exploitation). A low $\tau \to 0$ makes the routing deterministic, selecting the highest-utility model. A high $\tau$ allows exploration to discover performance improvements in alternative models.

---

## 3. Data Protocols & Schemas

### 3.1 Routing Configuration Schema
The engine configuration defines active models, cost profiles, and endpoint addresses.

```json
{
  "engine_name": "model_intelligence_router",
  "routing_temperature": 0.15,
  "active_providers": {
    "self_hosted_llama": {
      "endpoint_uri": "http://10.240.12.80:8000/v1",
      "model_identifier": "meta-llama/Llama-3-70b-instruct",
      "input_token_cost_usd_m": 0.0,
      "output_token_cost_usd_m": 0.0,
      "concurrency_limit": 64,
      "max_context_length": 8192
    },
    "managed_gemini": {
      "endpoint_uri": "https://generativelanguage.googleapis.com/v1beta",
      "model_identifier": "gemini-1.5-flash",
      "input_token_cost_usd_m": 0.075,
      "output_token_cost_usd_m": 0.30,
      "concurrency_limit": 2000,
      "max_context_length": 1048576
    }
  },
  "task_profiles": {
    "code_generation": {
      "target_accuracy": 0.85,
      "max_latency_ms": 3000,
      "weights": { "quality": 0.70, "cost": 0.20, "speed": 0.10 }
    },
    "general_chat": {
      "target_accuracy": 0.65,
      "max_latency_ms": 1500,
      "weights": { "quality": 0.30, "cost": 0.50, "speed": 0.20 }
    }
  }
}
```

### 3.2 Execution Request Event Schema
Every routed transaction is recorded as an execution event:

```json
{
  "transaction_id": "tx-10029-xx",
  "timestamp_utc": "2026-06-26T03:06:06Z",
  "task_type": "code_generation",
  "input_tokens": 1420,
  "allocated_model": "self_hosted_llama",
  "routing_reason": "Data sovereignty restriction + high target quality score.",
  "telemetry": {
    "ttft_ms": 148,
    "itl_ms": 6.8,
    "completed_successfully": true,
    "error_code": null
  }
}
```

---

## 4. Integration & Commands

To audit endpoints or update routing parameters from the administrative console, developers interact with the engine daemon via CLI parameters.

### 4.1 Force Route Check
```bash
python -m uaieos.engines.model_intelligence --action check-route --task code_generation --payload-tokens 400
```
*Expected Output:*
```json
{
  "selected_endpoint": "self_hosted_llama",
  "estimated_cost_usd": 0.00,
  "confidence_score": 0.941
}
```

### 4.2 Endpoint Health Check
```bash
python -m uaieos.engines.model_intelligence --action verify-endpoints --provider self_hosted_llama
```
*Expected Output:*
```json
{
  "status": "HEALTHY",
  "active_concurrency": 12,
  "available_slots": 52,
  "latency_p95_ms": 1150
}
```

---

## 5. System Cross-References
*   For the theoretical model evaluation standards and latency criteria, see [PART_02_MODEL_INTELLIGENCE.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_02_MODEL_INTELLIGENCE.md).
*   For details on token optimization, cache policies, and unit economics calculations, see [PART_13_AI_ECONOMICS.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_13_AI_ECONOMICS.md).
*   For details on evaluation pipeline execution and benchmarking against golden datasets, refer to [PART_11_EVALUATION_BENCHMARKING.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_11_EVALUATION_BENCHMARKING.md).
