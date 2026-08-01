# Module 09 — Build vs. Buy Engine

## 1. Context & Strategy

### 1.1 Purpose
The Build vs. Buy Engine provides a mathematical framework for deciding whether to write custom software in-house or purchase a commercial vendor license.

### 1.2 Philosophy
Custom code is a permanent liability. Unless a feature represents the core business IP or a primary competitive differentiator, we prioritize buying a mature third-party service over writing and maintaining custom implementations.

---

## 2. Ingest Parameters & Taxonomy

### 2.1 Inputs & Outputs
*   **Inputs**: DIR, developer cost estimates, SaaS pricing sheets.
*   **Outputs**: Build vs. Buy Report with 3-year Total Cost of Ownership (TCO).

### 2.2 Financial Parameters
*   **Developer Cost**: Cost per hour of engineering (fully loaded rate, e.g., $100/hr).
*   **Build Cost**: Engineering hours to V1 + ongoing maintenance (assumed 20% of build cost annually).
*   **Buy Cost**: Setup fee + annual subscription cost.

---

## 3. Operational Algorithm & Decision Tree

### 3.1 Total Cost of Ownership (TCO) Calculation
The engine compares costs over a 36-month horizon:

\[TCO_{Build} = Build\_Hours \times Hourly\_Rate + (Maintenance\_Hours \times Hourly\_Rate \times 3)\]

\[TCO_{Buy} = Setup\_Fee + (Monthly\_SaaS\_Cost \times 36)\]

### 3.2 Decision Tree logic
```
                          [TCO Comparison]
                                 │
                   [Is it Core Proprietary IP?]
                     ├── YES ──► [Build (Proprietary Advantage)]
                     └── NO  ──► [Select Option with Lower TCO]
```

---

## 4. Reusable Templates & Checklists

### 4.1 Template: Build vs. Buy Analysis
```markdown
### 1. Financial Overview
*   **Decision ID**: DEC-[UUID]
*   *TCO Build*: $[TCO_Build]
*   *TCO Buy*: $[TCO_Buy]
*   **Verdict**: **BUY** (TCO savings of $12,400 over 3 years)

### 2. Core IP Validation
*   *Is this system a competitive differentiator?* [Yes / No]
```

### 4.2 Checklist
*   [ ] Calculated fully loaded developer rates.
*   [ ] Checked SaaS limits and contract terms.
*   [ ] Estimated ongoing maintenance hours.
*   [ ] Verified core IP status.

---

## 5. SRE, AI-Agent, & Safety Parameters

### 5.1 AI-Agent Execution Instructions
1.  **Parse**: Read vendor pricing API or tables.
2.  **Calculate**: Solve TCO comparison. If TCO Buy < TCO Build and Core IP is false, recommend Buy.

### 5.2 Common Anti-patterns
*   *Not-Invented-Here (NIH) Syndrome*: Engineers building custom queue routers because they "prefer writing custom sockets" over using RabbitMQ or SQS.

### 5.3 Exit Criteria
*   Build vs. Buy analysis completed and **TCO models validated**.
*   Proceed to **Module 10: Open Source Evaluation**.
