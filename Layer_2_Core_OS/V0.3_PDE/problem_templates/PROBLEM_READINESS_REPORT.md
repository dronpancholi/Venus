# Template: Problem Readiness Report

## 1. Document Control
*   **Project Name**: [Project Name]
*   **Intake ID**: INT-[UUID]
*   **Readiness ID**: READY-[UUID]
*   **Date Evaluated**: [Date]
*   **Gateway Evaluator**: [Name]

---

## 2. Readiness Scoring Model (The Gateway Score)
*Architecture and engineering must not begin below a Gateway Score of 0.80.*

\[Gateway\_Score = \frac{1}{10} \sum_{i=1}^{10} Score_i\]

Where each indicator is scored on a scale of 0.0 to 1.0 based on the following criteria:

| # | Readiness Indicator | Evaluation Criteria | Current Score (0.0 - 1.0) |
|---|---|---|---|
| 1 | **Root Cause Validation** | Is the root cause isolated and backed by transactional evidence? | [0.0] |
| 2 | **Stakeholder Alignment** | Are executive, engineering, and user conflicts resolved? | [0.0] |
| 3 | **Constraint Definition** | Are all hard technical, regulatory, and cost limits documented? | [0.0] |
| 4 | **Assumption Validation** | Are high-impact assumptions validated (Risk Scores < 3.0)? | [0.0] |
| 5 | **Unknowns Clarified** | Have critical unknowns been resolved via spike tasks? | [0.0] |
| 6 | **Opportunity Analysis** | Is there a clear strategic/automation advantage identified? | [0.0] |
| 7 | **Failure Mitigation** | Have high-priority failure scenarios (RPN >= 50) been mitigated?| [0.0] |
| 8 | **Systems Context** | Is the ecosystem integration and data flow mapped? | [0.0] |
| 9 | **Success Criteria** | Are quantitative KPIs (Technical, Business) established? | [0.0] |
| 10| **AI Suitability** | Is the selection of AI (if any) justified vs. automation? | [0.0] |

*   **Calculated Gateway Score**: [0.00]
*   **Target Threshold**: **0.80**
*   **Evaluation Status**: [**BLOCKED** / **APPROVED FOR ARCHITECTURE**]

---

## 3. Detailed Gap Analysis (If Blocked)
*Identify indicators scoring below 0.8 and detail the required remediation actions.*

*   **Gap 1: [Indicator Name, e.g., Assumption Validation]**
    *   *Why it is failing*: [e.g., ASM-AI-01 has a Risk Score of 5.0 and has not been tested in a sandbox environment.]
    *   *Required Remediation*: [e.g., Run spike script `scripts/verify_parser.py` and log output accuracy.]
    *   *Assigned Owner*: [Name]

*   **Gap 2: [Indicator Name]**
    *   *Why it is failing*: [Description]
    *   *Required Remediation*: [Description]
    *   *Assigned Owner*: [Name]

---

## 4. Gatekeeper Sign-offs
*Document the formal validation approvals. Signatures confirm the accuracy of the underlying registers.*

*   **Technical Director Approval**:
    *   *Signature*: [Name] | *Date*: [Date] | *Comments*: "[Insert Comments]"
*   **Compliance & Risk Approval**:
    *   *Signature*: [Name] | *Date*: [Date] | *Comments*: "[Insert Comments]"
*   **Product Owner Approval**:
    *   *Signature*: [Name] | *Date*: [Date] | *Comments*: "[Insert Comments]"
