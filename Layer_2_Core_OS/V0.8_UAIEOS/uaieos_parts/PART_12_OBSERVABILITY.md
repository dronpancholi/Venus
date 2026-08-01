# UAIEOS Part 12: Observability Manual

This manual governs the design, aggregation, and structure of telemetry, logs, metrics, and traces across the UAIEOS lifecycle. It enforces the integration of OpenTelemetry semantic conventions for artificial intelligence workloads.

---

## 1. Tracing Schemas and distributed Context

To trace agentic execution across distributed microservices, model gateways, and external APIs, all transactions must maintain a validated distributed context.

### 1.1 SpanContext Schema
Every execution block (Span) must propagate the following context down the call chain:

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `trace_id` | Hex String (32 char) | Unique identifier for the entire transaction chain. |
| `span_id` | Hex String (16 char) | Unique identifier for the local execution unit. |
| `trace_flags` | Hex String (2 char) | Sampling flags (e.g., `01` for active sampling). |
| `trace_state` | Key-Value Pair | Vendor-specific routing parameters and budget trackers. |

### 1.2 OpenTelemetry AI Semantic Convention Span Schema
```json
{
  "trace_id": "8a0f9b3c4d5e6f7a8b9c0d1e2f3a4b5c",
  "span_id": "1f2e3d4c5b6a7f8e",
  "parent_span_id": "0000000000000000",
  "name": "llm_inference",
  "kind": "SPAN_KIND_INTERNAL",
  "start_time_unix_nano": 1782384366000000000,
  "end_time_unix_nano": 1782384367450000000,
  "attributes": {
    "gen_ai.system": "gemini",
    "gen_ai.request.model": "gemini-1.5-pro",
    "gen_ai.response.model": "gemini-1.5-pro-002",
    "gen_ai.request.temperature": 0.2,
    "gen_ai.request.max_tokens": 2048,
    "gen_ai.usage.prompt_tokens": 1520,
    "gen_ai.usage.completion_tokens": 340,
    "gen_ai.usage.total_tokens": 1860,
    "gen_ai.usage.cached_tokens": 1024,
    "gen_ai.latency.time_to_first_token_ms": 280,
    "gen_ai.latency.total_duration_ms": 1450,
    "gen_ai.cost.usd": 0.00532,
    "uaieos.agent.name": "architect_agent",
    "uaieos.security.guardrails_triggered": false
  }
}
```

---

## 2. Core Operational Metrics

The following metrics are collected continuously and aggregated via Prometheus and OpenTelemetry agents:

### 2.1 Latency Performance Metrics
*   **Time-to-First-Token (TTFT):** Measures the duration between prompt transmission and the arrival of the first output token. Target: $\text{TTFT} < 350\text{ ms}$.
*   **Token Generation Rate:** Tokens generated per second. Formula:
    $$R_{\text{tok}} = \frac{N_{\text{completions}}}{\Delta t_{\text{generation}}}$$

### 2.2 Financial and Resource Metrics
*   **Transaction Token Unit Cost:** Normalized financial spend per transaction.
*   **Total Cost Matrix:** Captures input, output, and cached usage counts to evaluate ROI against budget rules.

---

## 3. Semantic Caching Monitoring

To reduce latency and system overhead, the model gateways employ semantic caching. Telemetry tracks:
*   **Cache Hit Ratio:**
    $$R_{\text{hit}} = \frac{N_{\text{hits}}}{N_{\text{hits}} + N_{\text{misses}}}$$
*   **Semantic Similarity Distributions:** Plots the distribution of cosine similarities for incoming queries relative to cached vectors.

### 3.1 Aggregation Thresholds
The gateway uses semantic distance to group similar traces:

$$\text{Group}(Q_k) \text{ if } \max_{j} \left( \text{Cos}(Q_k, Q_j) \right) \ge 0.92$$

Traces that fall within this clustering threshold are mapped to the same diagnostic partition, enabling aggregate performance debugging.

---

## 4. System Cross-References
*   To implement the telemetry collectors and exporters, see [ENGINE_OBSERVABILITY_TELEMETRY.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/ENGINE_OBSERVABILITY_TELEMETRY.md).
*   For cost-tracking algorithms, see [PART_13_AI_ECONOMICS.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_13_AI_ECONOMICS.md).
*   For evaluation metrics monitored via telemetry, see [PART_11_EVALUATION_BENCHMARKING.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_11_EVALUATION_BENCHMARKING.md).
