# Performance Engineering (M177)

**File:** `genesis/performance/__init__.py`
**Tests:** 10

Instruments platform operations with timing, percentiles, and regression detection.

### API
```python
pm = PerformanceMonitor(kernel=kernel, slow_threshold_ms=1000.0)

# Wrap any callable
result = pm.measure("operation", fn, arg1, arg2)

# Or use as decorator
@pm.instrument("my_operation", tags=["critical"])
def do_work(): ...

# Record manually
pm.record("query.latency", 42.5, tags=["search"])

# Summaries and regression detection
summary = pm.summary("operation")["operation"]
# p50_ms, p95_ms, p99_ms, avg_ms, count

regressions = pm.detect_regressions(baseline, threshold_pct=20)
```

### Slow Operation Alerts
When any operation exceeds `slow_threshold_ms`, emits `performance.slow_operation` event.
