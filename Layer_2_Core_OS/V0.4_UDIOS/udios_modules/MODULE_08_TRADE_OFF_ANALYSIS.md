# Module 08 — Trade-off Analysis Engine

## 1. Context & Strategy

### 1.1 Purpose
The Trade-off Analysis Engine evaluates generated alternative options against the system constraints. It forces an objective comparison across key vectors like Latency, Cost, Security, Complexity, and Maintainability.

### 1.2 Philosophy
There are no solutions, only trade-offs. Swapping a database engine to reduce license fees (Financial) will alter execution performance (Technical) or increase deployment complexity (Operational). Every trade-off must be modeled.

---

## 2. Ingest Parameters & Taxonomy

### 2.1 Inputs & Outputs
*   **Inputs**: Expanded Alternative Vectors Directory (from Module 07) and active Project Constraints (from V0.3 Module 7).
*   **Outputs**: Multi-criteria Trade-off Analysis Matrix.

### 2.2 Core Comparison Vectors
1.  **Latency**: Average query/request execution window.
2.  **Cost**: Compute infrastructure spend and software licensing.
3.  **Maintainability**: Code footprint, backup frequency, cluster setup overhead.
4.  **Security**: RLS support, encryption protocols, patch cadence.
5.  **Hiring**: Team familiarity, recruiting cost/availability of skills.
6.  **Complexity**: Deployment footprint, dependency tree depth.
7.  **Vendor Lock**: Reversibility costs, proprietary APIs.
8.  **Scalability**: Multi-node replication ease, connection pools limit.

---

## 3. Operational Algorithm & Scoring

### 3.1 Weighted Matrix Model
The suitability of each option \(S_j\) is calculated using a weighted score:

\[S_j = \sum_{i=1}^{8} (Score_{ji} \times Weight_i)\]

Where:
*   \(Score_{ji}\): Score of option \(j\) on vector \(i\) (1: Poor, 5: Excellent).
*   \(Weight_i\): Weighted multiplier of importance of vector \(i\) (sum of weights = 1.0).

### 3.2 Trade-off Tree Logic
```
                    [Run Weighted Matrix Model]
                                 │
                   [Does Winner Breach Constraints?]
                     ├── YES ──► [Reject Winner; Re-evaluate Options]
                     └── NO  ──► [Mark as Recommended Option]
```

---

## 4. Reusable Templates & Checklists

### 4.1 Template: Multi-Criteria Decision Matrix
```markdown
### 1. Trade-off Matrix
*   **Decision ID**: DEC-[UUID]

| Option Name | Latency (x0.2) | Cost (x0.3) | Security (x0.3) | Complexity (x0.2) | Total Score |
|---|---|---|---|---|---|
| PostgreSQL | 4 (0.8) | 5 (1.5) | 5 (1.5) | 4 (0.8) | **4.6** |
| DynamoDB | 5 (1.0) | 3 (0.9) | 4 (1.2) | 3 (0.6) | **3.7** |
```

### 4.2 Checklist
*   [ ] Checked database and network limits.
*   [ ] Evaluated setup latency overhead.
*   [ ] Assigned correct weights.
*   [ ] Checked options for constraint breaches.

---

## 5. SRE, AI-Agent, & Safety Parameters

### 5.1 AI-Agent Execution Instructions
1.  **Map**: Retrieve weights from active project registers.
2.  **Calculate**: Solve the weighted equation. If any option scores < 2.0 on a critical parameter (Security/Cost), automatically drop it from the pool.

### 5.2 Common Anti-patterns
*   *The Fixed Weight Scam*: Manipulating weights after calculation to force the preferred option to score highest.

### 5.3 Exit Criteria
*   Weighted Trade-off Analysis Matrix generated and **winner selected**.
*   Proceed to **Module 09: Build vs. Buy**.
