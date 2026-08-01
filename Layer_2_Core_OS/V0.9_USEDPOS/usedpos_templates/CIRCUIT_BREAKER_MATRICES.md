# Circuit Breaker Matrices
**Document ID:** VENUS-STD-048
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. State Matrix
The circuit breaker wraps external calls to prevent cascading failures:

```
      [State: CLOSED] ───(Failure Rate > 50%)───► [State: OPEN]
             ▲                                         │
             │                                   (Cool-down: 30s)
             │                                         │
             └───────(Success Rate = 100%)─────── [State: HALF-OPEN]
```

## 2. Parameter Matrix
- **Failure Threshold**: $50\%$ error rate over a sliding window of $100$ requests.
- **Cool-down Duration**: $30	ext{ seconds}$ before transitioning to `HALF-OPEN` status.

---

## 3. Reusable Checklist & Exit Criteria
*   [ ] Checked that fallbacks return static mock values or cached payloads.
*   [ ] Verified state changes publish telemetry alerts to monitoring tools.
*   [ ] Confirmed retry limits during half-open states do not overload downstream nodes.
