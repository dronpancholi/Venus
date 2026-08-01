# Part 06 — Infrastructure

## 1. Cloud & Computing Topologies
Infrastructure models resource configurations (Compute, CDN, Autoscaling, Kubernetes, GPU, Edge) across Cloud, Hybrid, and On-Premises environments.

---

## 2. Infrastructure Patterns Matrix

| Topology | Strengths | Weaknesses | Best For |
|---|---|---|---|
| **Cloud (Serverless)**| Instant scale, pay-per-use | Cold start latency, cost spikes | Early V1 releases |
| **Containers (K8s)** | Custom configuration, scaling | Setup overhead, resource waste | Large-scale platforms |
| **Edge Compute** | Zero routing latency, localized | Zero disk access, limited memory | CDN routers, cache |
| **GPU / On-Prem** | Low training costs, control | High initial hardware setup fees | LLM hosting / Science |

---

## 3. Auto-scaling Logic
Proposals must define dynamic auto-scaling rules based on CPU and memory thresholds:

```
[System Load Spikes] ──► [Sustained CPU > 75% for 3 mins] ──► [Deploy 2 New Nodes]
                                                                     │
                                                                     ▼
                                                        [Trigger Gateway Re-routing]
```

### 3.1 Cold Start Mitigation
*   *Strategy*: Keep warm instances active during peak operational windows.
*   *Target limits*: Max cold start latency under 500ms.

---

## 4. Infrastructure Checklist
*   [ ] Selected environment profile (Cloud vs. Edge vs. K8s).
*   [ ] Defined auto-scaling triggers.
*   [ ] Documented CPU and memory constraints.
*   [ ] Verified GPU allocations for AI workloads.
