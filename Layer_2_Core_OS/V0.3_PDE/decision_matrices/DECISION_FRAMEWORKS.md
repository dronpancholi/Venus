# Project VENUS — Decision Frameworks Dossier

## 1. Rationale & Governance

This dossier contains the institutional decision frameworks used to validate projects, select technologies, and evaluate build-versus-buy trade-offs. No decision may be logged in the project's history without executing the respective matrix below.

---

## 2. Decision Matrices

### 2.1 Matrix 1: Is the Problem Worth Solving?
Evaluate the problem's market urgency and economic value:

| Vector | 1 (Low) | 3 (Medium) | 5 (High) |
|---|---|---|---|
| **Willingness to Pay** | User expects it for free. | Will pay standard SaaS fees. | Urgent budget allocated. |
| **Alternative Friction**| Simple spreadsheets work. | Fragmented tools are used. | No viable workarounds exist. |
| **Pain Recurrence** | Monthly/Yearly. | Weekly. | Daily / Hourly. |
| **Compliance Mandate**| No compliance value. | Enhances operations. | legally required to operate. |

*   **Exit Threshold**: Total Score **≥ 12 / 20** required to proceed.

---

### 2.2 Matrix 2: Should Software Be Built? (Build vs. Buy)
Determine whether to write proprietary code or purchase existing tools:

| Evaluation Vector | Buy Existing SaaS | Build Custom Code |
|---|---|---|
| **Core Competency** | Low strategic differentiator. | Core moat and product IP. |
| **Time to Market** | Immediate deployment. | 6–18 months development. |
| **Total Cost of Ownership**| Fixed subscription pricing. | Ongoing maintenance & engineering. |
| **Customization Need** | Standard configurations work. | Unique workflow integration required. |
| **Ecosystem Safety** | Dependent on vendor roadmap. | Fully controlled internal asset. |

*   **Decision Rule**: Build only if **Core Competency = Custom** and **Customization Need = Custom**. Otherwise, Buy/Integrate.

---

### 2.3 Matrix 3: Should AI Be Involved?
Evaluate LLM/ML suitability:

| Vector | 1 (Low) | 3 (Medium) | 5 (High) |
|---|---|---|---|
| **Semantic Complexity** | Standard SQL/Regex works. | Context-aware parsing needed. | Generative output required. |
| **Error Tolerance** | Zero tolerance (Financial/Auth). | Minor drift acceptable. | Subjective human validation. |
| **Cost Ceiling** | Cost must be < $0.0001/txn. | Cost < $0.05/txn. | High value per query. |

*   **Decision Rule**: Deploy AI only if **Semantic Complexity ≥ 3** and **Error Tolerance ≥ 3** and **Cost Ceiling ≥ 3**. Otherwise, use deterministic code.

---

### 2.4 Matrix 4: Should Open Source Be Adopted?
Evaluate candidate libraries:

| Vector | Adopt Open Source | Build/Buy Proprietary |
|---|---|---|
| **Licensing** | Permissive (MIT, Apache 2.0). | SSPL / AGPL (SaaS copyleft risks). |
| **Security Maturity** | Public CVE checks active. | Hidden, un-audited codebase. |
| **Ecosystem Support** | High GitHub stars, frequent commits.| Inactive/abandoned library. |
| **Control Requirement**| Standard package sufficient. | Requires custom kernel/DB changes. |

*   **Decision Rule**: Adopt Open Source only if **Licensing = Permissive** and **Ecosystem Support = High**.
