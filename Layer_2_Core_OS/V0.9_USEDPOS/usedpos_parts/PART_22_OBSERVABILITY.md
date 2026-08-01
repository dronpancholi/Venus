# Part 22: Observability

## 1. Context & Strategy
Observability under Project Venus establishes the foundational framework for measuring system reliability, detecting regressions, and debugging complex distributed environments. Systems must generate telemetry data natively according to the OpenTelemetry (OTel) standard, enabling unified querying and correlation across metrics, logs, and distributed traces.

---

## 2. Reliability Mathematics & SLO Models

### 2.1 System Availability Formula
System availability ($A$) is calculated as a function of Mean Time Between Failures ($\text{MTBF}$) and Mean Time To Repair ($\text{MTTR}$):

$$A = \frac{\text{MTBF}}{\text{MTBF} + \text{MTTR}}$$

To achieve "four nines" ($99.99\%$) availability:
*   If $\text{MTBF} = 30\text{ days}$ ($43,200\text{ minutes}$), the maximum acceptable $\text{MTTR}$ is:
    $$0.9999 = \frac{43200}{43200 + \text{MTTR}} \implies \text{MTTR} \approx 4.32\text{ minutes}$$

### 2.2 Error Budget Depletion Rate
The depletion rate ($DR$) of the error budget over a measurement window ($W$) determines paging urgency:

$$DR = \frac{\text{Error Rate}}{\text{Allowed Error Rate}}$$

If the allowed error rate is $0.1\%$ ($99.9\%$ SLO) and the current error rate is $2\%$ over $1\text{ hour}$, the budget burn rate is $20\text{x}$, depleting the entire monthly budget in:

$$\text{Time to Depletion} = \frac{720\text{ hours}}{20} = 36\text{ hours}$$

---

## 3. Telemetry Integration Standards

### 3.1 OpenTelemetry Collector Configuration
All nodes must deploy an OTel Collector daemon set to ingest, process, and export metrics, traces, and logs.

```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318
  prometheus:
    config:
      scrape_configs:
        - job_name: 'kubernetes-service-endpoints'
          kubernetes_sd_configs:
            - role: endpoints

processors:
  batch:
    timeout: 1s
    send_batch_size: 256
  memory_limiter:
    check_interval: 1s
    limit_percentage: 75
    spike_limit_percentage: 15

exporters:
  prometheus:
    endpoint: 0.0.0.0:8889
  otlp/jaeger:
    endpoint: "jaeger-collector.observability.svc.cluster.local:4317"
    tls:
      insecure: true

service:
  pipelines:
    metrics:
      receivers: [otlp, prometheus]
      processors: [memory_limiter, batch]
      exporters: [prometheus]
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [otlp/jaeger]
```

### 3.2 Prometheus Alerting Rules
Prometheus alerts must trigger on error budget burn rate breaches:

```yaml
# alerts-slos.yaml
groups:
  - name: venus-slos
    rules:
      - alert: ErrorBudgetBurnRateHigh
        expr: |
          (
            sum(rate(http_requests_total{status=~"5.."}[1h])) 
            / 
            sum(rate(http_requests_total[1h]))
          ) > 0.02
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error budget burn rate detected on {{ $labels.service }}"
          description: "Burn rate is currently above 2%, threatening the 99.9% SLO."
```

---

## 4. Reusable Checklist & Exit Criteria
*   [ ] Checked that all microservice frameworks include OTel middleware.
*   [ ] Ensured trace context (`traceparent` header) propagation across all HTTP and gRPC network edges.
*   [ ] Configured SLIs for latency (p95/p99) and success rates on all public APIs.
*   [ ] Set up alert routing rules targeting pager channels for critical budget depletion.
*   [ ] Verified log outputs conform to structured JSON format containing trace IDs.
