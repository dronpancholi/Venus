# Part 08 — Observability

## 1. Observability Design Metrics
Observability models metrics, tracing, logging, and chaos engineering rules to verify active systems health and performance post-deployment.

---

## 2. Telemetry Parameters (The Golden Signals)
Every service must expose metrics tracking the four golden signals:
1.  **Latency**: Time to service a request (split by success and failure).
2.  **Traffic**: Demand volume (e.g. HTTP requests per second).
3.  **Errors**: Rate of requests that fail (e.g. HTTP 500 rate).
4.  **Saturation**: System resource depletion (e.g. thread pool utilization %).

---

## 3. SLA, SLO, & SLI Modeling
We define quantitative targets to measure availability:

\[SLI = \frac{Successful\_Requests\_Under\_Latency\_Threshold}{Total\_Requests}\]

*   **Service Level Indicator (SLI)**: Actual performance measurement.
*   **Service Level Objective (SLO)**: Target reliability goal (e.g. 99.9% of requests have latency < 100ms).
*   **Service Level Agreement (SLA)**: Contractual business commitment with financial penalties.

---

## 4. Observability Checklist
*   [ ] Configured Prometheus endpoints on all workers.
*   [ ] Set up OpenTelemetry (OTel) context propagation across services.
*   [ ] Defined SLI/SLO metrics.
*   [ ] Configured Sentry error boundary captures.
