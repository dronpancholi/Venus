# Part 01 — Systems Thinking

## 1. First Principles Analysis
Systems thinking models software as a collection of feedback loops rather than static code modules. Every subsystem change is analyzed to identify emergence, nonlinear behaviors, and secondary/third-order effects.

---

## 2. Dynamic Systems Modeling & Loops

### 2.1 Feedback Loops (Reinforcing vs. Balancing)
*   **Reinforcing Loops (R)**: Accelerate change, leading to exponential growth or runaway failure (e.g., retry storms on database latency).
*   **Balancing Loops (B)**: Stabilize systems, pushing them back toward equilibrium (e.g., rate limiters capping inbound queue sizes).

```
[Inbound Load] ──(+)──► [Queue Size] ──(+)──► [Rate Limiter Trigger]
      ▲                                                  │
      │                                                 (-)
      └──────────────────────────────────────────────────┘
                 (B1: Queue Stabilization Loop)
```

### 2.2 Leverage Points
Identify high-yield intervention coordinates. For example, rather than scaling database instances (high cost), implementing a token-bucket rate limiter at the gateway represents a high-leverage stabilizing change.

---

## 3. Order Effects & Emergence

### 3.1 Second & Third Order Effects
*   **First Order**: Implement local in-memory cache to reduce database load.
*   **Second Order**: App worker memory footprint increases, triggering worker recycling during traffic spikes.
*   **Third Order**: Client requests drop during container restarts, resulting in transaction loss.

### 3.2 Emergence Dynamics
Identify behaviors that arise only when subsystems interact. For instance, when three microservices use independent auto-scaling policies, their concurrency limits can synchronize to saturate a shared database cluster.

---

## 4. Systems Thinking Checklist
*   [ ] Mapped all reinforcing loops in transaction paths.
*   [ ] Identified rate-limiting balancing points.
*   [ ] Outlined second-order and third-order effects of cache eviction rules.
*   [ ] Documented system leverage points.
