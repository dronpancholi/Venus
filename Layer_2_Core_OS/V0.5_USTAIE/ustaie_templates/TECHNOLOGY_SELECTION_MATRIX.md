# Template: Technology Selection Matrix

## 1. Document Control
*   **Project Name**: [Project Name]
*   **Decision ID**: DEC-[UUID]

---

## 2. Technology Comparison Matrix

| Technology Profile | Primary Strength | Primary Weakness | License Safety | Selected |
|---|---|---|---|---|
| **[Tech A, e.g., Postgres]** | Relational integrity, JSONB | Scale sharding complexity | Permissive | **YES** |
| **[Tech B, e.g., MongoDB]** | Schema flexibility | Weak joins, query latency | Restrictive (SSPL) | **NO** |
| **[Tech C, e.g., DynamoDB]** | Auto-scaling latency | Proprietary cloud locks | Proprietary | **NO** |

---

## 3. Selection Rationale & Trade-offs
*Detail the selection rationale and trade-offs.*

*   **Selected Option**: [Tech Name]
*   **Justification**: [Describe why the chosen option is the best fit]
*   **Mitigation Strategy for Disadvantages**: [e.g., Cache reads locally to mitigate query latency limits]
