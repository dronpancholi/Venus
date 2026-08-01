# Template: Stakeholder Analysis

## 1. Meta Control
*   **Project Name**: [Project Name]
*   **Intake ID**: INT-[UUID]
*   **Analysis Date**: [Date]
*   **Lead Researcher**: [Name]

---

## 2. Stakeholder Profiles & Incentives Matrix

| Stakeholder Role | Incentives | Fears | Objectives | Primary KPIs | Key Constraints |
|---|---|---|---|---|---|
| **Founder / Executive** | [e.g., Growth, Valuation, Market Moat] | [e.g., Competitor first-mover, Cash burn] | [e.g., Launch V1 within Q3] | [e.g., ARR, User Activation] | [e.g., Hard hiring limit of 5 developers] |
| **Engineering Lead** | [e.g., System stability, Clean architecture] | [e.g., Technical debt, Outages] | [e.g., Build robust API gateway] | [e.g., MTTR, Deploy rate, Uptime] | [e.g., Budget limits for third-party tools] |
| **Product Operator** | [e.g., Rapid workflow execution] | [e.g., Data entry errors, Slow interfaces] | [e.g., Automate outreach review] | [e.g., Operations completed/day] | [e.g., Zero programming capability] |
| **Finance / CFO** | [e.g., Gross margin, Cost efficiency] | [e.g., Scaling infrastructure costs] | [e.g., Keep cloud cost below $1K/mo] | [e.g., Gross Margin %, Cloud ROI] | [e.g., No capital expenditures pre-seed] |
| **Compliance / Legal** | [e.g., Zero regulation violations] | [e.g., Data breaches, Fines] | [e.g., Ensure GDPR/CCPA coverage] | [e.g., Compliance audit pass rate] | [e.g., Data residency rules] |
| **End User / Client** | [e.g., Speed, Accuracy, Low cost] | [e.g., Spamming their partners, High cost] | [e.g., Get backlinks with high domain rank]| [e.g., Backlink indexing speed] | [e.g., Tech-illiterate interface requirement]|

---

## 3. Influence & Interest Mapping

```
High │ 
     │   [Keep Satisfied]                [Manage Closely]
     │   - Legal / Compliance            - VP of Engineering
I    │   - Finance / CFO                 - Founder / CEO
N    │
F    │───────────────────────────────────────────────────────────
L    │   [Monitor Only]                  [Keep Informed]
U    │   - Hardware Vendors              - Operations Team
E    │   - External Partners             - End Users / Clients
N    │
C    │
E    └───────────────────────────────────────────────────────────
Low                          INTEREST                         High
```

### 3.1 Mapping Registry
*   **High Influence / High Interest (Manage Closely)**:
    1.  [Stakeholder Title] | *Core Alignment Strategy*: [e.g., Weekly roadmap synchronization]
    2.  [Stakeholder Title] | *Core Alignment Strategy*: [Description]
*   **High Influence / Low Interest (Keep Satisfied)**:
    1.  [Stakeholder Title] | *Core Alignment Strategy*: [e.g., Monthly compliance briefs]
*   **Low Influence / High Interest (Keep Informed)**:
    1.  [Stakeholder Title] | *Core Alignment Strategy*: [e.g., Slack dashboard notifications]

---

## 4. Conflict & Trade-off Resolution Matrix

Identify key conflicts of interest between stakeholders and establish clear priorities:

| Conflict Scenario | Stakeholder A | Stakeholder B | Resolution Strategy |
|---|---|---|---|
| **Speed vs. Compliance** | **Founder** (Wants fast release) | **Legal** (Wants GDPR review) | Use V0.2 Research Engine automated checks during pipeline build; legal signs off asynchronously within 48h. |
| **Feature Richness vs. Cost** | **Product Lead** (Wants LLM checks) | **Finance** (Wants low API cost) | Run hybrid ML check: use regex/semantic rules first, invoke LLM only on border cases (ICS < 0.7). |
| **Developer Velocity vs. Control**| **Engineers** (Want direct database access)| **SecOps** (Wants strict IAM control) | Implement zero-trust DB client logs; access via signed temporary tokens only. |

---

## 5. Stakeholder Interview & Validation Logs
Maintain records of direct feedback to avoid making assumptions about stakeholder needs:

*   **Log ID**: STK-[UUID]-01
    *   *Stakeholder*: [Name / Title, e.g., CFO]
    *   *Input Method*: [Interview / Survey / Support Ticket]
    *   *Validated Statement*: "[Insert direct quote or validated requirement here]"
    *   *Impact on Project*: [e.g., Modified success criteria to target gross margin > 85%]
