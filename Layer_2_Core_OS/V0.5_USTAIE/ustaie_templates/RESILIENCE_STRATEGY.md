# Template: Resilience Strategy

## 1. Document Control
*   **Project Name**: [Project Name]
*   **Resilience ID**: RES-[UUID]

---

## 2. Fault Tolerance Strategy
*Describe the mechanisms used to ensure system resilience under failure (Circuit Breakers, Bulkheads, Retries).*

*   **Circuit Breaker Strategy**:
    *   *Target Service*: Third-party indexing API.
    *   *Trigger*: Trip breaker if request fail rate > 10% in 1 minute.
    *   *Fallback*: Serve stale cached pages from Redis.
*   **Bulkhead Pattern**:
    *   *Implementation*: Allocate isolated thread pools for billing flows and outreach crawler flows to prevent crawler delays from blocking customer checkouts.

---

## 3. Retries & Backoff Policies
*   **Default HTTP Retry Policy**: Enforced max 3 attempts.
*   **Backoff Algorithm**: Exponential backoff with jitter.
    \[Delay = Base \times 2^{Attempt} + Jitter\]
*   **Validation Command**: `npm run test:resilience-simulation`
