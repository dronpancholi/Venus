# Engine: Capacity Planner

## 1. Context & Strategy

### 1.1 Purpose
The Capacity Planner Engine calculates CPU, memory, database IOPS, storage footprint, and network bandwidth allocations required to support target transactional workloads. It models scale profiles based on current metrics to prevent over-provisioning cost spikes or under-provisioning outages.

### 1.2 Philosophy
Capacity planning must be deterministic and automated. We size system resources using engineering scaling equations rather than guessing configurations.

---

## 2. Ingest Parameters & Taxonomy

### 2.1 Inputs & Outputs
*   **Inputs**: Target requests per second ($RPS$), latency profiles ($T_{response}$), transaction data payload sizes, historical metric logs, and target resource margins.
*   **Outputs**: System Sizing Document containing recommended CPU cores, RAM gigabytes, disk IOPS limits, and network throughput thresholds.

### 2.2 Sizing Pipeline
```
[Ingest RPS & Latency Metrics] ──► [Compute CPU & RAM Demands] ──► [Determine Disk IOPS Limits] ──► [Generate Terraform Resource Spec]
```

---

## 3. Algorithmic Checks & Computations

### 3.1 Compute Sizing Model
The engine determines CPU cores ($C_{req}$) and Memory ($M_{req}$) requirements based on target processing constraints:

$$C_{req} = \left( \frac{RPS \times T_{cpu\_ms}}{1000} \right) \times (1 + B_{margin})$$

$$M_{req} = \Big( (RPS \times T_{active\_sec}) \times S_{payload\_kb} \Big) + M_{base}$$

Where:
*   $T_{cpu\_ms}$: Average CPU processing time per request (e.g., $15\text{ms}$).
*   $B_{margin}$: Resource headroom buffer to absorb spikes (typically $0.5$ or $50\%$).
*   $T_{active\_sec}$: Average transaction lifecycle duration in memory.
*   $S_{payload\_kb}$: Size of the transaction memory payload.
*   $M_{base}$: Base memory consumption of the system runtime.

For $RPS = 2000$, $T_{cpu\_ms} = 20\text{ms}$, and $B_{margin} = 0.5$:
$$C_{req} = \left( \frac{2000 \times 20}{1000} \right) \times 1.5 = 40 \times 1.5 = 60\text{ cores}$$

### 3.2 Disk IOPS Estimation
Database IOPS requirements ($I_{req}$) are calculated as:

$$I_{req} = (RPS_{write} \times P_{write}) + (RPS_{read} \times P_{read})$$

Where $P$ is the database page access factor.

---

## 4. Reusable Checklist & Exit Criteria
*   [ ] Checked that ingress request profiles match target production SLA forecasts.
*   [ ] Confirmed CPU buffer variables account for multi-thread scheduler latency.
*   [ ] Verified database write patterns reflect real-world page sizes and index updates.
*   [ ] Checked that network egress bandwidth predictions remain below regional link capacity limiters.
*   *Exit Criteria*: Sizing reports match target deployment models within $\pm 10\%$ confidence intervals.
