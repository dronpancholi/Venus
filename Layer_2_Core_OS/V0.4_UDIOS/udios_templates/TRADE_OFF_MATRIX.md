# Template: Trade-off Matrix

## 1. Document Control
*   **Project Name**: [Project Name]
*   **Decision ID**: DEC-[UUID]
*   **Date Evaluated**: [Date]

---

## 2. Multi-Criteria Decision Analysis (MCDA)
*Assign weight factors (summing to 1.0) and score each option on a scale of 1 to 5.*

| Evaluation Criteria | Weight | Option 1: Postgres | Option 2: DynamoDB | Option 3: SQLite |
|---|---|---|---|---|
| **Latency** | 0.20 | 4 (0.80) | 5 (1.00) | 5 (1.00) |
| **Cost** | 0.30 | 5 (1.50) | 3 (0.90) | 5 (1.50) |
| **Security** | 0.30 | 5 (1.50) | 4 (1.20) | 2 (0.60) |
| **Complexity** | 0.20 | 4 (0.80) | 3 (0.60) | 5 (1.00) |
| **Total Score** | **1.00** | **4.60** (Winner) | **3.70** | **4.10** |

---

## 3. Analysis of the Trade-off Decisions
*Analyze the trade-offs of the recommended option.*

*   **Primary Sacrifice (Postgres)**: By selecting Postgres, we sacrifice the sub-millisecond write speeds of local SQLite database files (compromised Latency for Security/ACID compliance).
*   **Mitigation Strategy**: Implement local memory caching on read routes to bring average request latency below 5ms.
