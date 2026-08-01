# Observability Grafana Dashboard Specification
**Document ID:** VENUS-STD-098
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Overview
This specification details the standardized metrics schema and panel structures for monitoring Project Venus components in Grafana.

## 2. Grafana Dashboard Config Layout Schema
Every service dashboard must follow a four-tier panel grid:
*   **Tier 1: Request Rate (RPS)** - Incoming requests per second.
*   **Tier 2: Error Rates** - HTTP 5xx error percentages.
*   **Tier 3: Latencies** - p95 and p99 server response latencies.
*   **Tier 4: Resource Utilization** - Kubernetes Pod CPU, memory usage, and Database active connections pool.

## 3. Prometheus Metric Source Reference

### 3.1 HTTP Latency Query (p95)
```promql
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{app="venus-core-service"}[5m])) by (le))
```

### 3.2 Error Rate Query
```promql
sum(rate(http_requests_total{app="venus-core-service", status=~"5.."}[5m])) 
/ 
sum(rate(http_requests_total{app="venus-core-service"}[5m])) * 100
```

### 3.3 Database Active Connections Query
```promql
pg_stat_database_numbackends{datname="venus_prod"}
```

## 4. Dashboard JSON Model Outline
```json
{
  "annotations": { "list": [] },
  "editable": true,
  "fiscalYearStartMonth": 0,
  "graphTooltip": 0,
  "id": 109,
  "links": [],
  "liveNow": false,
  "panels": [
    {
      "collapsed": false,
      "gridPos": { "h": 8, "w": 12, "x": 0, "y": 0 },
      "id": 1,
      "title": "Application Request Throughput (RPS)",
      "type": "timeseries",
      "targets": [
        {
          "datasource": { "type": "prometheus", "uid": "prometheus-prod" },
          "editorMode": "code",
          "expr": "sum(rate(http_requests_total{app=\"venus-core-service\"}[5m]))",
          "legendFormat": "Requests per Second"
        }
      ]
    }
  ],
  "refresh": "10s",
  "schemaVersion": 38,
  "style": "dark",
  "tags": ["venus", "production"],
  "time": { "from": "now-1h", "to": "now" },
  "title": "Venus Core Service Observability Dashboard",
  "version": 1
}
```

## 5. Cross-References
- [SLO SLI Prospectus](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/SLO_SLI_PROSPECTUS.md)
