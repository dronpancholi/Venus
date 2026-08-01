# Template: Observability Plan

## 1. Document Control
*   **Project Name**: [Project Name]
*   **Plan ID**: OBS-[UUID]

---

## 2. SLI/SLO Target Parameters
*Define target metrics to track availability and operational quality.*

*   **Availability SLO**: 99.9% of user requests return HTTP 200/201 within 30-day windows.
*   *Latency SLO*: 95% of user database queries return in <= 50ms.
*   *Error SLO*: Error HTTP 5xx rate remains < 0.1% of daily request volume.

---

## 3. Alerts & Notification Channels

| Severity Class | Trigger Condition | Notification Target | SLA to Acknowledge |
|---|---|---|---|
| **P1 - Critical** | Gateway HTTP 5xx rate > 1.0% in 5 mins | PagerDuty / On-call SRE | 15 minutes |
| **P2 - High** | Worker queue backlog > 10,000 tasks | Slack SRE channel | 1 hour |
| **P3 - Medium** | Disk space capacity reaches 80% | Email Notification | 24 hours |

---

## 4. Distributed Tracing Schema
*   **Trace Context Propagator**: W3C Trace Context headers (`traceparent`, `tracestate`).
*   **Collector Agent**: OpenTelemetry collector routing metrics to Datadog / self-hosted Prometheus.
