# Template: Executive Problem Brief

## 1. Document Control
*   **Project Name**: [Project Name]
*   **Intake ID**: INT-[UUID]
*   **Brief ID**: EXE-[UUID]
*   **Date**: [Date]
*   **Prepared By**: [Name]
*   **Intended Audience**: [C-Suite, VP of Product, Board of Directors]

---

## 2. Executive Summary
*Provide a 3-sentence summary of the validated problem, its business threat, and the recommended intervention strategy.*

---

## 3. The Cost of Doing Nothing
Quantify the operational and financial impact of leaving this problem unsolved:

*   **Financial Loss**: [$0.00 / month due to bad allocations or vendor overcharge]
*   **Operational Delay**: [e.g., 20 engineering hours wasted per week on hotfixes]
*   **User Friction**: [e.g., Customer churn rates at 4.2% due to slow processing]
*   **Risk Profile**: [e.g., Compliance risks, high potential for legal audit failure]

---

## 4. Key Constraints & Strategic Boundaries
Identify the high-level guardrails that must shape any proposed solution:

*   **Financial Ceiling**: [e.g., Solution must cost < $500/mo to run]
*   **Time Criticality**: [e.g., Must resolve before Q4 holiday volume spike]
*   **Regulatory Limits**: [e.g., Must maintain 100% HIPAA and GDPR data isolation]
*   **Technical Boundary**: [e.g., Must integrate directly with existing Salesforce API]

---

## 5. Technology Recommendation & AI Assessment
*Summarize the core recommendations from Module 11 (AI Suitability) and Decision Frameworks.*

*   **Recommended Approach**: [e.g., Build a lightweight caching middleware instead of an LLM agent.]
*   **AI Exposure**: [e.g., None required for initial phase / LLM utilized only for extraction.]
*   **Build vs. Buy Decision**: [e.g., Build internal API router (proprietary code) due to specific security constraints.]

---

## 6. Business Success KPIs
*Define the high-level KPIs that the executive team will use to measure project success.*

| KPI Description | Current Baseline | Target Post-Solution | Measurement Method |
|---|---|---|---|
| **Operational Speed** | [e.g., 4 hours processing] | [< 5 minutes processing] | Database timestamp logs |
| **Gross Margin Impact**| [e.g., 68% gross margin] | [> 85% gross margin] | Financial ledger audits |
| **Outage Frequency** | [e.g., 4 times per month] | [Zero per quarter] | StatusPage alert history |

---

## 7. Problem Readiness Summary
*   **Gateway Score**: [0.00 / 1.00]
*   **Status**: [**BLOCKED** / **APPROVED FOR DEVELOPMENT**]
*   **Next Action Item**: [e.g., Complete stakeholder sign-off on legal constraints.]
