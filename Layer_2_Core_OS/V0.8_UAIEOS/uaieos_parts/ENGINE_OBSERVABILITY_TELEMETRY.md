# UAIEOS Engine Specification: Observability & Telemetry

This engine specification defines the distributed tracing middleware, metrics exporters, and semantic trace log schemas implemented in the UAIEOS telemetry collector stack.

---

## 1. Observability Pipeline Architecture

The engine hooks into the request-response lifecycle of model execution, translating call details into OpenTelemetry-compliant spans and exporting metrics directly to Grafana / Prometheus instances.

```
       [Execution Scope]
               |
    (Tracer Span Initiated)
               |
               v
     +-------------------+
     |   OTel Collector  | -> (Enriches span with GenAI attributes)
     +-------------------+
               |
        +------+------+
        |             |
        v             v
  [gRPC Trace]   [HTTP Metric]
  (Jaeger/Tempo) (Prometheus)
```

---

## 2. Distributed Tracing Middleware (Python)

The following middleware hooks into async python execution systems to capture latency, token sizes, errors, and metadata context.

```python
import time
import uuid
from typing import Dict, Any, Callable, Awaitable

class TraceSpanContext:
    def __init__(self, trace_id: str, parent_span_id: str = None):
        self.trace_id: str = trace_id
        self.parent_span_id: str = parent_span_id or "0" * 16
        self.span_id: str = uuid.uuid4().hex[:16]

class TelemetryTracingMiddleware:
    def __init__(self, trace_exporter: Callable[[Dict[str, Any]], None]):
        self.trace_exporter = trace_exporter

    async def record_llm_call(
        self,
        model_name: str,
        prompt: str,
        api_call: Callable[[], Awaitable[Dict[str, Any]]],
        span_ctx: TraceSpanContext
    ) -> Dict[str, Any]:
        """Wraps an asynchronous LLM request with telemetry tracing instrumentation."""
        start_time_ns = time.time_ns()
        error_occurred = False
        error_msg = None
        response = {}
        
        try:
            response = await api_call()
            return response
        except Exception as e:
            error_occurred = True
            error_msg = str(e)
            raise e
        finally:
            end_time_ns = time.time_ns()
            duration_ms = (end_time_ns - start_time_ns) / 1_000_000.0
            
            # Formulate OpenTelemetry AI semantic span envelope
            span_record = {
                "trace_id": span_ctx.trace_id,
                "span_id": span_ctx.span_id,
                "parent_span_id": span_ctx.parent_span_id,
                "name": "llm_inference",
                "start_time_unix_nano": start_time_ns,
                "end_time_unix_nano": end_time_ns,
                "attributes": {
                    "gen_ai.system": "gemini",
                    "gen_ai.request.model": model_name,
                    "gen_ai.usage.prompt_tokens": response.get("prompt_tokens", 0),
                    "gen_ai.usage.completion_tokens": response.get("completion_tokens", 0),
                    "gen_ai.usage.total_tokens": response.get("total_tokens", 0),
                    "gen_ai.latency.total_duration_ms": duration_ms,
                    "uaieos.execution.error": error_occurred,
                    "uaieos.execution.error_msg": error_msg
                }
            }
            self.trace_exporter(span_record)
```

---

## 3. Metrics Export Configuration (Prometheus)

The collector registers and exposes metrics to Prometheus scraping scrapers. Below is the configuration structure for scraping and formatting the metrics.

### 3.1 Scraping Target Schema (yaml)
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'uaieos-telemetry-engine'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    params:
      format: ['prometheus']
```

### 3.2 Metric Collector Initialization
```python
from prometheus_client import Counter, Histogram, CollectorRegistry

class PrometheusMetricsCollector:
    def __init__(self, registry: CollectorRegistry):
        self.token_counter = Counter(
            "uaieos_token_consumption_total",
            "Cumulative count of tokens consumed.",
            labelnames=["model", "type"], # type: 'prompt' or 'completion'
            registry=registry
        )
        self.latency_histogram = Histogram(
            "uaieos_llm_latency_seconds",
            "Distribution of execution latencies.",
            labelnames=["model"],
            buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
            registry=registry
        )

    def record_metrics(self, model: str, prompt_tokens: int, completion_tokens: int, duration_sec: float) -> None:
        self.token_counter.labels(model=model, type="prompt").inc(prompt_tokens)
        self.token_counter.labels(model=model, type="completion").inc(completion_tokens)
        self.latency_histogram.labels(model=model).observe(duration_sec)
```

---

## 4. System Cross-References
*   For tracing schema fields and operational metrics, see [PART_12_OBSERVABILITY.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_12_OBSERVABILITY.md).
*   For the cost attributes mapped directly in traces, see [ENGINE_AI_ECONOMICS.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/ENGINE_AI_ECONOMICS.md).
*   For self-healing event triggers extracted from observability pipelines, see [PART_14_AUTONOMOUS_AI_OPERATIONS.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_14_AUTONOMOUS_AI_OPERATIONS.md).
